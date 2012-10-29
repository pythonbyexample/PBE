#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from random import randint
from time import time

from utils import Loc, ujoin

space      = ' '
blank      = ' '
hiddenchar = '.'
minechar   = '*'
nl         = '\n'


class Tile(object):
    hidden = True
    mine   = False
    marked = False
    number = 0

    def __init__(self, x, y):
        self.loc = Loc(x,y)

    def __repr__(self):
        if self.marked   : s = minechar
        elif self.hidden : s = hiddenchar
        elif self.mine   : s = minechar
        else             : s = str(self.number or blank)
        return "%2s" % s

    def toggle_mark(self):
        """Toggle 'mine' mark on/off."""
        self.marked = not self.marked
        self.hidden = not self.hidden


class Board(object):
    """Minesweeper playing board."""
    def __init__(self, size, num_mines):
        self.size    = size
        self.divider = '-' * (size * 3 + 5)
        self.board   = [ [Tile(x,y) for x in range(size)] for y in range(size) ]

        for _ in range(num_mines):
            self.random_empty().mine = True

        for tile in self:
            tile.number = sum( ntile.mine for ntile in self.neighbours(tile) )

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __iter__(self):
        """Iterate over board tile locations."""
        return ( self[Loc(x,y)] for x in range(self.size) for y in range(self.size) )

    def marked_or_revealed(self, tile):
        return bool(not tile.hidden or tile.mine and tile.marked)

    def cleared(self):
        """All mines defused?"""
        return all( self.marked_or_revealed(tile) for tile in self )

    def all_hidden(self):
        return [tile for tile in self if tile.hidden]

    def random_hidden(self):
        return rndchoice(self.all_hidden())

    def all_empty(self):
        return [tile for tile in self if not tile.mine]

    def random_empty(self):
        return rndchoice(self.all_empty())


    def draw(self):
        print(space*4, ujoin( [n+1 for n in range(self.size)], space*2 ), nl)

        for n, row in enumerate(self.board):
            print(n+1, space, ujoin(row, space), nl)
        print(self.divider)

    def reveal(self, tile):
        if not tile.number:
            self.reveal_empty_neighbours(tile)
        tile.hidden = False
        return tile

    def reveal_empty_neighbours(self, tile):
        """ Reveal all empty (number=0) tiles adjacent to starting tile `loc` and subsequent unhidden tiles.
            Uses floodfill algorithm.
        """
        if tile.number != 0:
            tile.hidden = False
        if not tile.hidden:
            return

        tile.hidden = False
        for ntile in self.neighbours(tile):
            self.reveal_empty_neighbours(ntile)

    def neighbours(self, tile):
        """Return the list of neighbours of `loc`."""
        x, y = tile.loc
        coords = (-1,0,1)
        locs = set((x+n, y+m) for n in coords for m in coords) - set( [(x,y)] )
        return [ self[ Loc(*tup) ] for tup in locs if self.valid(*tup) ]

    def valid(self, x, y):
        return bool( x <= self.size-1 and y <= self.size-1 and x >= 0 and y >= 0 )


class Minesweeper(object):
    start    = time()
    win_msg  = "All mines cleared (%d:%d)!"
    lose_msg = "KABOOM. END."

    def __init__(self, board):
        self.board = board

    def check_end(self, tile):
        """Check if game is lost (stepped on a mine), or won (all mines found)."""
        if tile.mine and not tile.marked:
            self.game_lost()
        elif self.board.cleared():
            self.game_won()

    def game_lost(self):
        board = self.board
        for tile in board.all_hidden():
            board.reveal(tile)

        board.draw()
        print(self.lose_msg)
        sys.exit()

    def game_won(self):
        elapsed = time() - self.start
        print(self.win_msg % (elapsed/60, elapsed%60))
        sys.exit()
