#!/usr/bin/env python

# Imports {{{
# Inspired by Flippy game By Al Sweigart http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, sys, pygame, time
from copy import copy, deepcopy
from math import floor
import logging
from logging import info, debug

from pygame.locals import *
# from board import Board
from board import Loc
from shared import *

FPS            = 10
width          = 640
height         = 480
tilesize       = 50     # width & height of each space on the board, in pixels
dimensions     = 8,8
board_fn       = "flippyboard.png"
bg_fn          = "flippybackground.png"
animationspeed = 25     # integer from 1 to 100, higher is faster animation
blank          = ' '

xmargin        = int((width - (dimensions[0] * tilesize)) / 2)
ymargin        = int((height - (dimensions[1] * tilesize)) / 2)

white          = (255, 255, 255)
black          = (  0,   0,   0)
green          = (  0, 155,   0)
brightblue     = (  0,  50, 255)
brown          = (174,  94,   0)

colours        = Container(bg1=brightblue, bg2=green, grid=black, text=white, hint=brown, white=white, black=black)
logging.basicConfig(filename="out.log", level=logging.DEBUG, format="%(message)s")
# }}}

def writeln(*args):
    debug(', '.join([str(a) for a in args]))

class Container(object):
    def __init__(self, **kwds)  : self.__dict__.update(kwds)
    def __setitem__(self, k, v) : self.__dict__[k] = v
    def __getitem__(self, k)    : return self.__dict__[k]


class Item(object):
    def tile_center(self, loc):
        return xmargin + loc.x * tilesize + int(tilesize / 2), ymargin + loc.y * tilesize + int(tilesize / 2)


class Piece(Item):
    colours  = ["white", "black"]

    def __init__(self, code):
        self.code   = code
        self.white  = code==0
        self.black  = code==1
        self.colour = self.colours[code]
        self.rgb    = colours[self.colour]

    def __repr__(self):
        return "<%s piece>" % self.colour

    def draw(self, loc, colour=None):
        pygame.draw.circle(reversi.display, colour or self.rgb, self.tile_center(loc), int(tilesize / 2) - 4)

    def flip(self):
        self.code = 1 - self.code
        self.__init__(self.code)

    def opposite(self):
        return Piece(int(not self.code))

    def __eq__(self, other):
        return bool(self.colour == getattr(other, "colour", -1))

    def __ne__(self, other):
        return not self.__eq__(other)


class Hint(Item):
    def __repr__(self):
        return "<hint>"

    def draw(self, loc):
        x, y = self.tile_center(loc)
        pygame.draw.rect(reversi.display, colours.hint, (x-4, y-4, 8, 8))


