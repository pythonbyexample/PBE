#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice
from itertools import cycle

dimensions = 3, 3
blank      = '.'
players    = "xo"


class Board(object):
    def __init__(self):
        self.maxx, self.maxy = dimensions
        self.board = [ [blank]*self.maxx for _ in range(self.maxy) ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def __iter__(self):
        """Iterate over board tiles."""
        return ( Loc(x,y) for x in range(self.maxx) for y in range(self.maxy) )

    def draw(self):
        for row in self.board:
            print( ''.join(row) )
        print()

    def get_valid_moves(self, piece):
        return [ loc for loc in self if self.is_valid_move(piece, loc) ]

    def filled(self):
        return not any( self[loc]==blank for loc in self )

    def random_blank(self):
        return choice( [loc for loc in self if self[loc]==blank] )

    def completed(self, line, item):
        return all( self[loc]==item for loc in line )


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


class Tictactoe(object):
    def make_win_lines(self):
        lines, diag1, diag2 = [], [], []

        for n in range(3):
            lines.append( [Loc(m, n) for m in range(3)] )
            lines.append( [Loc(n, m) for m in range(3)] )
            diag1.append(Loc(n, n))
            diag2.append(Loc(2-n, n))

        lines.extend((diag1, diag2))
        self.win_lines = lines

    def winner(self, player):
        if player : print("%s is the winner!" % player)
        else      : print("It's a draw!")
        sys.exit()

    def check_winner(self):
        for player in players:
            for line in self.win_lines:
                if board.completed(line, player):
                    self.winner(player)

    def run(self):
        self.make_win_lines()
        turns = cycle(players)

        while 1:
            loc = board.random_blank()
            board[loc] = turns.next()
            board.draw()
            self.check_winner()
            if board.filled(): self.winner(None)


if __name__ == "__main__":
    board = Board()
    Tictactoe().run()
