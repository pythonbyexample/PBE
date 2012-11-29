#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import randint
from time import sleep

from utils import TextInput, nl, first
from minesweeper_lib import MinesweeperBoard, Minesweeper, Tile

size       = 6
num_mines  = randint(4, 8)
mark_key   = 'm'
ai_run     = 0
padding    = 2, 1


class Test(object):
    def test(self):
        # allow entering of multiple (up to 10) locations
        pattern        = "%s? loc%s" % (mark_key, " loc?"*9)
        self.textinput = TextInput(pattern, board)
        while True:
            board.draw()
            self.ai_move() if ai_run else self.make_move()

    def make_move(self):
        cmd  = self.textinput.getinput()
        mark = bool(first(cmd) == mark_key)
        if mark: cmd.pop(0)

        for loc in cmd:
            tile = board[loc]
            tile.toggle_mark() if mark else board.reveal(tile)
            msweep.check_end(tile)

    def ai_move(self):
        """Very primitive `AI', does not mark mines & does not try to avoid them."""
        loc = board.random_hidden()

        while loc.x:
            print(nl, "loc", loc.x+1, loc.y+1, nl)
            msweep.check_end( board.reveal( board[loc] ) )
            loc = loc.moved(-1, 0)      # move location to the left

            if board[loc].revealed:
                continue
            board.draw()


if __name__ == "__main__":
    board = MinesweeperBoard(size, Tile, num_mines=num_mines, num_grid=True, padding=padding)
    msweep = Minesweeper(board)
    try: Test().test()
    except KeyboardInterrupt: pass
