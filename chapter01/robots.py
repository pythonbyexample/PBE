#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
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
    robot             = False
    bullet            = False
    blank             = False
    attribute_toggles = [("hidden", "revealed")]

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return self.char


class Blank(Tile):
    char  = blank
    blank = True


class Robot(Tile):
    char       = 'r'
    robot      = True

    def __init__(self, loc):
        self.loc       = loc
        board[loc]     = self
        directions     = board.directions()
        self.direction = Loop(directions, name="dir")
        self.program   = []

    def go(self):
        self.program = self.program or self.create_program()
        cmd = getattr(self, self.program.pop(0))
        cmd()

    def turn_cw(self):
        self.direction.next()

    def turn_ccw(self):
        self.direction.prev()

    def wait(self):
        pass

    def random(self):
        getattr(self, rndchoice(commands.values()) )()

    def fire(self):
        pass

    def move(self):
        to = board.getloc(self.loc, Loc(*self.direction.dir))
        if board.valid(to) and board[to].blank:
            board.move(self, to)
        else:
            self.program = []

    def create_program(self):
        return [ rndchoice(commands.values()) ] * randint(1, 6)


class Player(Robot):
    char = '@'
    player = True


class Missile(Tile):
    char = '*'
    missile = True


class RBoard(Board):
    def getloc(self, start, dir):
        """Return location next to `start` point in direction `dir`."""
        return Loc(start.x + dir.x, start.y + dir.y)

    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )


class RobotsGame(object):
    def program_expand(self, inp):
        program = []

        for cmd in inp.split():
            count = 1
            if len(cmd) == 2:
                count = int(cmd[0])
                cmd = cmd[-1]
            program.extend( [commands[cmd]] * count )
        return program


class Test(object):
    def run(self):
        while True:
            print(nl*5)
            board.draw()
            player.program = player.program or self.create_program()
            for r in [player] + robots: r.go()

    def create_program(self):
        while 1:
            try:
                inp = raw_input(prompt)
                if inp == quit_key:
                    sys.exit()

                print("rgame.program_expand(inp)", rgame.program_expand(inp))
                return rgame.program_expand(inp)
            except (IndexError, ValueError, TypeError):
                continue


if __name__ == "__main__":
    board  = RBoard(size, Blank)
    rgame  = RobotsGame()
    player = Player(board.random_blank())
    robots = [ Robot(board.random_blank()) for _ in range(num_robots) ]

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
