#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import randint
from time import sleep

from utils import TextInput
from minesweeper_lib import nl, MinesweeperBoard, Minesweeper

size       = 6
num_mines  = randint(4, 8)
pause_time = 0.7
mark_key   = 'm'
ai_run     = 0


class Test(object):
    def test(self):
        self.textinput = TextInput(board, "m? loc")
        while True:
            board.draw()
            self.ai_move() if ai_run else self.make_move()

    def make_move(self):
        cmd  = self.textinput.getinput()
        loc  = cmd.pop()
        mark = bool(cmd)
        tile = board[loc]
        tile.toggle_mark() if mark else board.reveal(tile)
        msweep.check_end(tile)

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
