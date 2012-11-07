#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import sleep

from board import Loc, Board

size       = 3
pause_time = 0.3
blank      = '.'
players    = 'xo'


class TictactoeBoard(Board):
    def filled(self):
        return not any( self[loc]==blank for loc in self.locations() )

    def random_blank(self):
        return rndchoice( [loc for loc in self.locations() if self[loc]==blank] )

    def completed(self, line, item):
        return all( self[loc]==item for loc in line )


class Tictactoe(object):
    winmsg  = "%s is the winner!"
    drawmsg = "It's a draw!"

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

        lines.extend((diag1, diag2))
        self.win_lines = lines

    def game_won(self, player):
        print(self.winmsg % player if player else self.drawmsg)
        sys.exit()

    def check_winner(self):
        for player in players:
            for line in self.win_lines:
                if board.completed(line, player):
                    self.game_won(player)

    def run(self):
        self.make_win_lines()

        while True:
            for player in players:
                board[ board.random_blank() ] = player
                board.draw()
                print()
                sleep(pause_time)

                self.check_winner()
                if board.filled(): self.game_won(None)


if __name__ == "__main__":
    board = TictactoeBoard(size, blank)
    Tictactoe().run()
