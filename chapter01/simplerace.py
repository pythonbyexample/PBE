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
ai_run = 1
track  = [blank]*size


class Tile(object):
    def __repr__(self):
        return self.char

class Blank(Tile):
    colour = None
    char   = blank

class Piece(Tile):
    loc    = None
    done   = False
    colour = None
    black  = white = False

    def __init__(self, colour):
        setattr(self, colour, True)
        self.colour = colour
        self.char   = colour[0]

    def move(self, loc):
        track[self.loc] = Blank()
        if loc > len(track) - 1:
            self.done = True
        else:
            track[loc] = self


class SimpleRace(object):
    prompt = "> "
    winmsg = "%s won the race!"

    def draw(self):
        print(joins(track))

    def run(self):
        white = Piece(cwhite), Piece(cwhite)
        black = Piece(cblack), Piece(cblack)
        turns = cycle( rndchoice((white, black), (black, white)) )
        dice  = Dice(num=1)

        while True:
            player  = turns.next()
            move    = dice.rollsum()
            newlocs = [(piece, piece.loc + move) for piece in player]
            valid   = [(p, loc) for p, loc in newlocs if track[loc].colour != p.colour]
            if valid:
                piece, loc = rndchoice(valid)
                piece.move(loc)

    def check_end(self, player):
        if all(p.done for p in player):
            self.game_won(player)

    def game_won(self, player):
        print(self.winmsg % player)



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
    SimpleRace().run()
