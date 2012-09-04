#!/usr/bin/env python

# Imports {{{
import sys
from copy import deepcopy
from math import floor

import pygame

from settings import *
# }}}


def draw_image(image, topleft=None, topright=None, center=None, bottomleft=None):
    image, rect = image
    if   topright   : rect.topright = topright
    elif topleft    : rect.topleft = topleft
    elif center     : rect.center = center
    elif bottomleft : rect.bottomleft = bottomleft
    reversi.bgimage.blit(image, rect)

def render_text(text, colour, bg=None, topright=None, center=None, bottomleft=None, font=None, border=0):
    font = font or reversi.font
    if bg : surf = font.render(text, True, colour, bg)
    else  : surf = font.render(text, True, colour)
    rect = surf.get_rect()

    if topright     : rect.topright = topright
    elif center     : rect.center = center
    elif bottomleft : rect.bottomleft = bottomleft
    add_border(display, rect, border)

    reversi.display.blit(surf, rect)
    return surf, rect

def add_border(rect, border=0):
    """Border around a button."""
    if border:
        x, y = rect.topleft
        width, height = rect.width + border*2, rect.height + border*2
        pygame.draw.rect(reversi.display, colours.border, (x-border, y-border, width, height))

def unwrap(x, y=None):
    return x if y==None else (x,y)

def writeln(*args):
    debug(', '.join([str(a) for a in args]))



class Item(object):
    def __init__(self, board, loc=None):
        self.loc = loc
        if loc: board[loc] = self

    def tile_center(self, loc):
        return xmargin + loc.x * tilesize + int(tilesize / 2), ymargin + loc.y * tilesize + int(tilesize / 2)


class Piece(Item):
    def __init__(self, colour=None, board=None, loc=None):
        super(Piece, self).__init__(board, loc)
        self.colour = colour

    def __repr__(self):
        return "<%s piece>" % self.colour

    def draw(self):
        """Draw tile first because of 'haloing' when white piece is drawn over black."""
        draw_image(reversi.tileimg, center=self.tile_center(self.loc))
        draw_image(reversi.piece_img[self.colour], center=self.tile_center(self.loc))

    def flip(self):
        self.colour = white if self.colour==black else black

    def is_opposite_of(self, other):
        return isinstance(other, self.__class__) and self != other

    def __eq__(self, other):
        return bool(self.colour == getattr(other, "colour", -1))

    def __ne__(self, other):
        return not self.__eq__(other)


class Hint(Item):
    def __repr__(self):
        return "<hint>"

    def draw(self):
        x, y = self.tile_center(self.loc)
        pygame.draw.rect(reversi.display, colours.hint, (x-4, y-4, 8, 8))

class Blank(Item):
    def __repr__(self):
        return "<blank>"

    def draw(self):
        draw_image(reversi.tileimg, center=self.tile_center(self.loc))


class Board(object):
    def __init__(self):
        self.maxx, self.maxy = dimensions
        self.hints   = False

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def __iter__(self):
        for y in range(self.maxy):
            for x in range(self.maxx): yield Loc(x, y)

    def reset(self):
        self.board = [ [None for _ in range(self.maxx)] for _ in range(self.maxy) ]
        for loc in self: Blank(self, loc)

        Piece(white, self, Loc(3,3))
        Piece(white, self, Loc(4,4))
        Piece(black, self, Loc(3,4))
        Piece(black, self, Loc(4,3))

    def flip_pieces(self, pieces, n):
        """ Flip each one of `pieces` as a simple animation; `n` needs to be an even number so that we
            end up with pieces on the same side; they're flipped at a later time.
        """
        assert(n%2 == 0)
        for _ in range(n):
            for loc in pieces: self[loc].flip()
            for loc in pieces: self[loc].draw()
            reversi.mainclock_tick()
            reversi.check_for_quit()
            pygame.time.wait(50)

    def animate_move(self, captured, piece):
        """Flip pieces back and forth as a simple capture animation."""
        pygame.display.update()
        piece.draw()
        self.flip_pieces(captured, 4)

    def draw(self):
        reversi.display.blit(reversi.bgimage, bgimage.get_rect())
        for loc in self: self[loc].draw()
        pygame.display.update()

    def get_clicked_tile(self, loc):
        """If user clicked a tile, return it."""
        tileloc = Loc( int(floor( (loc.x-xmargin)/tilesize )), int(floor( (loc.y-ymargin)/tilesize )) )
        if tileloc.valid(): return tileloc

    def add_hints(self, piece):
        if self.hints:
            for loc in self.get_valid_moves(piece):
                h = Hint(self, loc)
                h.draw()

    def remove_hints(self):
        """ Note: we need to remove hints even when self.hints is True because that setting refers only
            to player's hints; they should always be removed at the end of player's turn.
        """
        for loc in self:
            if isinstance(self[loc], Hint):
                Blank(self, loc)

    def toggle_hints(self, piece):
        self.hints = not self.hints
        if self.hints : self.add_hints(piece)
        else          : self.remove_hints()

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

    def buttons(self):
        """New Game and Hints buttons."""
        return render_text("New Game", colours.text, colours.bg1, topright=(width-8,10), border=4), \
               render_text("Hints", colours.text, colours.bg1, topright=(width-8,40), border=4)

    def get_score(self, player, computer):
        """Determine the score by counting the tiles."""
        return sum(self[loc]==player.piece for loc in self), \
               sum(self[loc]==computer.piece for loc in self)

    def is_corner(self, loc):
        """Returns True if the position is in one of the four corners."""
        return loc.x in (0, self.maxx) and loc.y in (0, self.maxy)


class Loc(object):
    def __init__(self, x, y=None):
        x, y = unwrap(x, y)
        self.loc = x, y
        self.x, self.y = x, y

    def __str__(self):
        return str(self.loc)

    def __repr__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)

    def move(self, dir):
        return self.__class__(self.x + dir[0], self.y + dir[1])

    def valid(self):
        return bool( 0 <= self.x < dimensions[0] and 0 <= self.y < dimensions[1] )
