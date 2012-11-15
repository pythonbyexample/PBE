#!/usr/bin/env python

# Imports {{{
# Inspired by Flippy game By Al Sweigart http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

from __future__ import division

import sys
import random
import pygame
import logging

from time import time
from logging import debug

from pygame.locals import *

import board as board_module
from board import Board, Piece, Loc, render_text
from settings import *

logging.basicConfig(filename="out.log", level=logging.DEBUG, format="%(message)s")
# }}}

class Tile(object):
    def __init__(self, board, loc=None):
        self.loc = loc
        if loc: board[loc] = self

class Piece(Tile):
    """Black or White playing piece."""
    def __init__(self, colour=None, board=None, loc=None):
        super(Piece, self).__init__(board, loc)
        self.colour = colour

    def __repr__(self):
        return "<%s piece>" % self.colour

    def flip(self):
        self.colour = white if self.colour==black else black

    def is_opposite_of(self, other):
        return isinstance(other, Piece) and self != other

    def __eq__(self, other):
        return bool( self.colour == getattr(other, "colour", -1) )

    def __ne__(self, other):
        return not self.__eq__(other)


class Blank(Tile):
    def __repr__(self):
        return "<blank>"


class VersiBoard(Board):
    def __init__(self, size, def_tile):
        super(VersiBoard, self).__init__(size, def_tile)
        Piece(white, self, Loc(3,3))
        Piece(white, self, Loc(4,4))
        Piece(black, self, Loc(3,4))
        Piece(black, self, Loc(4,3))

    def is_valid_move(self, piece, loc):
        return bool( self.get_captured(piece, loc) )

    def get_captured(self, piece, start_loc):
        """If `start_loc` is a valid move, returns a list of locations of captured pieces."""
        if isinstance(self[start_loc], Piece):
            return []
        captured = []

        # check each of the eight directions
        for dir in self.dirlist2:
            templist = []
            loc      = self.nextloc(loc, dir)

            # keep adding locations as long as it's an enemy piece
            while self.valid(loc) and piece.is_opposite_of(self[loc]):
                templist.append(loc)
                loc = self.nextloc(loc, dir)

            # if reached end of board or next tile is not our piece, skip to next direction
            if not self.valid(loc) or self[loc] != piece:
                continue
            captured.extend(templist)
        return captured

    def get_valid_moves(self, piece):
        return [loc for loc in self if self.is_valid_move(piece, loc)]

    def get_score(self, player, computer):
        """Return a tuple of (player_score, computer_score)."""
        return sum( tile == player.piece for tile in self ), \
               sum( tile == computer.piece for tile in self )

    def is_corner(self, loc):
        return loc.x in (0, self.maxx) and loc.y in (0, self.maxy)


class PlayerAI(object):
    """Parent class for live and computer players."""
    def __init__(self, piece):
        self.piece = piece

    def make_move(self, loc):
        """Place new piece at `loc`, return list of captured locations."""
        captured = board.get_captured(self.piece, loc)
        piece = Piece(self.piece.colour, board, loc)
        for loc in captured: board[loc].flip()
        return captured


class Player(PlayerAI):
    newgame = hints = None      # buttons


class Computer(PlayerAI):
    def turn(self):
        """Return Location of best move."""
        possible_moves = board.get_valid_moves(self.piece)
        random.shuffle(possible_moves)

        for loc in possible_moves:
            if board.is_corner(loc): return loc

        # go through possible moves and remember the best scoring move
        score = -1
        for loc in possible_moves:
            captured = len(board.get_captured(self.piece, loc))
            if captured > score:
                score = captured
                best_move = loc
        return best_move


class Reversi(object):
    def run_game(self):
        """Display board, start the game, process moves; return True to start a new game, False to exit."""
        board.draw()
        valid_moves = board.get_valid_moves
        player      = random.choice(players)

        while True:
            board.draw()
            if player.manual:
                player.make_move(self.get_move())
                if   valid_moves(player.enemy().piece) : player = player.enemy()
                elif not valid_moves(player.piece)     : break

            else:
                player.make_move(player.get_random_move())

                # give next turn to player OR keep the turn OR end game if no turns left
                if   valid_moves(player.enemy().piece) : player = player.enemy()
                elif not valid_moves(player.piece)     : break



    def draw_info(self):
        """Draws scores and whose turn it is at the bottom of the screen."""
        scores = board.get_score(players)
        tpl    = "%s Score: %s    %s Score: %s"
        print(tpl % (players[0], players[1], scores[0], scores[1]))

    def results_message(self):
        """Display win/lose results message."""
        scores = board.get_score(players)
        text   = "The game was a tie!"
        print(text)


if __name__ == "__main__":
    reversi = Reversi()
    board   = Board()
    reversi.main()
