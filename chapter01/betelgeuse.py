#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint, random
import math

from utils import range1, TextInput, ujoin, first
from board import Board, Loc

size           = 8
player_chars   = 'IX'
ai_players     = 'IX'
ai_players     = 'X'

neutral_char   = 'N'
blank          = '.'
nl             = '\n'
space          = ' '
padding        = 13, 4

pause_time     = 0.5
num_stars      = 6
star_turns     = 5
star_defence   = 0.4
production_rng = 8, 12
send_chance    = 0.4
send_cutoff    = 25
show_ships     = True


class PlayerBase(object):
    """Used as base for all player's stars and fleets as well as Player class itself, to allow for
       making equality checks between all of them.
    """
    def __eq__(self, other):
        return bool(self.char==other.char)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return blank


class Tile(PlayerBase):
    blank = True

    def __init__(self, loc):
        self.loc = loc


class Star(Tile):
    blank = False
    char  = None
    ships = 0
    sep   = ':'

    def __init__(self, loc, num):
        self.loc        = loc
        self.num        = num
        self.production = randint(*production_rng)
        board[loc]      = self

    def __repr__(self):
        data = [self.char or neutral_char, self.num]
        if show_ships or self==betelgeuse.show_ships_player:
            data.append("%s:%s" % (self.production, self.ships))
        return ujoin(data, space)

    def go(self):
        if betelgeuse.turn % star_turns == 0:
            self.ships += self.production if (self in players) else (self.production // 2)


class BetelgeuseBoard(Board):
    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )

    def draw2(self):
        print(nl*5)
        for row in self.board:
            print(ujoin(row, '', tpl=self.tiletpl), nl*4)


class Fleet(PlayerBase):
    conquer_msg = "%s conquers star system #%d"

    def __init__(self, char, origin, star, ships):
        self.char    = char
        self.origin  = origin
        self.star    = star     # target star
        self.ships   = ships
        self.arrival = betelgeuse.turn + round(board.dist(origin.loc, star.loc) / 2)
        origin.ships -= ships

    def __repr__(self):
        eta = self.arrival - betelgeuse.turn
        return "(%s %s %s s:%d, a:%d)" % (self.char, self.origin.num, self.star.num, self.ships, eta)

    def go(self):
        if betelgeuse.turn >= self.arrival:
            if self == self.star : self.land()
            else                 : self.attack()

    def attack(self):
        """Note: need to do checks at the start of loop in case there are no ships in `star`."""
        while True:
            if not self.ships      : self.dismiss(); break
            if not self.star.ships : self.land(conquer=True); break
            loser = self.star if random() > star_defence else self
            loser.ships -= 1

    def land(self, conquer=False):
        # if conquer: print(self.conquer_msg % (self.char, self.star.num))
        self.star.char = self.char
        self.star.ships += self.ships
        self.dismiss()

    def dismiss(self):
        fleets.remove(self)


class Player(PlayerBase):
    def __init__(self, char):
        self.char = char
        self.ai   = bool(char in ai_players)

    def stars(self):
        return [star for star in stars if star==self]

    def send(self, *args):
        fleets.append( Fleet(self.char, *args) )

    def make_random_moves(self):
        moves = [self.random_move(star) for star in self.stars()]
        for cmd in moves:
            if cmd: self.send(*cmd)

    def random_move(self, star):
        def dist(star2): return board.dist(star.loc, star2.loc)

        if random() < send_chance and star.ships >= send_cutoff:
            targets = sorted([s for s in stars if s != self], key=dist)
            if not targets: return None
            ships = randint(star.ships // 2, star.ships)
            return star, first(targets), ships


class Betelgeuse(object):
    winmsg            = "%s has won!"
    turn              = 0
    show_ships_player = 0

    def check_end(self, player):
        pchars = set(sf.char for sf in stars+fleets if sf in players)
        if len(pchars) == 1:
            self.game_won(first(pchars))

    def game_won(self, char):
        board.draw()
        print(nl, self.winmsg % char)
        sys.exit()


class Test(object):
    def run(self):
        self.textinput = TextInput(board, "%hd %hd %d", accept_blank=True)

        while True:
            for player in players:
                betelgeuse.show_ships_player = player if not player.ai else 0
                board.draw()
                player.make_random_moves() if player.ai else self.make_moves(player)
                betelgeuse.check_end(player)

            for x in stars + fleets: x.go()
            betelgeuse.turn += 1

    def make_moves(self, player):
        while True:
            cmd = self.get_move(player)
            if not cmd: break
            player.send(*cmd)
            board.draw()

    def get_move(self, player):
        while True:
            cmd = self.textinput.getinput()
            if not cmd: return

            src, goal, ships = cmd
            src, goal = stars[src], stars[goal]
            if src == player and src.ships >= ships:
                return src, goal, ships
            else:
                print(self.textinput.invalid_move)


if __name__ == "__main__":
    board      = BetelgeuseBoard(size, Tile, padding=padding, pause_time=pause_time)
    betelgeuse = Betelgeuse()
    fleets     = []
    stars      = [Star(board.random_blank(), n) for n in range1(num_stars)]
    players    = [Player(c) for c in player_chars]
    for n, player in enumerate(players):
        stars[n].char = player.char

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
