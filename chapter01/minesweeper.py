#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice, randint
from time import time, sleep

from utils import Loc, joins

size       = 8
num_mines  = randint(4, 8)
num_mines = 2
ai_run     = 0

space      = ' '
blank      = ' '
hiddenchar = '.'
minechar   = '*'
divider    = '-' * (size * 3 + 5)


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
    def __init__(self, size):
        self.size = size
        self.board = [ [Tile(x,y) for x in range(size)] for y in range(size) ]
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
        return choice(self.all_hidden())

    def all_empty(self):
        return [tile for tile in self if not tile.mine]

    def random_empty(self):
        return choice(self.all_empty())


    def draw(self):
        sp2 = space*2
        print(space*4, sp2.join( [str(n+1) for n in range(self.size)] ))
        print('\n')

        for n, row in enumerate(self.board):
            print(n+1, space, joins(row, space))
            print()
        print(divider)

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
        return bool( x+1 <= self.size and y+1 <= self.size and x >= 0 and y >= 0 )


class Minesweeper(object):
    start    = time()
    win_msg  = "All mines cleared (%d:%d)!"
    lose_msg = "KABOOM. END."

    def check_end(self, tile):
        """Check if game is lost (stepped on a mine), or won (all mines found)."""
        if tile.mine and not tile.marked:
            self.game_lost()
        elif board.cleared():
            self.game_won()

    def game_lost(self):
        for tile in board.all_hidden():
            board.reveal(tile)
        board.draw()
        print(self.lose_msg)
        sys.exit()

    def game_won(self):
        elapsed = time() - self.start
        print(self.win_msg % (elapsed/60, elapsed%60))
        sys.exit()


class Test(object):
    prompt = "> "

    def test(self):
        while True:
            board.draw()

            if ai_run:
                self.ai_move()
            else:
                try:
                    self.manual_move()
                except IndexError, ValueError:
                    pass

    def manual_move(self):
        """Mark mine if """
        inp = raw_input(self.prompt)
        if inp == 'q': sys.exit()

        mark = inp.startswith('m')
        x, y = inp[-2], inp[-1]
        loc  = Loc( int(x)-1, int(y)-1 )
        tile = board[loc]

        tile.toggle_mark() if mark else board.reveal(tile)
        msweep.check_end(tile)

    def ai_move(self):
        """Very primitive `AI', does not mark mines & does not try to avoid them."""
        loc = board.random_hidden().loc

        while loc.x:
            print("\n loc", loc.x+1, loc.y+1); print()
            msweep.check_end( board.reveal(board[loc]) )
            loc = Loc(loc.x-1, loc.y)       # move location to the left
            board.draw()
            sleep(0.4)


if __name__ == "__main__":
    board = Board(size)
    msweep = Minesweeper()
    Test().test()
