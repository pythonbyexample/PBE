#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice
from itertools import cycle

size    = 3
blank   = '.'
players = "xo"

def toggle(player):
    return players[0] if player==players[1] else players[1]

class Board(object):
    """TicTacToe playing board."""

    def __init__(self, size):
        self.size = size
        self.board = [ [blank]*size for _ in range(size) ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def __iter__(self):
        """Iterate over board tile locations."""
        return ( Loc(x,y) for x in range(self.size) for y in range(self.size) )

    def draw(self):
        for row in self.board:
            print( ''.join(row) )
        print()

    def blanks(self):
        return [loc for loc in self if self[loc]==blank]

    def random_blank(self):
        return choice(self.blanks())

    def left_to_completion(self, line, player):
        """Return list of locations left to complete the `line` for player `item`."""
        if any( self[loc]==toggle(player) for loc in line ):
            return []   # empty lists will be ignored
        return [loc for loc in line if self[loc] == blank]

    def completed(self, line, player):
        """Return True if all of locations in `line` list contain `item`."""
        return all( self[loc]==player for loc in line )


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


class TicTacToe(object):

    def __init__(self, size):
        self.size = size

    def make_win_lines(self):
        size  = self.size
        lines = list()

        for n in range(size):
            lines.append( [Loc(m, n) for m in range(size)] )
            lines.append( [Loc(n, m) for m in range(size)] )

        lines.append( [Loc(n, n) for n in range(size)] )
        lines.append( [Loc(size-n-1, n) for n in range(size)] )
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

    def best_move(self, player):
        """Return best move for `player`."""
        good = [ board.left_to_completion(line, player) for line in self.win_lines ]
        good = sorted( [left for left in good if left], key=len )
        return good[0][0] if good else None

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
    TicTacToe(size).run()
