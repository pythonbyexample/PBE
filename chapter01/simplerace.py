#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from random import shuffle
from time import sleep
from itertools import cycle

from utils import Dice, TextInput, ujoin, nextval, lastind, first, enumerate1, getitem, nl, space

size         = 20
num_pieces   = 3
blank        = '.'
pause_time   = 0.5     # in seconds
player_chars = 'gb'
ai_players   = 'b'


class Tile(object):
    char = blank

    def __repr__(self):
        return self.char


class Piece(Tile):
    loc  = -1
    done = False

    def __init__(self, char):
        self.char = char

    def move(self, loc):
        """Move to location `loc`, if moved past the end, set `done` property."""
        track[self.loc] = Tile()

        if loc > lastind(track):
            self.done = True
        else:
            if track[loc].char is not blank:
                track[loc].loc = -1     # bump enemy piece back to start
            track[loc] = self

        self.loc = loc


class SimpleRace(object):
    winmsg = "\n'%s' wins the race!"

    def __init__(self):
        """ Create pieces; create list of players with one or the other being the first to move;
            create dice object.
        """
        self.dice = Dice(num=1)     # one 6-sided dice
        shuffle(players)

    def draw(self):
        """Display the racing track."""
        print(nl*5 + ujoin(track))

    def valid(self, piece, loc):
        """Valid move: any move that does not land on your other piece (beyond track is ok)."""
        return bool(loc > lastind(track) or track[loc].char != piece.char)

    def valid_moves(self, player, move):
        """ Valid moves for `player`: return tuples (piece, newloc) for each piece belonging to `player`.

            Note: when more than one piece are at the start, we need to avoid giving the player
            choice between two identical moves, so we need to convert the list of tuples to a dict which
            gets rid of duplicate keys (locations) and then convert back to a list using `items()`
            method.
            We also need to sort `moves` by location because looks better to the user when moves
            are sorted in order from left to right.
        """
        moves = [(p.loc+move, p) for p in player if not p.done and self.valid(p, p.loc+move)]
        return sorted( dict(moves).items() )

    def check_end(self, player):
        """Check if `player` has won the game."""
        if all(piece.done for piece in player):
            self.game_won(player)

    def game_won(self, player):
        self.draw()
        print(self.winmsg % player)
        sys.exit()


class Player(object):
    def __init__(self, char):
        self.char   = char
        self.ai     = char in ai_players
        self.pieces = [Piece(char) for _ in range(num_pieces)]

    def __repr__(self):
        return self.char

    def __iter__(self):
        return iter(self.pieces)


class Test(object):

    def run(self):
        """ Run main game loop.

            If more than one valid move is available to the human player, let him make the choice
            with `get_move()`.
        """
        def offer_choice(): return bool(not player.ai and len(valid_moves) > 1)

        self.textinput = TextInput('%hd')
        player = first(players)

        if ai_players and player.char not in ai_players:
            print("You are playing:", player)

        for player in cycle(players):
            race.draw()
            movedist    = race.dice.rollsum()
            valid_moves = race.valid_moves(player, movedist)

            if valid_moves:
                getmove = self.get_move if offer_choice() else rndchoice
                loc, piece = getmove(valid_moves)
                piece.move(loc)
                race.check_end(player)
            sleep(pause_time)

    def get_move(self, valid_moves):
        """Get player's choice of available moves."""
        moves = [space] * (size + 6)
        for n, (loc, _) in enumerate1(valid_moves):
            moves[loc] = n
        print(ujoin(moves))

        while True:
            move = getitem(valid_moves, self.textinput.getval())
            if move is None : print(self.textinput.invalid_move)
            else            : return move


if __name__ == "__main__":
    track   = [Tile() for _ in range(size)]
    players = [Player(c) for c in player_chars]
    race    = SimpleRace()
    try: Test().run()
    except KeyboardInterrupt: pass
