#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from random import shuffle
from time import sleep

from utils import Dice, ujoin, nextval

size       = 20
num_pieces = 3
blank      = '.'
space      = ' '
quit_key   = 'q'
nl         = '\n'
pause_time = 0.5     # in seconds

players    = 'gb'
ai_players = 'gb'


class Tile(object):
    def __repr__(self):
        return self.char

class Blank(Tile):
    char = blank

class Piece(Tile):
    loc  = -1
    done = False

    def __init__(self, char):
        self.char = char

    def move(self, loc):
        """Move to location `loc`, if moved past the end, set `done` property."""
        track[self.loc] = Blank()
        if loc > len(track) - 1:
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
        self.players = [[Piece(p) for _ in range(num_pieces)] for p in players]
        self.dice    = Dice(num=1)      # one 6-sided dice
        shuffle(self.players)

    def draw(self):
        """Display the racing track."""
        print(nl*5 + ujoin(track))

    def valid(self, piece, loc):
        """Valid move: any move that does not land on your other piece (beyond track is ok)."""
        return bool(loc > len(track)-1 or track[loc].char != piece.char)

    def valid_moves(self, player, move):
        """ Valid moves for `player`: return tuples (piece, newloc) for each piece belonging to `player`.

            Note: when more than one piece are at the start, we need to avoid giving the player
            choice between two identical moves, so we need to convert the list of tuples to a dict which
            gets rid of duplicate keys (locations) and then convert back to a list using `items()`
            method.
            We also need to sort `moves` by location because this looks better to the
            user when choices are shown in `get_move()`.
        """
        moves = [(p.loc+move, p) for p in player if not p.done and self.valid(p, p.loc+move)]
        return sorted( dict(moves).items() )

    def is_ai(self, player):
        return bool(player[0].char in ai_players)

    def check_end(self, player):
        """Check if `player` has won the game."""
        if all(piece.done for piece in player):
            self.game_won(player)

    def game_won(self, player):
        self.draw()
        print(self.winmsg % player[0].char)
        sys.exit()


class Test(object):
    prompt = "> "

    def offer_choice(self, player, valid_moves):
        return bool(not race.is_ai(player) and len(valid_moves) > 1)

    def run(self):
        """ Run main game loop.

            If more than one valid move is available to the human player, let him make the choice
            with `get_move()`.
        """
        player = race.players[0][0].char
        if ai_players and player not in ai_players:
            print("You are playing:", player)

        while True:
            for player in race.players:
                race.draw()
                movedist    = race.dice.rollsum()
                valid_moves = race.valid_moves(player, movedist)

                if valid_moves:
                    getmove = self.get_move if self.offer_choice(player, valid_moves) else rndchoice
                    loc, piece = getmove(valid_moves)
                    piece.move(loc)
                    race.check_end(player)
                sleep(pause_time)

    def get_move(self, valid_moves):
        """Get player's choice of move options."""
        moves = [space] * 26
        for n, (loc, _) in enumerate(valid_moves):
            moves[loc] = n + 1
        print(ujoin(moves))

        while True:
            try:
                inp = raw_input(self.prompt)
                if inp==quit_key: sys.exit()
                return valid_moves[int(inp)-1]
            except (IndexError, ValueError):
                pass


if __name__ == "__main__":
    track = [Blank() for _ in range(size)]
    race  = SimpleRace()
    try: Test().run()
    except KeyboardInterrupt: pass