class Board(object):
    def __init__(self, display):
        self.maxx, self.maxy = dimensions
        self.hints   = False
        self.display = display
        self.blank   = [ [blank for _ in range(self.maxx)] for _ in range(self.maxy) ]
        self.reset()

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def backup(self):
        self.backup_board = deepcopy(self.board)

    def restore(self):
        self.board = self.backup_board

    def __iter__(self):
        for y in range(self.maxy):
            for x in range(self.maxx):
                yield Loc(x, y)

    def clear(self, loc=None):
        if loc: self.board[loc.y][loc.x] = blank
        else:   self.board = deepcopy(self.blank)

    def animate_move(self, pieces_to_flip, piece, piece_loc):
        """ Draw the additional tile that was just laid down. (Otherwise we'd
            have to completely redraw the board & the board info.)
        """
        piece.draw(piece_loc)
        pygame.display.update()

        for rgb in range(0, 255, int(animationspeed * 2.55)):
            if rgb > 255 : rgb = 255
            elif rgb < 0 : rgb = 0

            if piece.white:
                colour = tuple([rgb] * 3)         # rgb goes from 0 to 255
            elif piece.black:
                colour = tuple([255 - rgb] * 3)   # rgb goes from 255 to 0

            for loc in pieces_to_flip:
                self[loc].draw(loc, colour)
            pygame.display.update()
            reversi.mainclock.tick(FPS)
            reversi.check_for_quit()

    def draw(self):
        self.display.blit(reversi.bgimage, reversi.bgimage.get_rect())

        # grid
        for x in range(self.maxx + 1):
            startx = (x * tilesize) + xmargin
            starty = ymargin
            endx   = (x * tilesize) + xmargin
            endy   = ymargin + (self.maxy * tilesize)
            pygame.draw.line(self.display, colours.grid, (startx, starty), (endx, endy))

        for y in range(self.maxy + 1):
            startx = xmargin
            starty = (y * tilesize) + ymargin
            endx   = xmargin + (self.maxx * tilesize)
            endy   = (y * tilesize) + ymargin
            pygame.draw.line(self.display, colours.grid, (startx, starty), (endx, endy))

        # pieces & hints
        for loc in self:
            if self[loc] != blank:
                self[loc].draw(loc)

    def get_clicked_tile(self, loc):
        """If user clicked a tile, return it."""
        loc   = copy(loc)
        loc.x = int(floor( (loc.x-xmargin)/float(tilesize) ))
        loc.y = int(floor( (loc.y-ymargin)/float(tilesize) ))
        if loc.valid(): return loc

    def reset(self):
        self.clear()
        self[ Loc(3,3) ] = Piece(0)
        self[ Loc(4,4) ] = Piece(0)
        self[ Loc(3,4) ] = Piece(1)
        self[ Loc(4,3) ] = Piece(1)

    def add_hints(self, piece):
        for loc in self.get_valid_moves(piece):
            self[loc] = Hint()

    def remove_hints(self, piece):
        for loc in self.get_valid_moves(piece):
            if isinstance(self[loc], Hint):
                self[loc] = blank

    def is_valid_move(self, piece, start_loc, dbg=0):
        """If it is a valid move, returns a list of spaces of the captured pieces."""
        loc = copy(start_loc)
        if not loc.valid() or self[loc] != blank:
            return False

        opposite_piece = piece.opposite()
        ok=dbg
        # ok = loc.loc==(5,3)
        # if ok: writeln("opposite_piece", opposite_piece)
        pieces_to_flip = []

        # check each of the eight directions:
        for dir in [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]:
            ok2 = 0
            fliplst = []
            # if ok2: writeln("dir", dir)
            # if ok2 and dir == [-1,0]: writeln("dir", dir)

            loc.move(dir)
            # if 0:
                # if is_on_board(loc): print "is opp:", self[loc] == opposite_piece

            while loc.valid() and self[loc] == opposite_piece:
                fliplst.append(copy(loc))
                ok2 = ok and fliplst
                loc.move(dir)

            if ok2:
                # print "self[loc]", self[loc]
                # print "self[loc]!=piece", self[loc]!=piece
                # print "self[loc]==piece", self[loc]==piece
                if fliplst: writeln("fliplst", fliplst)
            if not loc.valid() or self[loc] != piece:
                if ok2: writeln("Resetting fliplst")
                fliplst = []
            if ok2: writeln("\n")
            if ok2 and fliplst: writeln("fliplst", fliplst)
            pieces_to_flip.extend(fliplst)
            loc = copy(start_loc)

        if ok2 and pieces_to_flip: writeln("pieces_to_flip", pieces_to_flip)
        return pieces_to_flip or False

    def get_valid_moves(self, piece, dbg=0):
        return [loc for loc in self if self.is_valid_move(piece, loc, dbg=dbg)]

    def get_score(self, player_piece, computer_piece):
        """Determine the score by counting the tiles."""
        return Container(
            player   = sum(self[loc]==player_piece for loc in self),
            computer = sum(self[loc]==computer_piece for loc in self) )

    def is_corner(self, loc):
        """Returns True if the position is in one of the four corners."""
        x, y = loc
        return (x == 0 and y == 0) or  (x == self.maxx and y == 0) or \
               (x == 0 and y == self.maxy) or (x == self.maxx and y == self.maxy)


