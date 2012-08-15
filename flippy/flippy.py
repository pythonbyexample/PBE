#!/usr/bin/env python

# Imports {{{
# Flippy (an Othello or Reversi clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# Based on the "reversi.py" code that originally appeared in "Invent
# Your Own Computer Games with Python", chapter 15:
#   http://inventwithpython.com/chapter15.html

import random, sys, pygame, time, copy
from pygame.locals import *
from board import Board
from shared import *

FPS            = 10
width          = 640
height         = 480
spacesize      = 50 # width & height of each space on the board, in pixels
BOARDWIDTH     = 8
BOARDHEIGHT    = 8
white_tile     = "white_tile"
black_tile     = "black_tile"
EMPTY_SPACE    = "EMPTY_SPACE"
hint_tile      = "hint_tile"
animationspeed = 25 # integer from 1 to 100, higher is faster animation

xmargin        = int((width - (BOARDWIDTH * spacesize)) / 2)
ymargin        = int((height - (BOARDHEIGHT * spacesize)) / 2)

cwhite         = (255, 255, 255)
cblack         = (  0,   0,   0)
green          = (  0, 155,   0)
brightblue     = (  0,  50, 255)
brown          = (174,  94,   0)

colours        = Container(bg1=brightblue, bg2=green, grid=cblack, text=cwhite, hint=brown)
# }}}

class Item(object):
    piece = hint = blank = False

class Piece(Item):
    def __init__(self, colour):
        self.colour = ["white", "black"][colour]

    def flip(self):
        self.colour = "white" if self.colour=="black" else "black"


