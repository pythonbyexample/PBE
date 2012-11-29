#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep
from itertools import cycle

from utils import Loop, TextInput, enumerate1, range1, ujoin, first, nl, space
from board import Board, Loc, BaseTile

size        = 4
players     = 'OX'
ai_players  = 'X'
check_moves = 15
padding     = 5, 3


class Tile(BaseTile):
    num = maxnum = player = None

    def __repr__(self):
        return "%s %s" % (self.player or space, self.num)

    def add(self, player):
        """ Increment tile number; if number wraps, increment neighbour tiles.
            `bblocks.counter` is used to avoid infinite recursion loops.
        """
        bblocks.counter.next()
        if bblocks.counter == check_moves:
            bblocks.check_end(player)

        if self._add(player):
            for tile in board.cross_neighbours(self):
                tile.add(player)
            board.draw()

    def _add(self, player):
        self.player = player
        self.num.next()
        return bool(self.num == 1)


class BlocksBoard(Board):
    def __init__(self, *args, **kwargs):
        super(BlocksBoard, self).__init__(*args, **kwargs)
        neighbours = self.neighbour_cross_locs

        for tile in self:
            tile.maxnum = len( [self.valid(nbloc) for nbloc in neighbours(tile)] )
            tile.num    = Loop(range1(tile.maxnum))

    def random_move(self, player):
        """Randomly choose between returning the move closest to completing a tile or a random move."""
        tiles = [t for t in self if self.valid_move(player, t.loc)]

        def to_max(t): return t.maxnum - t.num
        tiles.sort(key=to_max)
        return rndchoice( [first(tiles), rndchoice(tiles)] )

    def valid_move(self, player, loc):
        return bool( self[loc].player in (None, player) )


class BlockyBlocks(object):
    winmsg  = "%s has won!"
    counter = Loop(range1(check_moves))

    def check_end(self, player):
        if all(tile.player==player for tile in board):
            print(nl, self.winmsg % player)
            sys.exit()


class Test(object):
    def run(self):
        self.textinput = TextInput(board=board)

        for p in cycle(players):
            board.draw()
            tile = board.random_move(p) if p in ai_players else self.get_move(p)
            tile.add(p)
            bblocks.check_end(p)

    def get_move(self, player):
        while True:
            loc = self.textinput.getloc()
            if board.valid_move(player, loc) : return board[loc]
            else                             : print(self.textinput.invalid_move)


if __name__ == "__main__":
    board   = BlocksBoard(size, def_tile, num_grid=True, padding=padding)
    bblocks = BlockyBlocks()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
