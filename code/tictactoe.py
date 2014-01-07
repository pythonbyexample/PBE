#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as randchoice
from itertools import cycle

from board import Loc, Board

size    = 3
blank   = '.'
players = 'XO'


class TictactoeBoard(Board):
    def filled(self):
        return not any(tile==blank for tile in self)

    def random_blank(self):
        return randchoice( [loc for loc in self.locations() if self[loc] == blank] )

    def completed(self, line, item):
        return all(self[loc] == item for loc in line)


class Tictactoe(object):
    winmsg  = "\n %s is the winner!"
    drawmsg = "\n It's a draw!"

    def make_win_lines(self):
        """Create a list of winning lines -- when a player fills any one of them, he wins."""
        winlines, diag1, diag2 = [], [], []

        for n in range(size):
            winlines.append( [Loc(m, n) for m in range(size)] )
            winlines.append( [Loc(n, m) for m in range(size)] )

            diag1.append(Loc(n, n))
            diag2.append(Loc(size-n-1, n))

        return winlines + [diag1, diag2]

    def check_end(self, player):
        """Check if `player` has won the game; check for a draw."""
        for line in self.win_lines:
            if board.completed(line, player):
                self.game_won(player)

        if board.filled(): self.game_won(None)

    def game_won(self, player):
        print(self.winmsg % player if player else self.drawmsg)
        sys.exit()

    def run(self):
        """Main loop."""
        self.win_lines = self.make_win_lines()

        for player in cycle(players):
            board[ board.random_blank() ] = player
            board.draw()
            self.check_end(player)


if __name__ == "__main__":
    board = TictactoeBoard(size, blank)
    Tictactoe().run()
