#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import randint
from time import sleep

from utils import TextInput, nl, first
from mines_lib import MinesBoard, Mines, Tile

size       = 6, 6
num_mines  = randint(4, 8)
mark_key   = 'm'
padding    = 2, 1


class BasicInterface(object):
    def run(self):
        # allow entering of multiple (up to 10) locations
        pattern        = "%s? loc%s" % (mark_key, " loc?"*9)
        self.textinput = TextInput(pattern, board, singlechar_cmds=True)
        while True:
            board.draw()
            self.make_move()

    def make_move(self):
        cmd  = self.textinput.getinput()
        mark = bool(first(cmd) == mark_key)
        if mark: cmd.pop(0)

        for loc in cmd:
            tile = board[loc]
            tile.toggle_mark() if mark else board.reveal(tile)
            mines.check_end(tile)


if __name__ == "__main__":
    board = MinesBoard(size, Tile, num_mines=num_mines, num_grid=True, padding=padding)
    mines = Mines(board)
    try: BasicInterface().run()
    except KeyboardInterrupt: pass
