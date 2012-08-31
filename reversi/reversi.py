#!/usr/bin/env python

# Imports {{{
# Inspired by Flippy game By Al Sweigart http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

from __future__ import division

import random, sys, pygame, time
from time import time
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
centerx        = int(width / 2)
centery        = int(height / 2)
tilesize       = 50     # width & height of each space on the board, in pixels
dimensions     = 8, 8

board_fn       = "flippyboard.png"
bg_fn          = "flippybackground.png"
white_fn       = "white.png"
black_fn       = "black.png"

blank          = ' '
white          = "white"
black          = "black"
animationspeed = 25     # integer from 1 to 100, higher is faster animation
newgame_code   = 0      # return code to start a new game

xmargin        = int((width - (dimensions[0] * tilesize)) / 2)
ymargin        = int((height - (dimensions[1] * tilesize)) / 2)

cwhite         = (255, 255, 255)
cblue          = (  0,  30,  90)
cblack         = (  0,   0,   0)
cgreen         = (  0, 155,   0)
cbrightblue    = (  0,  50, 255)
cbrown         = (174,  94,   0)

logging.basicConfig(filename="out.log", level=logging.DEBUG, format="%(message)s")

class Container(object):
    def __init__(self, **kwds)  : self.__dict__.update(kwds)
    def __setitem__(self, k, v) : self.__dict__[k] = v
    def __getitem__(self, k)    : return self.__dict__[k]

colours = Container(bg1=cbrightblue, bg2=cgreen, grid=cblack, text=cwhite, hint=cbrown, white=cwhite, black=cblack, border=cblue)
# }}}


class Item(object):
    def tile_center(self, loc):
        return xmargin + loc.x * tilesize + int(tilesize / 2), ymargin + loc.y * tilesize + int(tilesize / 2)


class Piece(Item):
    def __init__(self, colour, loc=None):
        self.colour = colour
        self.rgb    = colours[colour]
        self.loc    = loc
        if loc: board[loc] = self

    def __repr__(self):
        return "<%s piece>" % self.colour

    def draw(self, anim_rgb=None):
        # pygame.draw.circle(reversi.display, anim_rgb or self.rgb, self.tile_center(self.loc), int(tilesize / 2) - 4)
        draw_image(reversi, reversi.piece_img[self.colour], center=self.tile_center(self.loc))

    def flip(self):
        self.colour = white if self.colour==black else black
        self.rgb    = colours[self.colour]

    def is_opposite_of(self, other):
        return isinstance(other, self.__class__) and self != other

    def __eq__(self, other):
        return bool(self.colour == getattr(other, "colour", -1))

    def __ne__(self, other):
        return not self.__eq__(other)


class Hint(Item):
    def __init__(self, loc=None):
        self.loc = loc

    def __repr__(self):
        return "<hint>"

    def draw(self):
        x, y = self.tile_center(self.loc)
        pygame.draw.rect(reversi.display, colours.hint, (x-4, y-4, 8, 8))


