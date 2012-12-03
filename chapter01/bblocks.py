#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep
from itertools import cycle

from utils import Loop, TextInput, enumerate1, range1, ujoin, first, nl, space
from board import Board, Loc

size        = 4
# players     = 'ʘΔ'
p1numbers   = "➀➁➂➃"
p2numbers   = "➊➋➌➍"
players     = p1numbers, p2numbers
ai_players  = 'X'
check_moves = 15
padding     = 5, 3


class Tile(object):
    player = None

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return players[self.player-1][self.num-1] if self.player else str(self.num)
        # return "%s %s" % (self.player or space, self.num)

    def increment(self, player):
        """ Increment tile number; if number wraps, increment neighbour tiles.
            `bblocks.counter` is used to avoid infinite recursion loops.
        """
        if not bblocks.counter.next(): bblocks.check_end(player)

        if self._increment(player):
            for tile in board.cross_neighbours(self):
                tile.increment(player)
            board.draw()

    def _increment(self, player):
        self.player = player
        self.num.next()
        return bool(self.num == 1)


class BlocksBoard(Board):
    def __init__(self, *args, **kwargs):
        super(BlocksBoard, self).__init__(*args, **kwargs)
        neighbours = self.neighbour_cross_locs
        for tile in self:
            tile.maxnum = len( [self.valid(n) for n in neighbours(tile)] )
            tile.num    = Loop(range1(tile.maxnum))

    def calculate_move(self, player):
        """Randomly choose between returning the move closest to completing a tile or a random move."""
        tiles = [t for t in self if self.valid_move(player, t.loc)]

        def to_max(t): return t.maxnum - t.num
        tiles.sort(key=to_max)
        return rndchoice( [first(tiles), rndchoice(tiles)] )

    def valid_move(self, player, tile):
        return bool(tile.player is None or tile.player==player)


class BlockyBlocks(object):
    winmsg  = "%s has won!"
    counter = Loop(range(check_moves))

    def check_end(self, player):
        if all(t.player==player for t in board):
            self.game_won(player)

    def game_won(self, player):
        print(nl, self.winmsg % player)
        sys.exit()


class Test(object):
    def run(self):
        self.textinput = TextInput(board=board)

        for p in cycle(players):
            board.draw()
            tile = board.calculate_move(p) if p in ai_players else self.get_move(p)
            tile.increment(p)
            bblocks.check_end(p)

    def get_move(self, player):
        while True:
            loc = self.textinput.getloc()
            if board.valid_move(player, board[loc]) : return board[loc]
            else                             : print(self.textinput.invalid_move)


if __name__ == "__main__":
    board   = BlocksBoard(size, def_tile, num_grid=True, padding=padding)
    bblocks = BlockyBlocks()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
