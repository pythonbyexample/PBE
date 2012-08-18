#!/usr/bin/env python

# Imports {{{
# Inspired by Flippy game By Al Sweigart http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, sys, pygame, time
from copy import copy
from pygame.locals import *
from board import Board
from shared import *

FPS            = 10
width          = 640
height         = 480
spacesize      = 50 # width & height of each space on the board, in pixels
dimensions     = 8,8
hint_tile      = "hint_tile"
board_fn       = "flippyboard.png"
bg_fn          = "flippybackground.png"
animationspeed = 25 # integer from 1 to 100, higher is faster animation

xmargin        = int((width - (dimensions[0] * spacesize)) / 2)
ymargin        = int((height - (dimensions[1] * spacesize)) / 2)

cwhite         = (255, 255, 255)
cblack         = (  0,   0,   0)
green          = (  0, 155,   0)
brightblue     = (  0,  50, 255)
brown          = (174,  94,   0)

colours        = Container(bg1=brightblue, bg2=green, grid=cblack, text=cwhite, hint=brown, white=cwhite, black=cblack)
piece_colours  = ["white", "black"]
# }}}

class Container(object):
    def __init__(self, **kwds)  : self.__dict__.update(kwds)
    def __setitem__(self, k, v) : self.__dict__[k] = v
    def __getitem__(self, k)    : return self.__dict__[k]

class Item(object):
    is_piece = is_hint = is_blank = False


class Piece(Item):
    is_piece = True

    def __init__(self, colour):
        self.colour_int = colour
        self.white      = colour==0
        self.black      = colour==1
        self.colour     = piece_colours[colour]
        self.rgb        = colours[colour]

    def draw(self, loc):
        pygame.draw.circle(reversi.display, self.rgb, loc, int(spacesize / 2) - 4)

    def flip(self):
        self.colour_int = 1 - self.colour_int
        self.__init__(self.colour_int)

    def opposite(self):
        return Piece(int(not self.colour_int))

    def __eq__(self, other):
        return bool(self.colour == other.colour)


class Hint(Item):
    is_hint = True

    def draw(self, loc):
        pygame.draw.rect(reversi.display, colours.hint, (loc.x - 4, loc.y - 4, 8, 8))