class Board(object):
    def __init__(self, display):
        self.maxx, self.maxy = dimensions
        self.hints   = False
        self.display = display

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def backup(self):
        """Unused."""
        self.backup_board = deepcopy(self.board)

    def restore(self):
        """Unused."""
        self.board = self.backup_board

    def __iter__(self):
        for y in range(self.maxy):
            for x in range(self.maxx): yield Loc(x, y)

    def reset(self):
        self.board = [ [blank for _ in range(self.maxx)] for _ in range(self.maxy) ]
        Piece(white, Loc(3,3))
        Piece(white, Loc(4,4))
        Piece(black, Loc(3,4))
        Piece(black, Loc(4,3))

    def flip_pieces(self, pieces, n):
        """Flip each one of `pieces`."""
        for _ in range(n):
            for loc in pieces: self[loc].flip()
            for loc in pieces: self[loc].draw()
            pygame.display.update()
            reversi.mainclock_tick()
            reversi.check_for_quit()

    def animate_move(self, captured, piece, piece_loc):
        """Flip pieces back and forth as a simple capture animation."""
        piece.draw()
        self.flip_pieces(captured, 10)
        pygame.display.update()

    def animate_move_rgb(self, captured, piece, piece_loc):
        """UNUSED: rgb animation using regular pygame circles instead of images."""
        piece.draw()
        pygame.display.update()

        for rgb in range(0, 255, int(animationspeed * 2.55)):
            rgb = min(rgb, 255)

            if piece.colour == white:
                rgb = tuple([rgb] * 3)         # rgb goes from 0 to 255
            else:
                rgb = tuple([255 - rgb] * 3)   # rgb goes from 255 to 0

            for loc in captured:
                self[loc].draw(rgb)
            reversi.mainclock_tick()
            reversi.check_for_quit()

    def draw(self):
        self.display.blit(reversi.bgimage, reversi.bgimage.get_rect())

        # grid
        mx, my     = self.maxx, self.maxy
        vertical   = [(x*tilesize + xmargin, ymargin + my*tilesize) for x in range(mx+1)]
        horizontal = [(y*tilesize + ymargin, xmargin + mx*tilesize) for y in range(my+1)]

        for x1, y2 in vertical:
            pygame.draw.line(self.display, colours.grid, (x1, ymargin), (x1, y2))
        for y1, x2 in horizontal:
            pygame.draw.line(self.display, colours.grid, (xmargin, y1), (x2, y1))

        # pieces & hints
        for loc in self:
            if self[loc] != blank:
                self[loc].draw()
        pygame.display.update()

    def get_clicked_tile(self, loc):
        """If user clicked a tile, return it."""
        tileloc = Loc( int(floor( (loc.x-xmargin)/tilesize )), int(floor( (loc.y-ymargin)/tilesize )) )
        if tileloc.valid(): return tileloc

    def add_hints(self, piece):
        if self.hints:
            for loc in self.get_valid_moves(piece):
                Hint(loc)

    def remove_hints(self):
        """ Note: we need to remove hints even when self.hints is True because that setting refers only
            to player's hints; they should always be removed at the end of player's turn.
        """
        for loc in self:
            if isinstance(self[loc], Hint):
                self[loc] = blank

    def toggle_hints(self):
        if self.hints : self.remove_hints()
        else          : self.add_hints()
        self.hints = not self.hints

    def is_valid_move(self, piece, start_loc):
        return bool( self.get_captured(piece, start_loc) )

    def get_captured(self, piece, start_loc):
        """If it is a valid move, returns a list of locations of the captured pieces."""
        if isinstance(self[start_loc], Piece):
            return []
        captured = []

        # check each of the eight directions:
        for dir in [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]:
            templist = []
            loc      = start_loc.move(dir)

            while loc.valid() and piece.is_opposite_of( self[loc] ):
                templist.append(loc)
                loc = loc.move(dir)

            if not loc.valid() or self[loc] != piece:
                continue
            captured.extend(templist)
        return captured

    def get_valid_moves(self, piece):
        return [loc for loc in self if self.is_valid_move(piece, loc)]

    def get_score(self, player, computer):
        """Determine the score by counting the tiles."""
        return sum(self[loc]==player.piece for loc in self), \
               sum(self[loc]==computer.piece for loc in self)

    def is_corner(self, loc):
        """Returns True if the position is in one of the four corners."""
        return loc.x in (0, self.maxx) and loc.y in (0, self.maxy)


class PlayerAI(object):
    """Parent class for live and computer players."""
    def __init__(self, piece):
        self.piece = piece

    def make_move(self, loc):
        print "in make_move()"
        captured = board.get_captured(self.piece, loc)
        print "captured", captured
        piece = Piece(self.piece.colour, loc)
        board.animate_move(captured, piece, loc)
        for loc in captured:
            board[loc].flip()
        board.draw()
        reversi.draw_info(reversi.turn)
        return captured


