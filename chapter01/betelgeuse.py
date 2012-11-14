#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint, random
from time import sleep
import math

from utils import range1, parse_hnuminput, itersplit
from board import Board, Loc

size           = 4
player_chars   = ['O', 'X']
manual_players = ['O']
manual_players = []

pause_time     = 0.2
num_stars      = 6
star_turns     = 5
star_defence   = 0.4
send_chance    = 0.4
send_cutoff    = 25

nl             = '\n'
space          = ' '
blank          = '.'
prompt         = '> '
quit_key       = 'q'
divchar        = '-'
tiletpl        = "%5s"


class Tile(object):
    blank = True

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return blank


class Star(Tile):
    blank = False
    owner = None
    ships = 0

    def __init__(self, loc, num):
        self.loc        = loc
        self.num        = num
        self.production = randint(8, 12)
        board[loc]      = self

    def turn(self):
        if betelgeuse.turn % star_turns == 0:
            self.ships += self.production

    def __repr__(self):
        return "%s %s :%d" % (self.owner or space, self.num, self.ships)


class BetelgeuseBoard(Board):
    def dist(self, star1, star2):
        x1, y1 = star1.loc
        x2, y2 = star2.loc
        return math.sqrt(abs( (x2-x1)**2 - (y2-y1)**2 ))

    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )


class Fleet(object):
    conquer_msg = "%s conquers star system #%d"

    def __init__(self, player, src, target, ships):
        self.owner  = player
        self.src     = src
        self.target  = target
        self.ships   = ships
        self.arrival = betelgeuse.turn + round(board.dist(src, target) / 2)

    def move(self):
        if self.arrival >= betelgeuse.turn:
            if self.owner==self.target.owner : self.join()
            else                             : self.attack()

    def attack(self):
        while True:
            loser = self.target if random() > star_defence else self
            loser.ships -= 1
            if not self.ships        : self.die(); break
            if not self.target.ships : self.conquer(); break

    def join(self):
        self.target.ships += self.ships
        self.die()

    def conquer(self):
        print(self.conquer_msg % (self.owner, self.target.num))
        self.target.owner = self.owner
        self.target.ships += self.ships
        self.die()

    def die(self):
        fleets.remove(self)


class Player(object):
    def __init__(self, char):
        self.char   = char
        self.manual = bool(char in manual_players)

    def stars(self):
        return [s for s in stars if s.owner==self]

    def send(self, src, target, ships):
        fleets.append( Fleet(self, src, target, ships) )

    def make_random_moves(self):
        moves = [self.random_move(s) for s in self.stars()]
        return [m for m in moves if m]
        for cmd in moves:
            if cmd: self.send(*cmd)

    def random_move(self, star):
        def mystar(star): return star.owner==self
        def dist(s): return board.dist(star, s)

        if random() < send_chance and star.ships >= send_cutoff:
            targets = [s for s in stars if s.owner != self]
            targets.sort(key=dist)

            if not targets: return None
            ships = randint(star.ships/2, star.ships)
            return star, targets[0], ships

    def __repr__(self):
        return self.char


class Betelgeuse(object):
    winmsg = "%s has won!"
    turn   = 0

    def check_end(self, player):
        if len( set(x.owner for x in stars + fleets) ) == 1:
            self.game_won(stars[0].player)

    def game_won(self, player):
        print(nl, self.winmsg % player)
        sys.exit()


class Test(object):
    invalid_inp  = "Invalid input"
    invalid_move = "Invalid move... try again"

    def run(self):
        while True:
            for p in players:
                board.draw()

                if p.manual : self.make_moves()
                else        : p.make_random_moves()

                for star in stars: star.turn()
                for fleet in fleets: fleet.move()

                betelgeuse.check_end(p)
                betelgeuse.turn += 1
                sleep(pause_time)

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

                cmd         = inp.split() if space in inp else inp
                src, target = parse_hnuminput(cmd[:2])
                ships       = int(cmd[2])

                if star[src].ships >= ships:
                    return stars[src], stars[target], ships
            except (IndexError, ValueError, TypeError, KeyError):
                print(self.invalid_inp)
                continue


if __name__ == "__main__":
    board      = BetelgeuseBoard(size, Tile, tiletpl=tiletpl)
    betelgeuse = Betelgeuse()
    fleets     = []
    players    = []
    stars      = [Star(board.random_blank(), n) for n in range1(num_stars)]

    for n, char in enumerate(player_chars):
        player = Player(char)
        stars[n].owner = player
        players.append(player)

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
