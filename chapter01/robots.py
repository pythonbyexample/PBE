#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep

from utils import enumerate1, range1, parse_hnuminput, ujoin, flatten, AttrToggles, Loop
from board import Board, Loc, Dir

size          = 10, 10
num_robots    = 3
num_players   = 1
pause_time    = 0.2
missile_pause = 0.05

nl            = '\n'
space         = ' '
prompt        = '> '
blank         = '.'
robot_char    = 'r'
player_char   = '@'
missile_char  = '*'
quit_key      = 'q'
stat_sep      = " | "
# commands      = dict(m="move", t="turn_cw", T="turn_ccw", f="fire", w="wait", r="random")
commands      = dict(m="move", t="turn_cw", T="turn_ccw", f="fire", r="random")


class Tile(AttrToggles):
    robot   = False
    blank   = False
    missile = False
    health  = None

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return str(self.health) if self.robot else self.char


class Blank(Tile):
    char  = blank
    blank = True


class Mobile(Tile):
    def __init__(self, loc=None, direction=None):
        self.loc       = loc
        self.direction = direction or Loop(board.dirlist2, name="dir")
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
        cmd = getattr( self, rndchoice(commands.values()) )
        cmd()

    def fire(self):
        start = board.getloc(self.loc, self.direction.dir)
        if not start: return

        if board[start].blank:
            Missile(start, self.direction).go()
        else:
            Missile().hit(board[start])

    def move(self):
        loc = board.getloc(self.loc, self.direction.dir)
        if loc and board[loc].blank:
            board.move(self, loc)
        else:
            self.program = []

    def create_program(self):
        return [ rndchoice(commands.values()) ] * randint(1, 6)

class Robot(Mobile):
    char   = robot_char
    robot  = True
    health = 5

    def die(self):
        del board[self.loc]
        robots.remove(self)


class Player(Mobile):
    char        = player_char
    player      = True
    health      = 5
    status_msg  = "%s [%s]"
    invalid_msg = "Invalid input"

    def create_program(self):
        while 1:
            try:
                inp = raw_input(prompt).strip()
                if inp == quit_key: sys.exit()

                return rgame.expand_program(inp)
            except (IndexError, ValueError, TypeError, KeyError):
                print(self.invalid_msg)
                continue

    def status(self):
        # print("board.dirnames", repr(board.dirnames))
        return self.status_msg % (self.health, board.dirnames[self.direction.dir])

    def die(self):
        del board[self.loc]
        players.remove(self)


class Missile(Mobile):
    char    = missile_char
    missile = True
    health  = 1

    def go(self):
        while True:
            loc = board.getloc(self.loc, self.direction.dir)
            if not loc:
                self.die()
                break

            if board[loc].blank:
                board.move(self, loc)
                board.draw(missile_pause)
            else:
                self.hit(board[loc])
                break

    def hit(self, target):
        target.health -= 1
        if not target.health:
            target.die()
        self.die()

    def die(self):
        """Note: we need to check for `loc` for a special case of a missile with loc=None."""
        if self.loc: del board[self.loc]


class RBoard(Board):
    def getloc(self, start, dir):
        """Return location next to `start` point in direction `dir`."""
        loc = Loc(start.x + dir.x, start.y + dir.y)
        return loc if self.valid(loc) else None

    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )

    def draw(self, pause):
        print(nl*5)
        super(RBoard, self).draw()
        print(nl, stat_sep.join(p.status() for p in players) )
        sleep(pause)


class RobotsGame(object):
    def expand_cmd(self, cmd):
        count = 1
        if len(cmd) == 2:
            count = int(cmd[0])
            cmd = cmd[-1]
        return [commands[cmd]] * count

    def expand_program(self, inp):
        return flatten( self.expand_cmd(cmd) for cmd in inp.split() ) if inp else ["random"]


class Test(object):
    def run(self):
        while True:
            board.draw(pause_time)
            for mobile in players + robots: mobile.go()


if __name__ == "__main__":
    board   = RBoard(size, Blank)
    rgame   = RobotsGame()
    players = [ Player(board.random_blank()) for _ in range(num_players) ]
    robots  = [ Robot(board.random_blank()) for _ in range(num_robots) ]

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