class Player(PlayerAI):
    newgame = hints = None      # buttons

    def turn(self):
        board.draw()
        board.add_hints(self.piece)
        reversi.check_for_quit()

        # get button click or move click on a tile
        button = reversi.get_button_click(self.newgame, self.hints)
        if button == self.newgame:
            board.reset()
            return newgame_code

        elif button == self.hints:
            board.toggle_hints()

        elif button:
            move_to = board.get_clicked_tile(Loc(button))
            if move_to and board.is_valid_move(self.piece, move_to):
                return move_to

        board.draw()
        reversi.draw_info(reversi.turn)
        self.newgame, self.hints = self.buttons()
        reversi.mainclock_tick()

    def buttons(self):
        """New Game and Hints buttons."""
        return render_text("New Game", colours.text, colours.bg1, topright=(width-8,10), border=4), \
               render_text("Hints", colours.text, colours.bg1, topright=(width-8,40), border=4)


class Computer(PlayerAI):
    def turn(self):
        board.draw()
        reversi.draw_info(reversi.turn)
        possible_moves = board.get_valid_moves(self.piece)

        # Make it look like the computer is thinking by pausing a bit.
        resume = time() + random.randint(5, 15) * 0.1
        while time() < resume: pygame.display.update()

        # always go for a corner if available
        for loc in possible_moves:
            if board.is_corner(loc): return loc

        # go through all possible moves and remember the best scoring move
        score = -1
        for loc in possible_moves:
            captured = board.get_captured(self.piece, loc)
            if len(captured) > score:
                score = len(captured)
                best_move = loc
        print "best_move", best_move
        return best_move