class Board(object):
    def __init__(self, display):
        self.maxx, self.maxy = dimensions
        self.display = display
        self.blank = [ [[' '] for _ in range(self.maxx)] for _ in range(self.maxy) ]
        self.clear()
        for loc in self: self.put(wall, loc)

    def is_empty(self):
        return self.board == self.blank

    def clear(self, loc=None):
        if loc: self.board[loc.y][loc.x] = [' ']
        else:   self.board = deepcopy(self.blank)

    def display(self):
        pass

    def put(self, thing, loc=None):
        if not loc: loc = thing.loc
        self.board[loc.y][loc.x].append(thing)

    def __iter__(self):
        for y in range(self.maxy):
            for x in range(self.maxx):
                yield Loc(x, y)

    def valid(self, loc):
        return bool(0 <= loc.x < self.maxx and 0 <= loc.y < self.maxy)

    def near_border(self, loc):
        x, y = loc
        if x+1 == self.maxx or y+1 == self.maxy or x == 0 and y == 0:
            return True

    def empty(self, loc):
        return bool(self.valid(loc) and self.values(loc) == [' '])

    def remove(self, item, loc=None):
        loc = loc or item.loc
        l = self.board[loc.y][loc.x]
        if item in l: l.remove(item)

    def value(self, loc):
        return self.values(loc)[-1]

    def values(self, loc):
        if self.valid(loc): return self.board[loc.y][loc.x]

    def random(self):
        return randint(0, self.maxx-1), randint(0, self.maxy-1)

    def random_empty(self):
        for _ in range(999):
            l = Loc(self.random())
            if self.empty(l): return l

    def animate_tile_change(self, tiles_to_flip, tile_color, additional_tile):
        # Draw the additional tile that was just laid down. (Otherwise we'd
        # have to completely redraw the board & the board info.)
        additional_tile_color = colours.white if tile_color==white_tile else colours.black
        additional_tile_x, additional_tile_y = tile_center(additional_tile[0], additional_tile[1])
        pygame.draw.circle(self.display, additional_tile_color, (additional_tile_x, additional_tile_y), int(spacesize / 2) - 4)
        pygame.display.update()

        for rgb_values in range(0, 255, int(animationspeed * 2.55)):
            if rgb_values > 255:
                rgb_values = 255
            elif rgb_values < 0:
                rgb_values = 0

            if tile_color == white_tile:
                color = tuple([rgb_values] * 3) # rgb_values goes from 0 to 255
            elif tile_color == black_tile:
                color = tuple([255 - rgb_values] * 3) # rgb_values goes from 255 to 0

            for x, y in tiles_to_flip:
                centerx, centery = tile_center(x, y)
                pygame.draw.circle(self.display, color, (centerx, centery), int(spacesize / 2) - 4)
            pygame.display.update()
            MAINCLOCK.tick(FPS)
            check_for_quit()

    def draw(self, board):
        self.display.blit(BGIMAGE, BGIMAGE.get_rect())

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

        # Draw the black & white tiles or hint spots.
        for x in range(self.maxx):
            for y in range(self.maxy):
                tile = board[x][y]
                tx, ty = tile_center(x, y)
                if tile in (white_tile, black_tile):
                    tile_color = colours.white if tile==white_tile else colours.black
                    pygame.draw.circle(self.display, tile_color, (tx, ty), int(spacesize / 2) - 4)
                if tile == hint_tile:
                    pygame.draw.rect(self.display, colours.hint, (tx - 4, ty - 4, 8, 8))

    def get_clicked_tile(self, position):
        """If user clicked a tile, return it."""
        mx, my = position
        # for x in range(self.maxx):
            # for y in range(self.maxy):
        for x, y in self:
            if mx > x * spacesize + xmargin and mx < (x + 1) * spacesize + xmargin and \
               my > y * spacesize + ymargin and my < (y + 1) * spacesize + ymargin:
                return (x, y)
        return None

    def draw_info(self, board, player_tile, computer_tile, turn):
        """Draws scores and whose turn it is at the bottom of the screen."""
        scores = self.get_score_of_board(board)
        tpl = "Player Score: %s    Computer Score: %s    %s's Turn"
        surf, rect = render_text(tpl % (scores[player_tile], scores[computer_tile], turn.title()), colours.bg1, bottomleft=(10, height-5))
        self.display.blit(surf, rect)

    def reset(self, board):
        # for x in range(self.maxx):
            # for y in range(self.maxy):
        for x, y in self:
            board[x][y] = empty
        self.put(white_tile, Loc(3,3))
        self.put(white_tile, Loc(4,4))
        self.put(black_tile, Loc(3,4))
        self.put(black_tile, Loc(4,3))

    # def new():
    #     board = []
    #     for i in range(self.maxx):
    #         board.append([empty] * self.maxy)
    #     return board

    def is_valid_move(self, tile, xstart, ystart):
        """If it is a valid move, returns a list of spaces of the captured pieces."""
        board = self.board
        if board[xstart][ystart] != empty or not is_on_board(xstart, ystart):
            return False

        board[xstart][ystart] = tile    # temporarily set the tile on the board.
        other_tile = black_tile if tile==white_tile else white_tile

        tiles_to_flip = []
        # check each of the eight directions:
        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection
            y += ydirection
            if is_on_board(x, y) and board[x][y] == other_tile:
                # The piece belongs to the other player next to our piece.
                x += xdirection
                y += ydirection
                if not is_on_board(x, y):
                    continue

                while board[x][y] == other_tile:
                    x += xdirection
                    y += ydirection
                    if not is_on_board(x, y):
                        break
                if not is_on_board(x, y):
                    continue

                if board[x][y] == tile:
                    # There are pieces to flip over. Go in the reverse
                    # direction until we reach the original space, noting all
                    # the tiles along the way.
                    while True:
                        x -= xdirection
                        y -= ydirection
                        if x == xstart and y == ystart:
                            break
                        tiles_to_flip.append([x, y])

        board[xstart][ystart] = empty
        return tiles_to_flip or False

    def is_on_board(self, x, y):
        return bool(0 <= x < self.maxx and 0 <= y < self.maxy)

    def get_board_with_valid_moves(self, board, tile):
        # Returns a new board with hint markings.
        dupe_board = copy.deepcopy(board)

        for x, y in get_valid_moves(dupe_board, tile):
            dupe_board[x][y] = hint_tile
        return dupe_board

    def get_valid_moves(self, board, tile):
        return [(x,y) for x in range(self.maxx) for y in range(self.maxy) if is_valid_move(board, tile, x, y)]

    def get_score_of_board(self, board):
        """Determine the score by counting the tiles."""
        xscore = oscore = 0
        for x in range(self.maxx):
            for y in range(self.maxy):
                if board[x][y] == white_tile:
                    xscore += 1
                if board[x][y] == black_tile:
                    oscore += 1
        return {white_tile:xscore, black_tile:oscore}


