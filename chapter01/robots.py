#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as rndchoice
from random import randint

from utils import Loop, TextInput, sjoin, nl
from board import Board, BaseTile


size          = 15, 10
num_players   = 1
num_robots    = 6
num_rocks     = 5

pause_time    = 0.2
missile_pause = 0.03
max_turns     = 25
max_cmds      = 15

chars         = dict(Player='☺', Missile='*', Rock='☗', Goal='⚑', Blank='.', Robot='♉')
health_dict   = dict(Player=5, Robot=5, Missile=1, Rock=10, Goal=99)
commands      = dict(m="move", t="turn_cw", T="turn_ccw", f="fire", w="wait", r="random")
fullcmds      = list(commands.values())


class Tile(BaseTile):
    player = robot = blank = missile = rock = goal = False
    health = None

    def __init__(self, loc):
        super(Tile, self).__init__(loc)
        self.char   = chars.get(self.__class__.__name__)
        self.health = health_dict.get(self.__class__.__name__)
        if loc: board[loc] = self

    def __repr__(self):
        return self.char

    def destroy(self):
        """Note: we need to check for `loc` for a special case of a missile with loc=None."""
        if self.loc: del board[self.loc]


class Blank(Tile) : pass
class Rock(Tile)  : pass
class Goal(Tile)  : pass


class Mobile(Tile):
    turn = 1

    def __init__(self, loc=None, direction=None):
        super(Mobile, self).__init__(loc)
        self.direction = direction or Loop(board.dirlist2, name="dir")
        self.program   = []

    def go(self):
        self.program = self.program or self.create_program()
        cmd = getattr(self, self.program.pop(0))
        cmd()
        self.turn += 1

    def turn_cw(self)  : self.direction.next()
    def turn_ccw(self) : self.direction.prev()
    def wait(self)     : pass

    def random(self):
        method = getattr(self, rndchoice(fullcmds))
        method()

    def fire(self):
        start = board.next_tile(self, self.direction.dir)

        if not start     : return
        elif start.blank : Missile(start.loc, self.direction).go()
        else             : Missile().hit(start)

    def move(self):
        tile = board.next_tile(self, self.direction.dir)

        if tile and tile.blank : board.move(self, tile.loc)
        else                   : self.program = []

    def create_program(self):
        return [rndchoice(fullcmds)] * randint(1, 6)


class Robot(Mobile):
    # def __repr__(self): return str(self.health)

    def destroy(self):
        del board[self]
        robots.remove(self)


class Player(Mobile):
    status_msg = "%shp | %s"

    def move(self):
        tile = board.next_tile(self, self.direction.dir)
        if tile and tile.goal:
            board.move(self, tile.loc)
            rgame.game_end(True)

        super(Player, self).move()
        if self.turn >= max_turns:
            rgame.game_end(False)

    def status(self):
        return self.status_msg % (self.health, board.dirnames[self.direction.dir])

    def destroy(self):
        del board[self]
        players.remove(self)


class Missile(Mobile):
    def go(self):
        while True:
            tile = board.next_tile(self, self.direction.dir)

            if not tile:
                self.destroy()
                break
            elif tile.blank:
                board.move(self, tile.loc)
                board.draw(missile_pause)
            else:
                self.hit(tile)
                break

    def hit(self, target):
        target.health -= 1
        if not target.health:
            target.destroy()
        self.destroy()


### BOARD ###

class RBoard(Board):
    stat_sep = " | "

    def random_blank(self):
        return rndchoice(self.locations("blank"))

    def status(self):
        print( nl, self.stat_sep.join(p.status() for p in players) )


class RobotsGame(object):
    winmsg  = "Victory! You've reached the goal!"
    losemsg = "You failed to reach the goal in %d turns.."

    def game_end(self, win):
        board.draw()
        print( nl, self.winmsg if win else (self.losemsg % max_turns) )
        sys.exit()

    def expand_program(self, cmds):
        L = []
        while True:
            if not cmds: break
            count = 1
            cmd   = cmds.pop(0)

            if isinstance(cmd, int):
                count, cmd = cmd, cmds.pop(0)

            L.extend( [commands[cmd]] * count )
        return L


class Test(object):

    def run(self):
        cmdpat  = "%d?"
        cmdpat  = cmdpat + " (%s)" % sjoin(commands.keys(), '|')
        pattern = cmdpat + (" %s?" % cmdpat) * (max_cmds - 1)

        self.textinput = TextInput(pattern, board, accept_blank=True, singlechar_cmds=True)

        while True:
            board.draw()
            for unit in players + robots:
                cprog        = self.create_program if unit.player else unit.create_program
                unit.program = unit.program or cprog()
                unit.go()

    def create_program(self):
        while True:
            try:
                program = self.textinput.getinput() or ['r']
                return rgame.expand_program(program)
            except (KeyError, IndexError):
                print(self.textinput.invalid_inp)


if __name__ == "__main__":
    board = RBoard(size, Blank, pause_time=pause_time)
    # board.place_tiles()

    rgame   = RobotsGame()
    randloc = board.random_blank
    players = [ Player(randloc()) for _ in range(num_players) ]
    robots  = [ Robot(randloc()) for _ in range(num_robots) ]
    rocks   = [ Rock(randloc()) for _ in range(num_rocks) ]

    Goal(randloc())

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
