#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep

from utils import enumerate1, range1, parse_hnuminput, ujoin, Loop
from board import Board, Loc, Dir

size           = 4
players        = ['O', 'X']
# manual_players = ['O']
manual_players = []

pause_time     = 0.2
check_moves    = 15

nl             = '\n'
space          = ' '
prompt         = '> '
quit_key       = 'q'
divchar        = '-'
tiletpl        = "%5s"


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
        super(BlocksBoard, self).__init__(size, def_tile)
        for tile in self:
            tile.maxnum = len( [self.valid(n) == True for n in self.neighbour_cross_locs(tile.loc)] )
            tile.num    = Loop(range1(tile.maxnum), name='n')

    def random_move(self, player):
        """If a 50% roll is made, return the move closest to completing a tile; otherwise a random move."""
        tiles = [t for t in self if self.valid_move(player, t.loc)]

        def to_max(t): return t.maxnum - t.num
        tiles.sort(key=to_max)

        if randint(0,1) : return tiles[0]
        else            : return rndchoice(tiles)

    def valid_move(self, player, loc):
        return bool( self.valid(loc) and self[loc].player in (None, player) )

    def draw(self):
        print(nl*5)
        print(space*5, ujoin( range1(self.width), space, tiletpl ), nl)

        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, space, tiletpl), nl*2)
        print(divchar * (self.width*6 + 5))
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
    invalid_inp  = "Invalid input"
    invalid_move = "Invalid move... try again"

    def run(self):
        while True:
            for p in players:
                board.draw()
                tile = self.get_move(p) if p in manual_players else board.random_move(p)
                tile.add(p)
                bblocks.check_end(p)

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
