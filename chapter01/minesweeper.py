#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import randint
from time import sleep

from utils import Loc
from minesweeper_lib import nl, MinesweeperBoard, Minesweeper

size       = 12, 6
num_mines  = randint(4, 8)
prompt     = "> "
pause_time = 0.7

ai_run     = 1


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
        """Get user command and mark mine or reveal a location; check if game is won/lost."""
        inp = raw_input(prompt)
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
            print(nl, "loc", loc.x+1, loc.y+1, nl)
            msweep.check_end( board.reveal(board[loc]) )
            loc = loc.moved(-1, 0)      # move location to the left
            board.draw()
            sleep(pause_time)


if __name__ == "__main__":
    board = MinesweeperBoard(size, num_mines)
    msweep = Minesweeper(board)
    try: Test().test()
    except KeyboardInterrupt: pass