class Board(object):
    def __init__(self, display):
        self.maxx, self.maxy = dimensions
        self.display = display
        self.blank = [ [[blank] for _ in range(self.maxx)] for _ in range(self.maxy) ]
        self.clear()
        for loc in self: self.put(wall, loc)

    # the following methods are unused in Reversi
    def __getitem__2(self, loc):
        return self.values(loc)[-1]

    def __setitem__2(self, loc, item):
        self.board[loc.y][loc.x].append(thing)

    def values(self, loc):
        if self.valid(loc): return self.board[loc.y][loc.x]

    def is_empty(self):
        return self.board == self.blank

    def valid(self, loc):
        return bool(0 <= loc.x < self.maxx and 0 <= loc.y < self.maxy)

    def empty(self, loc):
        return bool(self.valid(loc) and self[loc] == blank)

    def near_border(self, loc):
        x, y = loc
        if x+1 == self.maxx or y+1 == self.maxy or x == 0 and y == 0:
            return True

    def remove(self, item, loc=None):
        loc = loc or item.loc
        l = self.board[loc.y][loc.x]
        if item in l: l.remove(item)

    def random(self):
        return randint(0, self.maxx-1), randint(0, self.maxy-1)

    def random_empty(self):
        for _ in range(999):
            l = Loc(self.random())
            if self.empty(l): return l

    def new(self):
        board = []
        for i in range(self.maxx):
            board.append([empty] * self.maxy)
        return board

    # end of unused methods


    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def __iter__(self):
        for y in range(self.maxy):
            for x in range(self.maxx):
                yield Loc(x, y)

    def clear(self, loc=None):
        if loc: self.board[loc.y][loc.x] = [blank]
        else:   self.board = deepcopy(self.blank)

    def animate_move(self, pieces_to_flip, piece, piece_loc):
        """ Draw the additional tile that was just laid down. (Otherwise we'd
            have to completely redraw the board & the board info.)
        """
        loc_px = self.tile_center(piece_loc)
        pygame.draw.circle(self.display, piece.rgb, loc_px, int(spacesize / 2) - 4)
        pygame.display.update()

        for rgb_values in range(0, 255, int(animationspeed * 2.55)):
            if rgb_values > 255:
                rgb_values = 255
            elif rgb_values < 0:
                rgb_values = 0

            if piece.white:
                color = tuple([rgb_values] * 3)         # rgb_values goes from 0 to 255
            elif piece.black:
                color = tuple([255 - rgb_values] * 3)   # rgb_values goes from 255 to 0

            for loc in pieces_to_flip:
                pygame.draw.circle(self.display, color, self.tile_center(loc), int(spacesize / 2) - 4)
            pygame.display.update()
            mainclock.tick(FPS)
            reversi.check_for_quit()

    def draw(self, board=None):
        board = board or self.board
        self.display.blit(bgimage, bgimage.get_rect())

        # grid
        for x in range(self.maxx + 1):
            startx = (x * spacesize) + xmargin
            starty = ymargin
            endx   = (x * spacesize) + xmargin
            endy   = ymargin + (self.maxy * spacesize)
            pygame.draw.line(self.display, colours.grid, (startx, starty), (endx, endy))

        for y in range(self.maxy + 1):
            startx = xmargin
            starty = (y * spacesize) + ymargin
            endx   = xmargin + (self.maxx * spacesize)
            endy   = (y * spacesize) + ymargin
            pygame.draw.line(self.display, colours.grid, (startx, starty), (endx, endy))

        # pieces & hints
        for loc in self:
            # tloc = self.tile_center(loc)
            item = board[loc]
            if item != blank: item.draw()

    def get_clicked_tile(self, position):
        """If user clicked a tile, return it."""
        mx, my = position
        for x, y in self:
            if mx > x * spacesize + xmargin and mx < (x + 1) * spacesize + xmargin and \
               my > y * spacesize + ymargin and my < (y + 1) * spacesize + ymargin:
                return Loc(x, y)
        return None

    def reset(self):
        self.clear()
        self[ Loc(3,3) ] = Piece(0)
        self[ Loc(4,4) ] = Piece(0)
        self[ Loc(3,4) ] = Piece(1)
        self[ Loc(4,3) ] = Piece(1)

    def get_line(self, board, loc, dir):
        line = ''
        while 1:
            loc.x += xdir
            loc.y += ydir
            if not is_on_board(loc):
                return line
            item = board[loc]
            if item == blank: line += ' '
            elif item.is_piece: line += item.colour[0]


    def is_valid_move(self, piece, loc, board=None):
        """If it is a valid move, returns a list of spaces of the captured pieces."""
        start_loc   = copy(loc)
        board       = board or self.board
        is_on_board = self.is_on_board
        board[loc]  = piece

        if not is_on_board(loc) or piece != blank:
            return False

        opposite_piece = piece.opposite()
        pieces_to_flip = []

        # check each of the eight directions:
        for dir in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            line = self.get_line(board, loc, dir)
            loc.x += xdir
            loc.y += ydir
            if is_on_board(loc) and board[loc] == opposite_piece:
                # The piece belongs to the other player next to our piece.
                loc.x += xdir
                loc.y += ydir
                if not is_on_board(loc):
                    continue

                while board[loc] == opposite_piece:
                    loc.x += xdir
                    loc.y += ydir
                    if not is_on_board(loc):
                        break
                if not is_on_board(loc):
                    continue

                if board[loc] == piece:
                    # There are pieces to flip over. Go in the reverse directions
                    # until we reach the original space, noting all the pieces along the way.
                    while True:
                        loc.x -= xdir
                        loc.y -= ydir
                        if loc == start_loc:
                            break
                        pieces_to_flip.append(board[loc])

        board[loc] = blank
        return pieces_to_flip or False

    def is_on_board(self, loc):
        return bool( 0 <= loc.x < self.maxx and 0 <= loc.y < self.maxy )

    def board_with_hints(self, piece):
        """Returns a new board with hint markings."""
        dupe_board = copy.deepcopy(self.board)
        for loc in self.get_valid_moves(piece, dupe_board):
            dupe_board[loc] = hint_tile
        return dupe_board

    def get_valid_moves(self, piece, board=None):
        board = board or self.board
        return [loc for loc in self if self.is_valid_move(piece, loc, board)]

    def get_score(self, player_piece, computer_piece, board=None):
        """Determine the score by counting the tiles."""
        board           = board or self.board
        scores          = Container()
        scores.player   = sum(board[loc]==player_piece for loc in self)
        scores.computer = sum(board[loc]==computer_piece for loc in self)
        return scores

    def tile_center(self, loc):
        return xmargin + loc.x * spacesize + int(spacesize / 2), ymargin + loc.y * spacesize + int(spacesize / 2)

    def is_on_corner(loc):
        """Returns True if the position is in one of the four corners."""
        x, y = loc
        return (x == 0 and y == 0) or  (x == self.maxx and y == 0) or \
               (x == 0 and y == self.maxy) or (x == self.maxx and y == self.maxy)


