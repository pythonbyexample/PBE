#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep
from itertools import cycle

from utils import enumerate1, range1, ujoin, Loop, TextInput
from board import Board, Loc

size        = 4
players     = 'OX'
ai_players  = 'X'

check_moves = 15

nl          = '\n'
space       = ' '
padding     = 5, 3


class Tile(object):
    num    = 1
    maxnum = 1
    player = None

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return "%s %s" % (self.player or space, self.num)

    def add(self, player):
        """ Increment tile number; if number wraps, increment neighbour tiles.
            `bblocks.counter` is used to avoid infinite recursion loops.
        """
        bblocks.counter.next()
        if bblocks.counter == check_moves: bblocks.check_end(player)

        if self._add(player):
            for tile in board.cross_neighbours(self):
                tile.add(player)
            board.draw()

    def _add(self, player):
        self.player = player
        self.num.next()
        return bool(self.num == 1)


class BlocksBoard(Board):
    def __init__(self, size, def_tile):
        super(BlocksBoard, self).__init__(size, def_tile, num_grid=True, padding=padding)
        for tile in self:
            tile.maxnum = len( [self.valid(n) == True for n in self.neighbour_cross_locs(tile.loc)] )
            tile.num    = Loop(range1(tile.maxnum))

    def random_move(self, player):
        """If a 50% roll is made, return the move closest to completing a tile; otherwise a random move."""
        tiles = [t for t in self if self.valid_move(player, t.loc)]

        def to_max(t): return t.maxnum - t.num
        tiles.sort(key=to_max)

        if randint(0,1) : return tiles[0]
        else            : return rndchoice(tiles)

    def valid_move(self, player, loc):
        return bool( self.valid(loc) and self[loc].player in (None, player) )

    def draw2(self):
        print(nl*5)
        print(space*5, ujoin( range1(self.width), space, tiletpl ), nl)

        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, space, tiletpl), nl*2)
        sleep(pause_time)


class BlockyBlocks(object):
    winmsg  = "%s has won!"
    counter = Loop(range1(check_moves))

    def check_end(self, player):
        if all(t.player==player for t in board):
            self.game_won(player)

    def game_won(self, player):
        print(nl, self.winmsg % player)
        sys.exit()


class Test(object):
    invalid_move = "Invalid move... try again"

    def run(self):
        self.textinput = TextInput(board)

        for p in cycle(players):
            board.draw()
            tile = board.random_move(p) if p in ai_players else self.get_move(p)
            tile.add(p)
            bblocks.check_end(p)

    def get_move(self, player):
        while True:
            loc = self.textinput.getloc()
            if board.valid_move(player, loc):
                return board[loc]
            else:
                print(self.invalid_move)


if __name__ == "__main__":
    board   = BlocksBoard(size, Tile)
    bblocks = BlockyBlocks()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
