#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint, random
from time import sleep
import math

from utils import range1, parse_hnuminput, itersplit, ujoin, first
from board import Board, Loc

size         = 8
player_chars = 'IX'
ai_players   = 'X'
ai_players   = 'IX'

pause_time   = 0.5
num_stars    = 6
star_turns   = 5
star_defence = 0.4
send_chance  = 0.4
send_cutoff  = 25
show_ships   = True

nl           = '\n'
space        = ' '
blank        = '.'
prompt       = '> '
quit_key     = 'q'
divchar      = '-'
tiletpl      = '%14s'
neutral_char = 'N'


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
        self.production = randint(8, 12)
        board[loc]      = self

    def turn(self):
        if betelgeuse.turn % star_turns == 0:
            self.ships += self.production if (self in players) else (self.production // 2)

    def __repr__(self):
        data = [self.char or neutral_char, self.num]
        if show_ships or self==betelgeuse.show_ships_player:
            data.append("%s:%s" % (self.production, self.ships))
        return ujoin(data, space)


class BetelgeuseBoard(Board):
    def dist(self, *stars):
        l1, l2 = (s.loc for s in stars)
        return math.sqrt( abs(l2.x - l1.x)**2 + abs(l2.y - l1.y)**2  )

    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )

    def draw(self):
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
        self.arrival = betelgeuse.turn + round(board.dist(origin, star) / 2)
        origin.ships -= ships

    def move(self):
        if betelgeuse.turn >= self.arrival:
            if self == self.star : self.land()
            else                 : self.attack()

    def attack(self):
        """Note: need to do checks at the start of loop in case there are no ships in `star`."""
        while True:
            if not self.ships      : self.die(); break
            if not self.star.ships : self.land(conquer=True); break
            loser = self.star if random() > star_defence else self
            loser.ships -= 1

    def land(self, conquer=False):
        if conquer:
            print(self.conquer_msg % (self.char, self.star.num))
        self.star.char = self.char
        self.star.ships += self.ships
        self.die()

    def __repr__(self):
        eta = self.arrival - betelgeuse.turn
        return "(%s %s %s s:%d, a:%d)" % (self.char, self.origin.num, self.star.num, self.ships, eta)

    def die(self):
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
        def dist(star2): return board.dist(star, star2)

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
    invalid_inp  = "Invalid input"
    invalid_move = "Invalid move... try again"
    stat_div     = " | "

    def run(self):
        while True:
            for player in players:
                betelgeuse.show_ships_player = player if not player.ai else 0
                board.draw()
                print(ujoin( (f for f in fleets), self.stat_div ))
                print(ujoin( ("%s:%d" % (s, s.ships) for s in stars), self.stat_div ))

                player.make_random_moves() if player.ai else self.make_moves()

                for star in stars: star.turn()
                for fleet in fleets: fleet.move()

                betelgeuse.check_end(player)
                sleep(pause_time)

            betelgeuse.turn += 1

    def make_moves(self, player):
        while True:
            cmd = self.get_move(player)
            if not cmd: break
            player.send(*cmd)

    def get_move(self, player):
        while True:
            try:
                inp = raw_input(prompt).strip()
                if inp == quit_key: sys.exit()
                if not inp: return

                cmd       = inp.split() if space in inp else inp
                src, goal = parse_hnuminput(cmd[:2])
                ships     = int(cmd[2])

                if star[src].ships >= ships:
                    return stars[src], stars[goal], ships
            except (IndexError, ValueError, TypeError, KeyError):
                print(self.invalid_inp)
                continue


if __name__ == "__main__":
    board      = BetelgeuseBoard(size, Tile, tiletpl=tiletpl)
    betelgeuse = Betelgeuse()
    fleets     = []
    stars      = [Star(board.random_blank(), n) for n in range1(num_stars)]
    players    = [Player(c) for c in player_chars]
    for n, player in enumerate(players):
        stars[n].char = player.char

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
