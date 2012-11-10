#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep

from utils import enumerate1, range1, parse_hnuminput, ujoin, flatten, AttrToggles, Loop
from board import Board, Loc

size          = 10, 10
num_robots    = 3
num_players   = 1
pause_time    = 0.2
missile_pause = 0.05

nl            = '\n'
space         = ' '
prompt        = '> '
blank         = '.'
quit_key      = 'q'
# commands      = dict(m="move", t="turn_cw", T="turn_ccw", f="fire", w="wait", r="random")
commands      = dict(m="move", t="turn_cw", T="turn_ccw", f="fire", r="random")


class Tile(AttrToggles):
    robot             = False
    bullet            = False
    blank             = False
    missile           = False
    health            = None
    attribute_toggles = [("hidden", "revealed")]

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return str(self.health) if self.robot else self.char


class Blank(Tile):
    char  = blank
    blank = True


class Mobile(Tile):
    def __init__(self, loc, direction=None):
        self.loc       = loc
        directions     = board.directions()
        self.direction = direction or Loop(directions, name="dir")
        self.program   = []

        if loc: board[loc] = self

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
        start = board.getloc(self.loc, Loc(*self.direction.dir))

        if not board.valid(start):
            return
        if not board[start].blank:
            m = Missile(loc=None)
            m.hit(board[start])
            return
        Missile(start, self.direction).move()

    def move(self):
        to = board.getloc(self.loc, Loc(*self.direction.dir))
        if board.valid(to) and board[to].blank:
            board.move(self, to)
        else:
            self.program = []

    def create_program(self):
        return [ rndchoice(commands.values()) ] * randint(1, 6)

    def die(self):
        del board[self.loc]
        (robots if self.robot else players).remove(self)


class Robot(Mobile):
    char = 'r'
    robot = True
    health = 5


class Player(Mobile):
    char      = '@'
    player    = True
    health    = 5
    statusmsg = "%s [dir %s]"

    def create_program(self):
        while 1:
            try:
                inp = raw_input(prompt)
                if inp == quit_key:
                    sys.exit()

                print("rgame.program_expand(inp)", rgame.program_expand(inp))
                return rgame.program_expand(inp)
            except (IndexError, ValueError, TypeError, KeyError):
                print("Invalid input")
                continue

    def status(self):
        return self.statusmsg % (self.health, self.direction.dir)


class Missile(Mobile):
    char    = '*'
    missile = True
    health  = None

    def move(self):
        while True:
            to = board.getloc(self.loc, Loc(*self.direction.dir))

            if board.valid(to):
                if not board[to].blank:
                    self.hit(board[to])
                else:
                    board.move(self, to)
                    print(nl*5)
                    board.draw()
                    sleep(missile_pause)
                    continue
            else:
                self.die()
            return

    def hit(self, target):
        if target.missile:
            self.die()
            target.die()
        else:
            target.health -= 1
            if not target.health:
                target.die()
            self.die()

    def die(self):
        if self.loc: del board[self.loc]


class RBoard(Board):
    def getloc(self, start, dir):
        """Return location next to `start` point in direction `dir`."""
        return Loc(start.x + dir.x, start.y + dir.y)

    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )

    def draw(self):
        super(RBoard, self).draw()
        print( '|'.join(p.status() for p in players) )


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
            for r in players + robots: r.go()

            sleep(pause_time)


if __name__ == "__main__":
    board   = RBoard(size, Blank)
    rgame   = RobotsGame()
    players = [ Player(board.random_blank()) for _ in range(num_players) ]
    robots  = [ Robot(board.random_blank()) for _ in range(num_robots) ]

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
