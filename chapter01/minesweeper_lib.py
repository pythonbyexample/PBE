#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import time

from utils import AttrToggles, ujoin, range1, enumerate1, timefmt, space, nl
from board import Loc, Board, BaseTile

blank      = ' '
hiddenchar = '.'
minechar   = '✇'
flag       = '⚑'


class Tile(BaseTile, AttrToggles):
    revealed = mine = marked = False
    hidden   = True
    number   = None

    attribute_toggles = [("hidden", "revealed")]

    def __repr__(self):
        if   self.hidden : return hiddenchar
        elif self.marked : return flag
        elif self.mine   : return minechar
        else             : return str(self.number or blank)

    def toggle_mark(self):
        self.marked = not self.marked
        self.hidden = not self.hidden


class MinesweeperBoard(Board):
    def __init__(self, *args, **kwargs):
        num_mines = kwargs.pop("num_mines")

        super(MinesweeperBoard, self).__init__(*args, **kwargs)
        self.divider = '-' * (self.width * 4 + 4)

        for _ in range(num_mines):
            self.random_empty().mine = True

        for tile in self:
            tile.number = sum( nbtile.mine for nbtile in self.neighbours(tile) )

    def cleared(self):
        return all( self.marked_or_revealed(tile) for tile in self )

    def marked_or_revealed(self, tile) : return bool(tile.revealed or tile.mine and tile.marked)
    def random_hidden(self)            : return rndchoice(self.locations("hidden"))
    def random_empty(self)             : return rndchoice(self.tiles_not("mine"))

    def reveal(self, tile):
        if not tile.number:
            self.reveal_blank_neighbours(tile)
        tile.revealed = True
        return tile

    def reveal_blank_neighbours(self, tile):
        """ Reveal all empty (number=0) tiles adjacent to starting tile `loc` and subsequent unhidden tiles.
            Uses floodfill algorithm.
        """
        if tile.number   : tile.revealed = True
        if tile.revealed : return

        tile.revealed = True
        for nbtile in self.neighbours(tile):
            self.reveal_blank_neighbours(nbtile)


class Minesweeper(object):
    start    = time()
    win_msg  = "\n All mines cleared! (%s)"
    lose_msg = "\n KABOOM. END."

    def __init__(self, board):
        self.board = board

    def check_end(self, tile):
        """Check if game is lost (stepped on a mine), or won (all mines found)."""
        if tile.mine and not tile.marked:
            self.game_lost()
        elif self.board.cleared():
            self.game_won()

    def game_lost(self):
        B = self.board
        for tile in B: B.reveal(tile)
        B.draw()
        print(self.lose_msg)
        sys.exit()

    def game_won(self):
        self.board.draw()
        print( self.win_msg % timefmt(time() - self.start) )
        sys.exit()