class Reversi(object):
    def main(self):
        global mainclock, FONT, BIGFONT, bgimage

        pygame.init()
        mainclock    = pygame.time.Clock()
        self.display = pygame.display.set_mode((width, height))
        FONT         = pygame.font.Font("freesansbold.ttf", 16)
        BIGFONT      = pygame.font.Font("freesansbold.ttf", 32)
        pygame.display.set_caption("Flippy")

        # Set up the background image.
        board_image              = pygame.image.load(board_fn)
        # Use smoothscale() to stretch the board image to fit the entire board:
        board_image              = pygame.transform.smoothscale(board_image, (board.maxx * spacesize, board.maxy * spacesize))
        board_image_rect         = board_image.get_rect()
        board_image_rect.topleft = (xmargin, ymargin)
        bgimage                  = pygame.image.load(bg_fn)
        bgimage                  = pygame.transform.smoothscale(bgimage, (width, height))
        bgimage.blit(board_image, board_image_rect)

        while True:
            if not reversi.run_game(): break

    def run_game(self):
        board.reset()
        show_hints = False
        turn = random.choice(["computer", "player"])
        board.draw()
        self.player_piece, self.computer_piece = enter_player_piece()

        # "New Game" and "Hints" buttons
        newgame = render_text("New Game", colours.text, colours.bg2, topright=(width-8,10))
        hints   = render_text("Hints", colours.text, colours.bg2, topright=(width-8,40))

        while True:
            if turn == "player":
                if not self.get_valid_moves(self.player_piece):
                    break

                move_to = None
                while not move_to:
                    current_board = board.board_with_hints(self.player_piece) if show_hints else None
                    self.check_for_quit()

                    for event in pygame.event.get():
                        if event.type == MOUSEBUTTONUP:
                            if newgame[1].collidepoint(event.pos):
                                return True
                            elif hints[1].collidepoint(event.pos):
                                show_hints = not show_hints

                            move_to = board.get_clicked_tile(event.pos)
                            if move_to and not board.is_valid_move(self.player_piece, move_to):
                                move_to = None

                    board.draw(current_board)
                    board.draw_info(turn)
                    mainclock.tick(FPS)
                    pygame.display.update()

                self.make_move(self.player_piece, move_to, True)
                if self.get_valid_moves(self.computer_piece):
                    turn = "computer"

            else:
                # Computer's turn:
                if not self.get_valid_moves(self.computer_piece):
                    break

                board.draw()
                board.draw_info(self.player_piece, self.computer_piece, turn)

                # Make it look like the computer is thinking by pausing a bit.
                pause_until = time.time() + random.randint(5, 15) * 0.1
                while time.time() < pause_until:
                    pygame.display.update()

                # Make the move and end the turn.
                loc = self.get_computer_move()
                self.make_move(self.computer_piece, loc, True)
                if self.get_valid_moves(self.player_piece):
                    turn = "player"

        board.draw()
        scores = board.get_score(self.player_piece, self.computer_piece)

        # Determine the text of the message to display.
        pscore, cscore = scores.player, scores.computer
        if pscore > cscore:
            text = "You beat the computer by %s points! Congratulations!" % (pscore-cscore)
        elif pscore < cscore:
            text = "You lost. The computer beat you by %s points." % (cscore-pscore)
        else:
            text = "The game was a tie!"

        render_text(text, colours.text, colours.bg1, center=(int(width / 2), int(height / 2)))
        render_text("Play again?", colours.text, colours.bg1, center=(int(width / 2), int(height / 2) + 50), font=BIGFONT)
        yes = render_text("Yes", colours.text, colours.bg1, center=(int(width / 2) - 60, int(height / 2) + 90), font=BIGFONT)
        no  = render_text("No", colours.text, colours.bg1, center=(int(width / 2) + 60, int(height / 2) + 90), font=BIGFONT)

        while True:
            # Process events until the user clicks on Yes or No.
            self.check_for_quit()
            for event in pygame.event.get(): # event handling loop
                if event.type == MOUSEBUTTONUP:
                    if yes[1].collidepoint(event.pos):
                        return True
                    elif no[1].collidepoint(event.pos):
                        return False
            pygame.display.update()
            mainclock.tick(FPS)

    def draw_info(self, turn):
        """Draws scores and whose turn it is at the bottom of the screen."""
        scores = self.get_score(self.player_piece, self.computer_piece)
        tpl    = "Player Score: %s    Computer Score: %s    %s's Turn"
        msg    = render_text(tpl % (scores.player, scores.computer, turn.title()), colours.bg1, bottomleft=(10, height-5))

    def enter_player_piece(self):
        """Show selection buttons and return [player_piece, ai_tile]."""
        render_text("Do you want to be white or black?", colours.text, colours.bg1, center=(int(width / 2), int(height / 2)))
        white = render_text("White", colours.text, colours.bg1, center=(int(width / 2) - 60, int(height / 2) + 40))
        black = render_text("Black", colours.text, colours.bg1, center=(int(width / 2) + 60, int(height / 2) + 40))

        while True:
            # Keep looping until the player has clicked on a color.
            self.check_for_quit()
            for event in pygame.event.get(): # event handling loop
                if event.type == MOUSEBUTTONUP:
                    if white[1].collidepoint(event.pos):
                        return [white_piece, black_piece]
                    elif black[1].collidepoint(event.pos):
                        return [black_piece, white_piece]
            pygame.display.update()
            mainclock.tick(FPS)

    def make_move(self, piece, loc, None, real_move=False, board=None):
        """ Place the piece on the board at xstart, ystart, and flip tiles
            Returns False if this is an invalid move, True if it is valid.
        """
        board = board or self.board
        pieces_to_flip = board.is_valid_move(piece, loc)
        if pieces_to_flip:
            board[loc] = piece
            if real_move:
                board.animate_move(pieces_to_flip, piece, loc)
            for loc in pieces_to_flip:
                board[loc] = piece
            return True

    def get_computer_move(self):
        """Performace note: adding undo method to board would be faster than deepcopy."""
        possible_moves = board.get_valid_moves(self.computer_piece)
        random.shuffle(possible_moves)

        # always go for a corner if available.
        for loc in possible_moves:
            if board.is_on_corner(loc): return loc

        # Go through all possible moves and remember the best scoring move
        best_score = -1
        for loc in possible_moves:
            dupe_board = copy.deepcopy(board.board)
            self.make_move(self.computer_piece, loc, dupe_board)
            score = board.get_score(self.player_piece, self.computer_piece, dupe_board).computer
            if score > best_score:
                best_move = loc
                best_score = score
        return best_move

    def check_for_quit(self):
        for event in pygame.event.get((QUIT, KEYUP)):
            if event.type==QUIT or key_up(event, K_ESCAPE):
                pygame.quit()
                sys.exit()


def render_text(text, colour, bg=None, topright=None, center=None, bottomleft=None, font=FONT):
    if bg : surf = font.render(text, True, colour, bg)
    else  : surf = font.render(text, True, colour)
    rect = surf.get_rect()
    if topright     : rect.topright = topright
    elif center     : rect.center = center
    elif bottomleft : rect.bottomleft = bottomleft
    reversi.display.blit(surf, rect)
    return surf, rect


def key_up(event, key):
    return event.key==key and event.type==KEYUP


if __name__ == "__main__":
    white_piece = Piece(0)
    black_piece = Piece(1)
    reversi     = Reversi()
    board       = Board(reversi.display)
    reversi.main()
