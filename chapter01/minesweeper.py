#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice
from time import time, sleep

from utils import Loc

size       = 8
num_mines  = 6
blank      = ' '
hiddenchar = '.'
minechar   = '*'
autorun    = True


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
            self[loc].number = sum(self[loc].mine for loc in self.neighbours())

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __iter__(self):
        """Iterate over board tile locations."""
        return ( Loc(x,y) for x in range(self.size) for y in range(self.size) )

    def draw(self):
        for row in self:
            print( ' '.join(row) ); print()
        print()

    def toggle(self, loc):
        """Toggle 'mine' mark on/off."""
        self[loc].mine = not self[loc].mine

    def reveal(self, loc):
        self[loc].hidden = False
        return self[loc].mine

    def cleared(self):
        """All mines defused?"""
        return not (self[loc].mine and self[loc].hidden for loc in self)

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
        if tile.number != 0 or not tile.hidden:
            return
        tile.hidden = False
        for location in self.neighbours(loc):
            self.flood_fill(location)


class Player(object):
    top_score = 0

class Minesweeper(object):
    start = time()

    def run(self):
        while True:
            board.draw()
            if autorun:
                loc = board.random_hidden()

                while loc.x:
                    exploded = board.reveal(loc)
                    if exploded:
                        self.game_lost()
                    elif board.cleared():
                        self.game_won()
                    loc = Loc(loc.x-1, loc.y)   # move location to the left
                    board.draw()
                    sleep(0.4)
            else:
                inp  = raw_input("> ")
                if inp == 'q': sys.exit()

                mark = inp.startswith('m')
                x, y = inp[-2], inp[-1]
                loc  = Loc(int(x), int(y))

                if mark : board.mark(loc)
                else    : board.reveal(loc)

    def game_lost(self):
        print("KABOOM. END.")
        sys.exit()

    def game_won(self):
        elapsed = time() - self.start
        print("All mines cleared (%d:%d)" % (elapsed/60, elapsed%60))


if __name__ == "__main__":
    board = Board(size)
    Minesweeper(size).run()
