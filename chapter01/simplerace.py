#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import sleep
from itertools import cycle

from utils import Dice, joins

size   = 20
cwhite = "white"
cblack = "black"
blank  = '.'
nl     = '\n'
ai_run = 1


class Tile(object):
    def __repr__(self):
        return self.char

class Blank(Tile):
    colour = None
    char   = blank

class Piece(Tile):
    loc    = -1
    done   = False
    colour = None
    black  = white = False

    def __init__(self, colour):
        setattr(self, colour, True)
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
    winmsg = "%s won the race!"

    def __init__(self):
        white      = Piece(cwhite), Piece(cwhite)
        black      = Piece(cblack), Piece(cblack)
        self.turns = cycle( rndchoice( [(white, black), (black, white)] ) )
        self.dice  = Dice(num=1)

    def draw(self):
        print(joins(track), nl*5)

    def valid(self, piece, loc):
        """Valid move: any move that does not land on your other piece (beyond track is ok)."""
        return bool(loc > len(track) - 1 or track[loc] != piece.colour)

    def valid_moves(self, player, movedist):
        newlocs = [(piece, piece.loc + movedist) for piece in player if not piece.done]
        return [(p, loc) for p, loc in newlocs if self.valid(p, loc)]

    def check_end(self, player):
        if all(p.done for p in player):
            self.game_won(player)

    def game_won(self, player):
        print(self.winmsg % player[0].colour)
        sys.exit()


class Test(object):
    prompt = "> "

    def run(self):
        while True:
            race.draw()
            player      = race.turns.next()
            movedist    = race.dice.rollsum()
            valid_moves = race.valid_moves(player, movedist)

            if valid:
                piece, loc = rndchoice(valid_moves)
                piece.move(loc)
                race.check_end(player)
            sleep(0.6)

    def manual_move(self):
        """Get user command and mark mine or reveal a location; check if game is won/lost."""
        inp = raw_input(self.prompt)
        if inp == 'q': sys.exit()

        mark = inp.startswith('m')
        x, y = inp[-2], inp[-1]
        loc  = Loc( int(x)-1, int(y)-1 )
        tile = board[loc]

        tile.toggle_mark() if mark else board.reveal(tile)
        msweep.check_end(tile)

    def ai_move(self):
        """Very primitive `AI', does not mark mines & does not try to avoid them."""
        loc = board.random_hidden().loc

        while loc.x:
            print("\n loc", loc.x+1, loc.y+1); print()
            msweep.check_end( board.reveal(board[loc]) )
            loc = loc.moved(-1, 0)      # move location to the left
            board.draw()
            sleep(0.4)


if __name__ == "__main__":
    track = [Blank() for _ in range(size)]
    race  = SimpleRace()
    Test().run()
