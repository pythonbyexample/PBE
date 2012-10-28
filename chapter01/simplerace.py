#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import sleep
from itertools import cycle
from operator import itemgetter

from utils import Dice, joins, itersplit, enumerate1

size          = 20
cgreen        = "green"
cblue         = "blue"
manual_player = cgreen
manual_player = 0
blank         = '.'
space         = ' '
nl            = '\n'
tiletpl       = "%3s"
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
    winmsg = "%s wins the race!\n"

    def __init__(self):
        green        = Piece(cgreen), Piece(cgreen)
        blue         = Piece(cblue), Piece(cblue)
        self.players = rndchoice( [(green, blue), (blue, green)] )
        self.dice    = Dice(num=1)

    def draw(self):
        print(nl*5)
        print(''.join( tiletpl % (n+1) for n in range(len(track)) ))
        print(''.join( tiletpl % t for t in track ))

    def valid(self, piece, loc):
        """Valid move: any move that does not land on your other piece (beyond track is ok)."""
        return bool(loc > len(track)-1 or track[loc].colour != piece.colour)

    def valid_moves(self, player, move):
        """Valid moves for `player`: return tuples (piece, newloc) for each piece belonging to `player`."""
        def at_start(piece_newloc):
            return bool(piece_newloc[0].loc == -1)

        moves = [(p, p.loc+move) for p in player if not p.done and self.valid(p, p.loc+move)]
        start, other = itersplit(moves, at_start)
        moves = start[:1] + other
        return sorted(moves, key=itemgetter(1))

    def is_manual(self, player):
        return bool(player[0].colour == manual_player)

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
        if manual_player:
            print("You are playing:", manual_player)

        while True:
            for player in race.players:
                race.draw()
                movedist    = race.dice.rollsum()
                valid_moves = race.valid_moves(player, movedist)

                if valid_moves:
                    if race.is_manual(player) and len(valid_moves) > 1:
                        piece, loc = self.manual_move(valid_moves)
                    else:
                        piece, loc = rndchoice(valid_moves)

                    piece.move(loc)
                    race.check_end(player)
                sleep(pause_time)

    def manual_move(self, valid_moves):
        """Get player's choice of move options."""
        moves = [space*3] * 26
        for n, (_, loc) in enumerate1(valid_moves):
            moves[loc] = tiletpl % n
        print(''.join(moves))

        while True:
            try:
                inp = int(raw_input(self.prompt)) - 1
                return valid_moves[inp]
            except (IndexError, ValueError):
                pass


if __name__ == "__main__":
    track = [Blank() for _ in range(size)]
    race  = SimpleRace()
    try: Test().run()
    except KeyboardInterrupt: pass
