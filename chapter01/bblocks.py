#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep

from utils import enumerate1, range1, parse_hnuminput, ujoin, flatten, AttrToggles, Loop
from board import Board, Loc, Dir

size           = 9
players        = ['g', 'b']
manual_players = ['g']

pause_time     = 0.2
nl             = '\n'
space          = ' '
prompt         = '> '
quit_key       = 'q'
divchar        = '-'
tiletpl        = "%3s"


class Tile(AttrToggles):
    num    = 1
    maxnum = 1
    colour = None

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return "%s%s" % (self.colour or space, self.num)

    def add(self, player):
        if self._add(player):
            for tile in board.cross_neighbours(self):
                tile.add(player)
            board.draw(pause_time)

    def _add(self, colour):
        self.colour = colour
        self.num.next()
        return bool(self.num == 1)


class BlocksBoard(Board):
    def __init__(self, size, def_tile):
        super(BlocksBoard, self).__init__(size, def_tile)
        for tile in self:
            tile.maxnum = len( [self.valid(n) == True for n in self.neighbour_cross_locs(tile.loc)] )
            tile.num    = Loop(range1(tile.maxnum))

    def random_tile(self, colour):
        return rndchoice( [t for t in self if self.valid_move(colour, t.loc)] )

    def valid_move(self, player, loc):
        return bool( self.valid(loc) and self[loc].colour in (None, player) )

    def draw(self, pause):
        print(space*3, ujoin( range1(self.width), space, tiletpl ), nl)

        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, space, tiletpl), nl)
        print(divchar * (self.width*4 + 5))
        sleep(pause)


class BlockyBlocks(object):
    winmsg  = "%s has won!"

    def expand_cmd(self, cmd):
        count = 1
        if len(cmd) == 2:
            count = int(cmd[0])
            cmd = cmd[-1]
        return [commands[cmd]] * count

    def expand_program(self, inp):
        return flatten( self.expand_cmd(cmd) for cmd in inp.split() ) if inp else ["random"]

    def check_end(self, player):
        if all(t.colour==player for t in self):
            self.game_won(player)

    def game_won(self, player):
        print(nl, self.winmsg % player)
        sys.exit()


class Test(object):
    invalid_inp  = "Invalid input"
    invalid_move = "Invalid move... try again"

    def run(self):
        while True:
            for p in players:
                board.draw(pause_time)
                tile = self.get_move(p) if p in manual_players else board.random_tile(p)
                tile.add(p)

    def get_move(self, player):
        while 1:
            try:
                inp = raw_input(prompt).strip()
                if inp == quit_key: sys.exit()

                cmd = inp.split() if space in inp else inp
                x, y = parse_hnuminput(cmd[:2])
                loc = Loc(x, y)

                if board.valid_move(player, loc):
                    return board[loc]
            except (IndexError, ValueError, TypeError, KeyError):
                print(self.invalid_inp)
                continue



if __name__ == "__main__":
    board   = BlocksBoard(size, Tile)
    bblocks = BlockyBlocks()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
