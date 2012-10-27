#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import sleep
from itertools import cycle

from utils import Dice, joins

size          = 20
cwhite        = "white"
cblack        = "black"
blank         = '.'
space         = ' '
nl            = '\n'
manual_player = 0
pause_time    = 1       # in seconds


class Tile(object):
    colour = None

    def __repr__(self):
        return self.char

class Blank(Tile):
    char = blank

class Piece(Tile):
    loc  = -1
    done = False

    def __init__(self, colour):
        self.colour = colour
        self.char   = colour[0]

    def move(self, loc):
        """Move to location `loc`, if moved past the end, set `done` property."""
        track[self.loc] = Blank()
        if loc > len(track) - 1:
            self.done = True
        else:
            if track[loc].colour:
                track[loc].loc = -1     # bump enemy piece back to start
            track[loc] = self
            self.loc = loc


class SimpleRace(object):
    winmsg = "%s wins the race!"

    def __init__(self):
        white        = Piece(cwhite), Piece(cwhite)
        black        = Piece(cblack), Piece(cblack)
        self.players = rndchoice( [(white, black), (black, white)] )
        self.dice    = Dice(num=1)

    def draw(self):
        print( ''.join( "%3s" % (n+1) for n in range(len(track)) ) )
        print(space, joins(track, space*2), nl*5)

    def valid(self, piece, loc):
        """Valid move: any move that does not land on your other piece (beyond track is ok)."""
        return bool(loc > len(track)-1 or track[loc] != piece.colour)

    def valid_moves(self, player, move):
        """Valid moves for `player`: return tuples (piece, newloc) for each piece belonging to `player`."""
        moves = [(p, p.loc+move) for p in player if not p.done and self.valid(p, p.loc+move)]

    def check_end(self, player):
        """Check if `player` has won the game."""
        if all(piece.done for piece in player):
            self.game_won(player)

    def game_won(self, player):
        print(self.winmsg % player[0].colour)
        sys.exit()


class Test(object):
    prompt = "> "

    def run(self):
        while True:
            for n, player in enumerate(race.players):
                race.draw()
                movedist    = race.dice.rollsum()
                valid_moves = race.valid_moves(player, movedist)

                if valid_moves:
                    if n == manual_player and len(valid_moves) > 1:
                        piece, loc = self.manual_move(valid_moves)
                    else:
                        piece, loc = rndchoice(valid_moves)

                    piece.move(loc)
                    race.check_end(player)
                sleep(pause_time)

    def manual_move(self, valid_moves):
        """Get player's choice of move options."""
        moves = ["%d) loc %d to %d" % (n+1, p.loc, move) for n, (p, move) in enumerate(valid_moves)]
        prompt = nl.join(moves + [self.prompt])

        while True:
            try:
                inp = int(raw_input(prompt)) - 1
                return valid_moves[inp]
            except IndexError, ValueError:
                pass


if __name__ == "__main__":
    track = [Blank() for _ in range(size)]
    race  = SimpleRace()
    Test().run()
