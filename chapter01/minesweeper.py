#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import randint
from time import sleep

from utils import parse_hnuminput
from minesweeper_lib import nl, space, MinesweeperBoard, Minesweeper, Loc

size       = 6
num_mines  = randint(4, 8)
pause_time = 0.7
prompt     = '> '
quit_key   = 'q'
mark_key   = 'm'

ai_run     = 0


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
        if inp == quit_key: sys.exit()

        mark = inp.startswith(mark_key)
        inp = inp.lstrip(mark_key + space)

        if space in inp: inp = inp.split()
        x, y = parse_hnuminput(inp)
        tile = board[ Loc(x, y) ]

        tile.toggle_mark() if mark else board.reveal(tile)
        msweep.check_end(tile)

    def ai_move(self):
        """Very primitive `AI', does not mark mines & does not try to avoid them."""
        loc = board.random_hidden().loc

        while loc.x:
            print(nl, "loc", loc.x+1, loc.y+1, nl)
            msweep.check_end(board.reveal( board[loc] ))
            loc = loc.moved(-1, 0)      # move location to the left
            if board[loc].revealed:
                continue
            board.draw()
            sleep(pause_time)


if __name__ == "__main__":
    board = MinesweeperBoard(size, num_mines)
    msweep = Minesweeper(board)
    try: Test().test()
    except KeyboardInterrupt: pass
