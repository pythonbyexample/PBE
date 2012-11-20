#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import randint
from time import sleep

from utils import TextInput
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
        self.textinput = TextInput(board, ("loc", "%s loc"))
        while True:
            board.draw()
            self.ai_move() if ai_run else self.get_move()

    def get_move(self):
        while True:
            cmd  = self.textinput.getinput()
            ok   = True
            mark = False
            loc  = cmd.pop()

            if cmd:
                if cmd == [mark_key] : mark = True
                else                 : ok = False

            if board.valid(loc):
                tile = board[loc]
                tile.toggle_mark() if mark else board.reveal(tile)
                msweep.check_end(tile)
                return
            else:
                ok = False

            if not ok:
                print(self.invalid_move)

    def ai_move(self):
        """Very primitive `AI', does not mark mines & does not try to avoid them."""
        loc = board.random_hidden().loc

        while loc.x:
            print(nl, "loc", loc.x+1, loc.y+1, nl)
            msweep.check_end( board.reveal( board[loc] ) )
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
