#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import time

from utils import ujoin, range1, enumerate1
from board import Loc, Board

space      = ' '
blank      = ' '
hiddenchar = '.'
minechar   = '*'
nl         = '\n'
tiletpl    = '%3s'


class Tile(object):
    hidden = True
    mine   = False
    marked = False
    number = 0

    def __init__(self, x, y):
        self.loc = Loc(x,y)

    def __repr__(self):
        if self.marked   : return minechar
        elif self.hidden : return hiddenchar
        elif self.mine   : return minechar
        else             : return str(self.number or blank)

    def toggle_mark(self):
        """Toggle 'mine' mark on/off."""
        self.marked = not self.marked
        self.hidden = not self.hidden


class MinesweeperBoard(Board):
    """Minesweeper playing board."""

    def __init__(self, size, num_mines):
        super(MinesweeperBoard, self).__init__(size, Tile)

        self.divider = '-' * (self.width * 4 + 4)

        for _ in range(num_mines):
            self.random_empty().mine = True

        for tile in self:
            tile.number = sum( ntile.mine for ntile in self.neighbours(tile) )

    def marked_or_revealed(self, tile):
        return bool(not tile.hidden or tile.mine and tile.marked)

    def cleared(self):
        """All mines defused?"""
        return all( self.marked_or_revealed(tile) for tile in self )

    def all_hidden(self):
        return [tile for tile in self if tile.hidden]

    def random_hidden(self):
        return rndchoice(self.all_hidden())

    def all_empty(self):
        return [tile for tile in self if not tile.mine]

    def random_empty(self):
        return rndchoice(self.all_empty())

    def draw(self):
        columns = [n for n in range1(self.width)]
        print(space*3, ujoin(columns, space, tiletpl), nl)

        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, space, tiletpl), nl)

        print(self.divider)

    def reveal(self, tile):
        if not tile.number:
            self.reveal_empty_neighbours(tile)
        tile.hidden = False
        return tile

    def reveal_empty_neighbours(self, tile):
        """ Reveal all empty (number=0) tiles adjacent to starting tile `loc` and subsequent unhidden tiles.
            Uses floodfill algorithm.
        """
        if tile.number != 0:
            tile.hidden = False
        if not tile.hidden:
            return

        tile.hidden = False
        for ntile in self.neighbours(tile):
            self.reveal_empty_neighbours(ntile)


class Minesweeper(object):
    start    = time()
    win_msg  = "All mines cleared (%d:%02d)!"
    lose_msg = "KABOOM. END."

    def __init__(self, board):
        self.board = board

    def check_end(self, tile):
        """Check if game is lost (stepped on a mine), or won (all mines found)."""
        if tile.mine and not tile.marked:
            self.game_lost()
        elif self.board.cleared():
            self.game_won()

    def game_lost(self):
        board = self.board
        for tile in board.all_hidden():
            board.reveal(tile)

        board.draw()
        print(self.lose_msg)
        sys.exit()

    def game_won(self):
        elapsed = time() - self.start
        print(self.win_msg % (elapsed/60, elapsed%60))
        sys.exit()