class Reversi(object):
    def main(self):
        global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

        pygame.init()
        MAINCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Flippy")
        FONT = pygame.font.Font("freesansbold.ttf", 16)
        BIGFONT = pygame.font.Font("freesansbold.ttf", 32)

        # Set up the background image.
        board_image = pygame.image.load("flippyboard.png")
        # Use smoothscale() to stretch the board image to fit the entire board:
        board_image = pygame.transform.smoothscale(board_image, (BOARDWIDTH * spacesize, BOARDHEIGHT * spacesize))
        board_image_rect = board_image.get_rect()
        board_image_rect.topleft = (xmargin, ymargin)
        BGIMAGE = pygame.image.load("flippybackground.png")
        # Use smoothscale() to stretch the background image to fit the entire window:
        BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (width, height))
        BGIMAGE.blit(board_image, board_image_rect)

        # Run the main game.
        while True:
            if not run_game(): break

def render_text(text, colour, bg=None, topright=None, center=None, bottomleft=None, font=FONT):
    args = [text, True, colour]
    if bg: args.append(bg)
    surf = font.render(*args)
    rect = surf.get_rect()
    if topright     : rect.topright = topright
    elif center     : rect.center = center
    elif bottomleft : rect.bottomleft = bottomleft
    return surf, rect

def run_game():
    board.reset(main_board)
    show_hints = False
    turn = random.choice(["computer", "player"])

    draw_board(main_board)
    player_tile, computer_tile = enter_player_tile()

    # "New Game" and "Hints" buttons
    ngsurf, ngrect = render_text("New Game", colours.text, colours.bg2, topright=(width-8,10))
    hsurf, hrect = render_text("Hints", colours.text, colours.bg2, topright=(width-8,40))

    while True:
        if turn == "player":
            # Player's turn:
            if get_valid_moves(main_board, player_tile) == []:
                break

            movexy = None
            while not movexy:
                # Determine which board data structure to use for display.
                board_to_draw = get_board_with_valid_moves(main_board, player_tile) if show_hints else main_board

                check_for_quit()
                for event in pygame.event.get(): # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        if ngrect.collidepoint(event.pos):
                            return True
                        elif hrect.collidepoint(event.pos):
                            show_hints = not show_hints

                        movexy = get_clicked_tile(event.pos)
                        if movexy and not is_valid_move(main_board, player_tile, movexy[0], movexy[1]):
                            movexy = None

                draw_board(board_to_draw)
                draw_info(board_to_draw, player_tile, computer_tile, turn)
                DISPLAYSURF.blit(ngsurf, ngrect)
                DISPLAYSURF.blit(hsurf, hrect)
                MAINCLOCK.tick(FPS)
                pygame.display.update()

            # Make the move and end the turn.
            make_move(main_board, player_tile, movexy[0], movexy[1], True)
            if get_valid_moves(main_board, computer_tile) != []:
                # Only set for the computer's turn if it can make a move.
                turn = "computer"

        else:
            # Computer's turn:
            if get_valid_moves(main_board, computer_tile) == []:
                # If it was set to be the computer's turn but
                # they can't move, then end the game.
                break

            # Draw the board.
            draw_board(main_board)
            draw_info(main_board, player_tile, computer_tile, turn)

            # Draw the "New Game" and "Hints" buttons.
            DISPLAYSURF.blit(ngsurf, ngrect)
            DISPLAYSURF.blit(hsurf, hrect)

            # Make it look like the computer is thinking by pausing a bit.
            pause_until = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pause_until:
                pygame.display.update()

            # Make the move and end the turn.
            x, y = get_computer_move(main_board, computer_tile)
            make_move(main_board, computer_tile, x, y, True)
            if get_valid_moves(main_board, player_tile):
                turn = "player"

    draw_board(main_board)
    scores = get_score_of_board(main_board)

    # Determine the text of the message to display.
    pscore, cscore = scores[player_tile], scores[computer_tile]
    if pscore > cscore:
        text = "You beat the computer by %s points! Congratulations!" % (pscore-cscore)
    elif pscore < cscore:
        text = "You lost. The computer beat you by %s points." % (cscore-pscore)
    else:
        text = "The game was a tie!"

    msg = render_text(text, colours.text, colours.bg1, center=(int(width / 2), int(height / 2)))
    DISPLAYSURF.blit(*msg)

    msg = render_text("Play again?", colours.text, colours.bg1, center=(int(width / 2), int(height / 2) + 50), font=BIGFONT)
    DISPLAYSURF.blit(*msg)

    # yes/no buttons
    yes = render_text("Yes", colours.text, colours.bg1, center=(int(width / 2) - 60, int(height / 2) + 90), font=BIGFONT)
    DISPLAYSURF.blit(*yes)
    no = render_text("No", colours.text, colours.bg1, center=(int(width / 2) + 60, int(height / 2) + 90), font=BIGFONT)
    DISPLAYSURF.blit(*no)

    while True:
        # Process events until the user clicks on Yes or No.
        check_for_quit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                if yes[1].collidepoint(event.pos):
                    return True
                elif no[1].collidepoint(event.pos):
                    return False
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def tile_center(x, y):
    return xmargin + x * spacesize + int(spacesize / 2), ymargin + y * spacesize + int(spacesize / 2)

