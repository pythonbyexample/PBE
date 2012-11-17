#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint, random
from time import sleep
import math

from utils import range1, parse_hnuminput, itersplit, ujoin
from board import Board, Loc

size         = 4
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


class CompareChar(object):
    def __eq__(self, other):
        return bool(self.char==other.char)

    def __ne__(self, other):
        return not self.__eq__(other)


class Tile(CompareChar):
    blank = True

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return blank


class Star(Tile):
    blank = False
    owner = None
    ships = 0
    sep   = ':'

    def __init__(self, loc, num):
        self.loc        = loc
        self.num        = num
        self.production = randint(8, 12)
        board[loc]      = self

    def turn(self):
        if betelgeuse.turn % star_turns == 0:
            self.ships += self.production

    def __repr__(self):
        data = [self.owner or neutral_char, self.num, ships]
        if show_ships or self==betelgeuse.show_ships_player:
            data.append(self.production, self.ships)
        return ujoin(data, self.sep)
        # ships = ":%s" % self.ships if display_ships else ''
        # return "%s %s %s" % (self.owner or neutral_char, self.num, ships)


class BetelgeuseBoard(Board):
    def dist(self, *stars):
        l1, l2 = (s.loc for s in stars)
        return math.sqrt( abs( (l2.x - l1.x)**2 + (l2.y - l1.y)**2 ) )

    def random_blank(self):
        return rndchoice( [t.loc for t in self if t.blank] )

    def draw(self):
        print(nl*5)
        for row in self.board:
            print(ujoin(row, '', tpl=self.tiletpl), nl*2)



class Fleet(CompareChar):
    conquer_msg = "%s conquers star system #%d"

    def __init__(self, char, src, goal, ships):
        self.char    = char
        self.src     = src
        self.goal    = goal
        self.ships   = ships
        self.arrival = betelgeuse.turn + round(board.dist(src, goal) / 2)

    def move(self):
        if self.arrival >= betelgeuse.turn:
            if self == self.goal : self.land()
            else                 : self.attack()

    def attack(self):
        while True:
            loser = self.goal if random() > star_defence else self
            loser.ships -= 1
            if not self.ships      : self.die(); break
            if not self.goal.ships : self.land(conquer=True); break

    def land(self, conquer=False):
        if conquer:
            print(self.conquer_msg % (self.owner, self.goal.num))
        self.goal.char = self.char
        self.goal.ships += self.ships
        self.die()

    def __repr__(self):
        eta = self.arrival - betelgeuse.turn
        return "(%s %s %s s:%d, a:%d)" % (self.owner, self.src.num, self.goal.num, self.ships, eta)

    def die(self):
        fleets.remove(self)


class Player(CompareChar):
    def __init__(self, char):
        self.char = char
        self.ai   = bool(char in ai_players)

    def __repr__(self):
        return self.char

    def stars(self):
        return [star for star in stars if star==self]

    def send(self, src, goal, ships):
        fleets.append( Fleet(self, src, goal, ships) )

    def make_random_moves(self):
        moves = [self.random_move(s) for s in self.stars()]
        for cmd in moves:
            if cmd: self.send(*cmd)

    def random_move(self, star):
        def dist(s): return board.dist(star, s)

        if random() < send_chance and star.ships >= send_cutoff:
            targets = sorted([star for star in stars if star != self], key=dist)

            if not targets: return None
            ships = randint(star.ships // 2, star.ships)
            return star, targets[0], ships

    def __repr__(self):
        return self.char


class Betelgeuse(object):
    winmsg            = "%s has won!"
    turn              = 0
    show_ships_player = 0

    def check_end(self, player):
        if len( set(x.owner for x in stars + fleets) ) == 1:
            self.game_won(stars[0].owner)

    def game_won(self, player):
        print(nl, self.winmsg % player)
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
        stars[n].owner = player

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
