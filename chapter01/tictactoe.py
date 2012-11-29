#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from itertools import cycle

from board import Loc, Board

size       = 3
blank      = '.'
players    = 'xo'


class TictactoeBoard(Board):
    def filled(self):
        return not any(tile==blank for tile in self)

    def random_blank(self):
        return rndchoice( [loc for loc in self.locations() if self[loc]==blank] )

    def completed(self, line, item):
        return all( self[loc]==item for loc in line )


class Tictactoe(object):
    winmsg  = "\n %s is the winner!"
    drawmsg = "\n It's a draw!"

    def make_win_lines(self):
        """ Create a list of winning lines -- when a player fills any one of them, he wins.
            Each line is a list of locations.
        """
        lines, diag1, diag2 = [], [], []

        for n in range(3):
            lines.append( [Loc(m, n) for m in range(3)] )
            lines.append( [Loc(n, m) for m in range(3)] )

            diag1.append(Loc(n, n))
            diag2.append(Loc(2-n, n))

        return lines + [diag1, diag2]

    def game_won(self, player):
        print(self.winmsg % player if player else self.drawmsg)
        sys.exit()

    def check_end(self):
        if board.filled(): self.game_won(None)

        for player in players:
            for line in self.win_lines:
                if board.completed(line, player):
                    self.game_won(player)

    def run(self):
        self.win_lines = self.make_win_lines()

        for player in cycle(players):
            board[ board.random_blank() ] = player
            board.draw()
            self.check_end()


if __name__ == "__main__":
    board = TictactoeBoard(size, blank)
    Tictactoe().run()