def enter_player_tile():
    """Show selection buttons and return [player_tile, ai_tile]."""
    text_surf = FONT.render("Do you want to be white or black?", True, colours.text, colours.bg1)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(width / 2), int(height / 2))

    x_surf = BIGFONT.render("White", True, colours.text, colours.bg1)
    x_rect = x_surf.get_rect()
    x_rect.center = (int(width / 2) - 60, int(height / 2) + 40)

    o_surf = BIGFONT.render("Black", True, colours.text, colours.bg1)
    o_rect = o_surf.get_rect()
    o_rect.center = (int(width / 2) + 60, int(height / 2) + 40)

    DISPLAYSURF.blit(text_surf, text_rect)
    DISPLAYSURF.blit(x_surf, x_rect)
    DISPLAYSURF.blit(o_surf, o_rect)

    while True:
        # Keep looping until the player has clicked on a color.
        check_for_quit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                if x_rect.collidepoint(event.pos):
                    return [white_tile, black_tile]
                elif o_rect.collidepoint(event.pos):
                    return [black_tile, white_tile]
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def make_move(board, tile, xstart, ystart, real_move=False):
    """ Place the tile on the board at xstart, ystart, and flip tiles
        Returns False if this is an invalid move, True if it is valid.
    """
    tiles_to_flip = is_valid_move(board, tile, xstart, ystart)
    if tiles_to_flip:
        board[xstart][ystart] = tile
        if real_move:
            animate_tile_change(tiles_to_flip, tile, (xstart, ystart))

        for x, y in tiles_to_flip:
            board[x][y] = tile
        return True

def is_on_corner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or  (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or (x == BOARDWIDTH and y == BOARDHEIGHT)

def get_computer_move(board, computer_tile):
    """Performace issue: adding undo method to board would be faster than deepcopy."""
    possible_moves = get_valid_moves(board, computer_tile)
    random.shuffle(possible_moves)

    # always go for a corner if available.
    for loc in possible_moves:
        if is_on_corner(*loc): return loc

    # Go through all possible moves and remember the best scoring move
    best_score = -1
    for loc in possible_moves:
        dupe_board = copy.deepcopy(board)
        make_move(dupe_board, computer_tile, *loc)
        score = get_score_of_board(dupe_board)[computer_tile]
        if score > best_score:
            best_move = loc
            best_score = score
    return best_move

def key_up(event, key):
    return event.key==key and event.type==KEYUP

def check_for_quit():
    for event in pygame.event.get((QUIT, KEYUP)):
        if event.type==QUIT or key_up(event, K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    reversi = Reversi()
    board = Board()
    reversi.main()
