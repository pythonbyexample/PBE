#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep
from string import digits

from utils import enumerate1, range1, ujoin
from board import Board, Loc

size       = 9
pause_time = 0.2

nl         = '\n'
space      = ' '
prompt     = '> '
quit_key   = 'q'
tiletpl    = "%2s"
divider    = '-' * (27 + 3)
blank      = '.'

# using format produced by QQwing program; sample puzzle split into rows for checking
# ".13.....2 2.....48. ...7...19 ...9..8.. 7......2. ...3..... ..263.9.. 4.9.7.6.. ..149...8"
puzzles    = [".13.....22.....48....7...19...9..8..7......2....3.......263.9..4.9.7.6....149...8"]


class SudokuBoard(Board):
    def __init__(self, size, def_tile, puzzle):
        super(SudokuBoard, self).__init__(size, def_tile)
        for loc, val in zip(self.locations(), puzzle):
            self[loc] = val

        self.regions = []

        for n in range(3):
            for m in range(3):
                region = []
                for x in range(3 + 3*n):
                    region.extend( [Loc(x, y) for y in range(3 + 3*m)] )
                self.regions.append(region)

        self.lines = []

        for n in range(9):
            self.lines.append( [Loc(x, n) for x in range(9)] )
            self.lines.append( [Loc(n, y) for y in range(9)] )

    def draw(self):
        print(nl*5)
        print(space*2, ujoin( range1(self.width), space, tiletpl ), nl)

        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, space, tiletpl), nl)
        print(divider)


class SudokuGame(object):
    winmsg  = "Solved!"

    def check(self, loc, val):
        for reg_line in board.lines + board.regions:
            if val in (board[loc] for loc in reg_line):
                return False
        return True

    def check_end(self):
        if not any(t==blank for t in board):
            self.game_won()

    def game_won(self):
        print(nl, self.winmsg)
        sys.exit()



class Test(object):
    invalid_inp  = "Invalid input"
    invalid_move = "Invalid move... try again"

    def run(self):
        while True:
            board.draw()
            x, y, val = self.get_move()
            loc = Loc(x, y)
            if board.valid(loc) and board[loc]==blank:
                if sudoku.check(loc, val):
                    board[loc] = val
                    sudoku.check_end()
                else:
                    print(self.invalid_move)

    def get_move(self):
        while 1:
            try:
                inp = raw_input(prompt).strip()
                if inp == quit_key: sys.exit()
                # use hnuminput
                return int(inp[0]), int(inp[1]), inp[2]
            except (IndexError, ValueError, TypeError, KeyError):
                print(self.invalid_inp)
                continue


if __name__ == "__main__":
    board   = SudokuBoard( size, blank, rndchoice(puzzles) )
    sudoku  = SudokuGame()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
