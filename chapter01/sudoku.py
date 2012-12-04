#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep

from utils import enumerate1, range1, ujoin, TextInput, space, nl
from board import Board, Loc, BaseTile

size    = 9
blank   = '.'
tiletpl = '%2s'
divider = '-' * (27 + 9)

rng3    = range(3)
rng9    = range(9)
offsets = (0, 3, 6)

# in the format produced by QQwing program; just one puzzle for testing
puzzles    = [".13.....22.....48....7...19...9..8..7......2....3.......263.9..4.9.7.6....149...8"]


class Tile(BaseTile):
    initial = blank = False
    num     = char = None

    def __repr__(self)      : return self.char or str(self.num)
    def __eq__(self, other) : return bool(self.num == other)
    def __ne__(self, other) : return bool(self.num != other)


class Number(Tile):
    def __init__(self, num):
        super(Number, self).__init__()
        self.num = int(num)

class Blank(Tile)     : char = blank
class Initial(Number) : pass


class SudokuBoard(Board):
    def __init__(self, size, def_tile, puzzle):
        super(SudokuBoard, self).__init__(size, def_tile)

        for loc, val in zip(self.locations(), puzzle):
            if val != blank:
                self[loc] = Initial(val)

        self.regions = [self.make_region(xo, yo) for xo in offsets for yo in offsets]

        lines = []
        for n in rng9:
            lines.extend(( [Loc(x, n) for x in rng9], [Loc(n, y) for y in rng9] ))
        self.lines = lines

    def make_region(self, xo, yo):
        """Make one region at x offset `xo` and y offset `yo`."""
        return [ Loc(xo + x, yo + y) for x in rng3 for y in rng3 ]

    def draw(self):
        print(nl*5)
        def ljoin(L): return ujoin(L, space, tiletpl)

        print( space*4, ljoin((1,2,3)), space, ljoin((4,5,6)), space, ljoin((7,8,9)), nl )

        for n, row in enumerate1(self.board):
            print(tiletpl % n, space,
                  ljoin(row[:3]), space, ljoin(row[3:6]), space, ljoin(row[6:9]),
                  nl)
            if n in (3,6): print()
        print(divider)


class Sudoku(object):
    winmsg = "Solved!"

    def valid_move(self, loc, val):
        if board[loc].initial: return False

        for reg_line in board.lines + board.regions:
            if loc in reg_line and val in (board[loc] for loc in reg_line):
                return False
        return True

    def check_end(self):
        if not any(t.blank for t in board):
            print(nl, self.winmsg)
            sys.exit()


class Test(object):
    def run(self):
        self.textinput = TextInput("loc %d", board)
        while True:
            board.draw()
            loc, val   = self.get_move()
            board[loc] = Number(val)
            sudoku.check_end()

    def get_move(self):
        while True:
            cmd = self.textinput.getinput()
            if sudoku.valid_move(*cmd) : return cmd
            else                       : print(self.textinput.invalid_move)


if __name__ == "__main__":
    board  = SudokuBoard(size, Blank, rndchoice(puzzles))
    sudoku = Sudoku()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
