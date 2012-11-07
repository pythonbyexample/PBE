#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
from random import choice as rndchoice

from utils import enumerate1
from board import Board, Loc

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


class Player(object):
    pass


class Battleship(object):
    pass


class Test(object):
    pass
