#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import randint
from time import sleep

from utils import Loc
from minesweeper_lib import Board, Minesweeper

size      = 8
num_mines = randint(4, 8)
ai_run    = 0


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
        """Get user command and mark mine or reveal a location; check if game is won/lost."""
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
    board = Board(size, num_mines)
    msweep = Minesweeper(board)
    Test().test()