class Reversi(object):
    def __init__(self):
        pygame.init()
        self.mainclock = pygame.time.Clock()
        self.display   = pygame.display.set_mode((width, height))
        self.font      = pygame.font.Font("freesansbold.ttf", 16)
        self.bigfont   = pygame.font.Font("freesansbold.ttf", 32)
        pygame.display.set_caption("Reversi")

        # load images
        board_image    = load_image(board_fn, scale=(dimensions[0] * tilesize, dimensions[1] * tilesize))
        size = tilesize - 4
        self.piece_img = dict(white = load_image(white_fn, scale=(size, size)),
                              black = load_image(black_fn, scale=(size, size)) )

        self.bgimage = pygame.image.load(bg_fn)
        self.bgimage = pygame.transform.smoothscale(self.bgimage, (width, height))
        draw_image(self, board_image, topleft=(xmargin, ymargin))

    def main(self):
        while True:
            if not reversi.run_game(): break

    def run_game(self):
        self.turn = random.choice(["computer", "player"])
        self.turn = "player"
        board.draw()
        ppiece, cpiece  = self.enter_player_piece()
        player          = self.player    = Player(ppiece)
        computer        = self.computer  = Computer(cpiece)
        get_valid_moves = board.get_valid_moves

        while True:
            board.draw()
            if self.turn == "player":
                print "player turn"
                while True:
                    move_to = player.turn()
                    if move_to: break
                board.remove_hints()

                if move_to == newgame_code:
                    return newgame_code
                player.make_move(move_to)

                if   get_valid_moves(computer.piece)   : self.turn = "computer"
                elif not get_valid_moves(player.piece) : break

            elif self.turn == "computer":
                print "computer turn"
                computer.make_move( computer.turn() )

                if   get_valid_moves(player.piece)       : self.turn = "player"
                elif not get_valid_moves(computer.piece) : break

        board.draw()
        self.results_message()
        return self.new_game()

    def new_game(self):
        """Ask if playing a new game or not."""
        render_text("Play again?", colours.text, colours.bg1, center=(centerx, centery + 50), font=self.bigfont)
        yes = render_text("Yes", colours.text, colours.bg1, center=(centerx-60, centery+90), font=self.bigfont, border=4)
        no  = render_text("No", colours.text, colours.bg1, center=(centerx+60, centery+90), font=self.bigfont, border=4)

        while True:
            self.check_for_quit()
            button = self.get_button_click(yes, no)
            if button == yes  : return True
            elif button == no : return False
            self.mainclock_tick()

    def mainclock_tick(self):
        pygame.display.update()
        self.mainclock.tick(FPS)

    def enter_player_piece(self):
        """Show selection buttons and return [player_piece, ai_piece]."""
        render_text("Do you want to be white or black?", colours.text, colours.bg1, center=(centerx, int(height / 2)))
        whitebtn = render_text("White", colours.text, colours.bg1, center=(centerx-60, centery+40), border=4)
        blackbtn = render_text("Black", colours.text, colours.bg1, center=(centerx+60, centery+40), border=4)

        while True:
            self.check_for_quit()
            button = self.get_button_click(whitebtn, blackbtn)
            if   button == whitebtn: return [Piece(white), Piece(black)]
            elif button == blackbtn: return [Piece(black), Piece(white)]
            self.mainclock_tick()

    def get_button_click(self, *buttons):
        """If button is clicked, return it; if click is not over any button, return position; if no clicks, return None."""
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                for button in buttons:
                    if button and button[1].collidepoint(event.pos):
                        return button
                return event.pos

    def draw_info(self, turn):
        """Draws scores and whose turn it is at the bottom of the screen."""
        scores = board.get_score(self.player, self.computer)
        tpl    = "Player Score: %s    Computer Score: %s    %s's Turn"
        render_text(tpl % (scores[0], scores[1], turn.title()), colours.bg1, bottomleft=(10, height-5))

    def results_message(self):
        pscore, cscore = board.get_score(self.player, self.computer)
        if pscore > cscore:
            text = "You beat the computer by %s points! Congratulations!" % (pscore-cscore)
        elif pscore < cscore:
            text = "You lost. The computer beat you by %s points." % (cscore-pscore)
        else:
            text = "The game was a tie!"
        render_text(text, colours.text, colours.bg1, center=(centerx, centery))

    def check_for_quit(self):
        for event in pygame.event.get((QUIT, KEYUP)):
            if event.type==QUIT or (event.key==K_ESCAPE and event.type==KEYUP):
                pygame.quit()
                sys.exit()


def render_text(text, colour, bg=None, topright=None, center=None, bottomleft=None, font=None, border=0):
    font = font or reversi.font
    if bg : surf = font.render(text, True, colour, bg)
    else  : surf = font.render(text, True, colour)
    rect = surf.get_rect()

    if topright     : rect.topright = topright
    elif center     : rect.center = center
    elif bottomleft : rect.bottomleft = bottomleft
    add_border(rect, border)

    reversi.display.blit(surf, rect)
    return surf, rect


def load_image(fn, scale=None):
    image = pygame.image.load(fn)
    if scale:
        image = pygame.transform.smoothscale(image, scale)
    rect = image.get_rect()
    return image, rect

def draw_image(reversi, image, topleft=None, topright=None, center=None, bottomleft=None):
    image, rect = image
    if   topright   : rect.topright = topright
    elif topleft    : rect.topleft = topleft
    elif center     : rect.center = center
    elif bottomleft : rect.bottomleft = bottomleft
    reversi.bgimage.blit(image, rect)


def add_border(rect, border=0):
    """Border around a button."""
    if border:
        x, y = rect.topleft
        width, height = rect.width + border*2, rect.height + border*2
        pygame.draw.rect(reversi.display, colours.border, (x-border, y-border, width, height))

def writeln(*args):
    debug(', '.join([str(a) for a in args]))


if __name__ == "__main__":
    reversi = Reversi()
    board   = Board(reversi.display)
    board.reset()
    reversi.main()
