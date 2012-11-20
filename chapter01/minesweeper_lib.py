#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import time

from utils import ujoin, range1, enumerate1, timefmt, AttrToggles
from board import Loc, Board

space      = ' '
blank      = ' '
hiddenchar = '.'
minechar   = '*'
nl         = '\n'
tiletpl    = '%3s'


class Tile(AttrToggles):
    hidden            = True
    revealed          = False
    mine              = False
    marked            = False
    number            = 0
    attribute_toggles = [("hidden", "revealed")]

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        if self.marked   : return minechar
        elif self.hidden : return hiddenchar
        elif self.mine   : return minechar
        else             : return str(self.number or blank)

    def toggle_mark(self):
        """UNUSED Toggle 'mine' mark on/off."""
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
        return bool(tile.revealed or tile.mine and tile.marked)

    def cleared(self):
        """All mines defused?"""
        return all( self.marked_or_revealed(tile) for tile in self )

    def random_hidden(self):
        return rndchoice( [tile for tile in self if tile.hidden] )

    def random_empty(self):
        return rndchoice( [tile for tile in self if not tile.mine] )

    def draw(self):
        print(space*3, ujoin( range1(self.width), space, tiletpl ), nl)

        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, space, tiletpl), nl)
        print(self.divider)

    def reveal(self, tile):
        """Unhide `tile`."""
        if not tile.number:
            self.reveal_empty_neighbours(tile)
        tile.revealed = True
        return tile

    def reveal_empty_neighbours(self, tile):
        """ Reveal all empty (number=0) tiles adjacent to starting tile `loc` and subsequent unhidden tiles.
            Uses floodfill algorithm.
        """
        if tile.number   : tile.revealed = True
        if tile.revealed : return

        tile.revealed = True
        for ntile in self.neighbours(tile):
            self.reveal_empty_neighbours(ntile)


class Minesweeper(object):
    start    = time()
    win_msg  = "All mines cleared! (%s)"
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
        for tile in board: board.reveal(tile)

        board.draw()
        print(self.lose_msg)
        sys.exit()

    def game_won(self):
        print( self.win_msg % timefmt(time() - self.start) )
        sys.exit()
