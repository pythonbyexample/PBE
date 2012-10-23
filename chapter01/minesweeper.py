#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice, randint
from time import time, sleep

from utils import Loc, joins

size       = 8
num_mines  = randint(4, 8)
ai_run     = 1

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
        self.board = [ [Tile() for _ in range(size)] for _ in range(size) ]
        for _ in range(num_mines):
            self[self.random_empty()].mine = True

        for loc in self:
            self[loc].number = sum( self[nloc].mine for nloc in self.neighbours(loc) )

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __iter__(self):
        """Iterate over board tile locations."""
        return ( Loc(x,y) for x in range(self.size) for y in range(self.size) )

    def hidden_or_falsely_marked(self, tile):
        return bool(tile.hidden or tile.marked and not tile.mine)

    def cleared(self):
        """All mines defused?"""
        return not any( self.hidden_or_falsely_marked(self[loc]) for loc in self )

    def all_hidden(self):
        return [loc for loc in self if self[loc].hidden]

    def random_hidden(self):
        return choice(self.all_hidden())

    def all_empty(self):
        return [loc for loc in self if not self[loc].mine]

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

    def toggle_mark(self, loc):
        """Toggle 'mine' mark on/off."""
        self[loc].toggle_mark()

    def reveal(self, loc):
        tile = self[loc]
        if not tile.number:
            self.reveal_adjacent_empty(loc)
        tile.hidden = False
        return tile

    def reveal_adjacent_empty(self, loc):
        """ Reveal all empty (number=0) tiles adjacent to starting tile `loc` and subsequent unhidden tiles.
            Uses floodfill algorithm.
        """
        tile = self[loc]
        if tile.number != 0:
            tile.hidden = False
        if not tile.hidden:
            return

        tile.hidden = False
        for location in self.neighbours(loc):
            self.reveal_adjacent_empty(location)

    def neighbours(self, loc):
        """Return the list of neighbours of `loc`."""
        x, y = loc
        locs = set((x+n, y+m) for n in (-1,0,1) for m in (-1,0,1)) - set( [(x,y)] )
        return [Loc(*tup) for tup in locs if self.valid(*tup)]

    def valid(self, x, y):
        return bool( x+1 <= self.size and y+1 <= self.size and x >= 0 and y >= 0 )


class Minesweeper(object):
    start = time()

    def check_end(self, tile=None):
        """Check if game is lost (stepped on a mine), or won (all mines found)."""
        if tile and tile.mine:
            self.game_lost()
        elif board.cleared():
            self.game_won()

    def game_lost(self):
        for loc in board.all_hidden():
            board.reveal(loc)
        board.draw()
        print("KABOOM. END.")
        sys.exit()

    def game_won(self):
        elapsed = time() - self.start
        print("All mines cleared (%d:%d)!" % (elapsed/60, elapsed%60))
        sys.exit()


class Test(object):
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
        inp = raw_input("> ")
        if inp == 'q': sys.exit()

        mark = inp.startswith('m')
        x, y = inp[-2], inp[-1]
        loc  = Loc( int(x)-1, int(y)-1 )

        if mark:
            board.toggle_mark(loc)
            msweep.check_end()
        else:
            msweep.check_end(board.reveal(loc))

    def ai_move(self):
        """Very primitive `AI', does not mark mines & does not try to avoid them."""
        loc = board.random_hidden()

        while loc.x:
            print("\n loc", loc.x+1, loc.y+1); print()
            msweep.check_end(board.reveal(loc))
            loc = Loc(loc.x-1, loc.y)   # move location to the left
            board.draw()
            sleep(0.4)


if __name__ == "__main__":
    board = Board(size)
    msweep = Minesweeper()
    Test().test()
