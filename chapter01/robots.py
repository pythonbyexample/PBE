#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from time import sleep

from utils import enumerate1, range1, parse_hnuminput, ujoin, flatten, AttrToggles, Loop
from board import Board, Loc

size       = 10, 10
num_robots = 6
pause_time = 0.1

nl         = '\n'
space      = ' '
prompt     = '> '
blank      = '.'
quit_key   = 'q'
commands   = dict(m="move", t="turn_cw", T="turn_ccw", f="fire", w="wait", r="random")



class Tile(AttrToggles):
    """Tile that may be a ship or blank space (water)."""
    robot             = False
    bullet            = False
    blank             = False
    attribute_toggles = [("hidden", "revealed")]

    def __init__(self, x, y):
        self.loc = Loc(x, y)

    def __repr__(self):
        return self.char


class Blank(Tile):
    char  = blank
    blank = True

class Robot(Tile):
    char       = 'r'
    robot      = True

    def __init__(self, *args):
        super(Robot, self).__init__(*args)
        directions     = board.directions()
        self.direction = Loop(directions, name="dir")
        self.program   = []

    def go(self):
        if not self.program:
            self.create_program()
        cmd, length = self.program.pop(0)

        for _ in range(length):
            getattr(self, commands[cmd])()
            if not self.program:
                break

    def turn_cw(self):
        self.direction.next()

    def turn_ccw(self):
        self.direction.prev()

    def wait(self):
        pass

    def random(self):
        getattr(self, commands[ rndchoice(commands) ])()

    def move(self):
        to = board.getloc(self.loc, self.direction.dir)
        if board.valid(to):
            board.move(self, to)
        else:
            self.program = []

    def create_program(self):
        self.program = [ (rndchoice(commands), randint(1, 6)) ]


class Player(Robot):
    char = '@'
    player = True

class Bullet(Tile):
    char = '*'
    bullet = True


class RBoard(Board):
    def getloc(self, start, dir):
        """Return location next to `start` point in direction `dir`."""
        return Loc(start.x + dir.x, start.y + dir.y)

    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )


class Robots(object):
    def program_expand(self, inp):
        program = []

        for cmd in inp.split():
            count = 1
            if len(cmd) == 2:
                count = int(cmd[0])
                cmd = cmd[-1]
            program.extend(cmd for _ in range(count))
        return program


class Test(object):
    def run(self):
        while True:
            print(nl*5)
            board.draw()
            if not player.program: self.create_program()
            player.go()
            for robot in robots:
                robot.go()

    def create_program(self):
        while 1:
            try:
                inp = raw_input(prompt)
                if inp == quit_key:
                    sys.exit()

                player.program = rgame.program_expand(inp)
                return
            except (IndexError, ValueError, TypeError):
                continue


if __name__ == "__main__":
    board  = RBoard(size, Blank)
    robots = [Robot(*board.random_blank()) for _ in range(num_robots)]
    for r in robots:
        board[r.loc] = r
    player = Player(*board.random_blank())
    board[player.loc] = player
    rgame  = Robots()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
