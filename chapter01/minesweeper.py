#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice

size       = 8
num_mines  = 6
blank      = ' '
hiddenchar = '.'
minechar   = '*'


class Tile(object):
    hidden = True
    mine   = False
    number = 0

    def __repr__(self):
        if self.hidden : return hiddenchar
        elif self.mine : return minechar
        else           : return str(self.number or blank)

class Board(object):
    """Minesweeper playing board."""
    def __init__(self, size):
        self.size = size
        self.board = [ [Tile()]*size for _ in range(size) ]
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
        for row in self.board:
            print( ''.join(row) )
        print()

    def all_empty(self):
        return [loc for loc in self if not self[loc].mine]

    def random_empty(self):
        return choice(self.all_empty())

    def reveal_adjacent_empty(self, loc):
        """ Reveal all empty (number=0) tiles adjacent to starting tile and subsequent unhidden tiles.
            Uses floodfill algorithm.
        """
        tile = self[loc]
        if tile.number != 0 or not tile.hidden:
            return
        tile.hidden = False
        for loc in self.neighbours(loc):
            self.flood_fill(loc)


class Loc(object):
    """Tile location on the grid with x, y coordinates."""
    __slots__ = ['x', 'y', 'loc']

    def __init__(self, x, y):
        self.loc = x, y
        self.x, self.y = x, y

    def __str__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)


class Player(object):
    top_score = 0

class Minesweeper(object):

    def __init__(self, size):
        self.size = size

    def run(self):
        self.make_win_lines()
        turn = cycle(players)

        while 1:
            loc = self.best_move(turn)
            board[loc] = turn.next()
            board.draw()
            self.check_winner()
            if not board.blanks(): self.winner(None)


if __name__ == "__main__":
    board = Board(size)
    Minesweeper(size).run()