class Reversi(object):
    def __init__(self):
        pygame.init()
        self.mainclock = pygame.time.Clock()
        self.display   = pygame.display.set_mode((width, height))
        self.font      = pygame.font.Font("freesansbold.ttf", 16)
        self.bigfont   = pygame.font.Font("freesansbold.ttf", 32)
        pygame.display.set_caption("Reversi")

        # Set up the background image.
        board_image              = pygame.image.load(board_fn)
        # Use smoothscale() to stretch the board image to fit the entire board
        board_image              = pygame.transform.smoothscale(board_image, (dimensions[0] * tilesize, dimensions[1] * tilesize))
        board_image_rect         = board_image.get_rect()
        board_image_rect.topleft = (xmargin, ymargin)
        self.bgimage             = pygame.image.load(bg_fn)
        self.bgimage             = pygame.transform.smoothscale(self.bgimage, (width, height))
        self.bgimage.blit(board_image, board_image_rect)

    def main(self):
        while True:
            if not reversi.run_game(): break

    def run_game(self):
        turn = random.choice(["computer", "player"])
        turn = "player"
        board.draw()
        self.player_piece, self.computer_piece = self.enter_player_piece()

        # "New Game" and "Hints" buttons
        newgame = render_text("New Game", colours.text, colours.bg1, topright=(width-8,10))
        hints   = render_text("Hints", colours.text, colours.bg1, topright=(width-8,40))

        while True:
            if turn == "player":
                if board.hints:
                    board.add_hints(self.player_piece)
                if not board.get_valid_moves(self.player_piece):
                    break

                move_to = None
                while not move_to:
                    self.check_for_quit()

                    for event in pygame.event.get():
                        if event.type == MOUSEBUTTONUP:
                            if newgame[1].collidepoint(event.pos):
                                return True
                            elif hints[1].collidepoint(event.pos):
                                board.hints = not board.hints

                            move_to = board.get_clicked_tile(Loc(event.pos))
                            if move_to and not board.is_valid_move(self.player_piece, move_to):
                                move_to = None

                    board.draw()
                    self.draw_info(turn)
                    reversi.display.blit(*newgame)
                    reversi.display.blit(*hints)
                    self.mainclock.tick(FPS)
                    pygame.display.update()

                self.make_move(self.player_piece, move_to, True)
                if board.get_valid_moves(self.computer_piece):
                    turn = "computer"
                board.remove_hints(self.player_piece)

            else:
                # Computer's turn:
                if not board.get_valid_moves(self.computer_piece):
                    break

                board.draw()
                self.draw_info(turn)

                # Make it look like the computer is thinking by pausing a bit.
                pause_until = time.time() + random.randint(5, 15) * 0.1
                while time.time() < pause_until:
                    pygame.display.update()

                # Make the move and end the turn.
                loc = self.get_computer_move()
                self.make_move(self.computer_piece, loc, True)

                if board.get_valid_moves(self.player_piece, dbg=1):
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
        render_text("Play again?", colours.text, colours.bg1, center=(int(width / 2), int(height / 2) + 50), font=self.bigfont)
        yes = render_text("Yes", colours.text, colours.bg1, center=(int(width / 2) - 60, int(height / 2) + 90), font=self.bigfont)
        no  = render_text("No", colours.text, colours.bg1, center=(int(width / 2) + 60, int(height / 2) + 90), font=self.bigfont)

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
            self.mainclock.tick(FPS)

    def draw_info(self, turn):
        """Draws scores and whose turn it is at the bottom of the screen."""
        scores = board.get_score(self.player_piece, self.computer_piece)
        tpl    = "Player Score: %s    Computer Score: %s    %s's Turn"
        msg    = render_text(tpl % (scores.player, scores.computer, turn.title()), colours.bg1, bottomleft=(10, height-5))

    def enter_player_piece(self):
        """Show selection buttons and return [player_piece, ai_tile]."""
        render_text("Do you want to be white or black?", colours.text, colours.bg1, center=(int(width / 2), int(height / 2)))
        white = render_text("White", colours.text, colours.bg1, center=(int(width / 2) - 60, int(height / 2) + 40))
        black = render_text("Black", colours.text, colours.bg1, center=(int(width / 2) + 60, int(height / 2) + 40))

        while True:
            self.check_for_quit()
            button = self.get_button_click(white, black)
            if   button == white: return [white_piece, black_piece]
            elif button == black: return [black_piece, white_piece]
            pygame.display.update()
            self.mainclock.tick(FPS)

    def make_move(self, piece, loc, real_move=False):
        """ Place the piece on the board at xstart, ystart, and flip tiles
            Returns False if this is an invalid move, True if it is valid.
        """
        dbg = piece==white_piece
        pieces_to_flip = board.is_valid_move(piece, loc, dbg=0)
        if pieces_to_flip:
            board[loc] = copy(piece)
            if real_move:
                board.animate_move(pieces_to_flip, piece, loc)
            for loc in pieces_to_flip:
                board[loc].flip()
            return True

    def get_computer_move(self):
        """Performace note: adding undo method to board would be faster than deepcopy."""
        possible_moves = board.get_valid_moves(self.computer_piece)
        random.shuffle(possible_moves)

        # always go for a corner if available.
        for loc in possible_moves:
            if board.is_corner(loc): return loc

        # Go through all possible moves and remember the best scoring move
        best_score = -1
        for loc in possible_moves:
            dupe_board = deepcopy(board.board)
            board.backup()
            self.make_move(self.computer_piece, loc, False)
            score = board.get_score(self.player_piece, self.computer_piece).computer
            if score > best_score:
                best_move = loc
                best_score = score
            board.restore()
        return best_move

    def check_for_quit(self):
        for event in pygame.event.get((QUIT, KEYUP)):
            if event.type==QUIT or (event.key==K_ESCAPE and event.type==KEYUP):
                pygame.quit()
                sys.exit()

    def get_button_click(self, *buttons):
        """If button is clicked, return it; if click is not over any button, return position; if no clicks, return None."""
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                for button in buttons:
                    if button[1].collidepoint(event.pos):
                        return button
                return event.pos


def render_text(text, colour, bg=None, topright=None, center=None, bottomleft=None, font=None):
    font = font or reversi.font
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
