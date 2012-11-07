#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
from random import choice as rndchoice
from utils import enumerate1, Loc

board_size = 30, 10
nl         = '\n'
space      = ' '
tiletpl    = "%3s"
shipchar   = '#'
sunkship   = '%'
blank      = '.'
hitchar    = '*'


class Tile(object):
    """Tile that may be a ship or blank space (water)."""
    ship   = False
    is_hit = False

class Blank(Tile):
    char = blank

    def hit(self):
        self.is_hit = True
        self.char   = hitchar

class Ship(Tile):
    char = shipchar
    ship = True

    def hit(self):
        self.is_hit = True
        self.char   = sunkship


class BattleshipBoard(Board):
    def __init__(self, size):
        super(BattleshipBoard, self).__init__(size, Tile, stackable=False, tiletpl=tiletpl)

    def draw(self):
        print( ujoin((n+1 for n in range(self.maxx), tpl=tiletpl)), nl )
        for n, row in enumerate1(self.board):
            print( str(n), ujoin(row, tpl=tiletpl), nl)

    def all_unhit(self):
        return (loc for loc in self if not self[loc].is_hit)

    def random_unhit(self):
        return rndchoice(self.all_unhit())

    def reveal(self, loc):
        """UNUSED"""
        self[loc].hidden = False
        return self[loc]

    def valid_hidden(self, loc):
        return bool(self.valid(loc) and self[loc].hidden)


class ShipTracker(object):
    """Track currently targeted ship."""
    start = None
    dir   = None

    def __init__(self, board):
        self.board = board

    def random_hit(self):
        """Hit a random location on board and save it to `self.start` if a ship is hit."""
        board = self.board
        loc = board.random_unhit()
        board[loc].hidden = False
        if board[loc].ship:
            self.start = loc

    def track(self):
        """ Track the same ship across multiple turns.

            Keep track of the first hit (self.start) and direction (0:horiz, 1:vertical),
            try new locations in saved direction until the entire ship is sunk.
        """
        if not self.start:
            self.random_hit()
            return

        board   = self.board
        loc     = self.start
        hdirs   = [(1,0), (-1,0)]     # horizontal
        vdirs   = [(0,1), (0,-1)]     # vertical
        alldirs = [(dir in hdirs, dir) for dir in hdirs + vdirs]

        if self.dir is None:
            locs = [(is_hdir, loc.moved(dir)) for is_hdir, dir in alldirs]
            locs = [(is_hdir, loc) for loc in locs if board.valid_hidden(loc)]
            if locs:
                is_hdir, loc = locs[0]
                board[loc].hidden = False
                if board[loc].ship:
                    self.dir = int(is_hdir)
            else:
                self.random_hit()
            return

        dirs = hdirs if self.dir else vdirs
        dir  = dirs.pop()

        while True:
            loc = loc.moved(dir)
            tile = board[loc]

            if tile.hidden:
                board[loc].hidden = False
                return
            elif tile.is_hit and not tile.ship:
                if dirs:
                    dir = dirs.pop()
                else:
                    self.random_hit()


class Player(object):
    pass


class Battleship(object):
    pass


class Test(object):
    pass
