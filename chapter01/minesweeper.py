#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice
from time import time, sleep

from utils import Loc

size       = 8
num_mines  = 6
space      = ' '
blank      = ' '
hiddenchar = '.'
minechar   = '*'
divider    = '-' * (size * 3 + 5)
autorun    = True
autorun    = False


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

    def draw(self):
        print(space*4, "  ".join( [str(n+1) for n in range(self.size)] ))
        print()

        for n, row in enumerate(self.board):
            print( n+1, space, space.join([str(tile) for tile in row]) )
            print()
        print(divider)

    def toggle(self, loc):
        """Toggle 'mine' mark on/off."""
        tile = self[loc].marked
        tile.marked = not tile.marked
        tile.hidden = not tile.hidden

    def reveal(self, loc):
        tile = self[loc]
        if not tile.number:
            self.reveal_adjacent_empty(loc)
        tile.hidden = False
        return tile.mine

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
        lst = [
               # clockwise from upper left
               (x-1 , y-1),
               (x   , y-1),
               (x+1 , y-1),
               (x+1 , y),
               (x+1 , y+1),
               (x   , y+1),
               (x-1 , y+1),
               (x-1 , y),
               ]
        return [Loc(*tup) for tup in lst if self.valid(*tup)]

    def valid(self, x, y):
        return bool( x+1 <= self.size and y+1 <= self.size and x >= 0 and y >= 0 )


class Minesweeper(object):
    start = time()

    def run(self):
        while True:
            board.draw()
            self.ai_move() if autorun else self.manual_move()

    def ai_move(self):
        loc = board.random_hidden()

        while loc.x:
            self.check_end(board.reveal(loc))
            loc = Loc(loc.x-1, loc.y)   # move location to the left
            board.draw()
            sleep(0.4)

    def manual_move(self):
        inp  = raw_input("> ")
        if inp == 'q': sys.exit()

        mark = inp.startswith('m')
        x, y = inp[-2], inp[-1]
        loc  = Loc( int(x)-1, int(y)-1 )

        if mark:
            board.toggle(loc)
        else:
            self.check_end(board.reveal(loc))

    def check_end(self, exploded):
        if exploded:
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


if __name__ == "__main__":
    board = Board(size)
    Minesweeper().run()
