#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as rndchoice
from random import randint, random

from utils import range1, TextInput, sjoin, first, space, nl
from board import Board, BaseTile

size           = 8, 6
player_chars   = '⎔▣'
ai_players     = '⎔▣'
ai_players     = '⎔'

neutral_char   = '⊛'
blank          = '.'
padding        = 13, 4

pause_time     = 0.3
num_stars      = 6
show_ships     = True   # show production and # of ships for all stars

star_turns     = 5      # star production cycle
star_defence   = 0.6    # star defense rating: degree of advantage for defenders, must be less than 1.0
production_rng = 8, 12  # range of star production, ships per cycle
send_chance    = 0.4    # chance of sending a fleet, used by AI
send_cutoff    = 25     # only send a fleet if have >=N, used by AI


class PlayerBase(object):
    """Used as base for all player's stars and fleets as well as Player class itself, to allow for
       making equality checks between all of them.
    """
    def __eq__(self, other) : return bool(self.char == other.char)
    def __ne__(self, other) : return bool(self.char != other.char)
    def __repr__(self)      : return self.char


class Tile(BaseTile, PlayerBase) : blank = star = False
class Blank(Tile)                : char = blank

class Star(Blank):
    char  = neutral_char
    ships = 0

    def __init__(self, loc, num):
        super(Star, self).__init__(loc)
        self.num        = num
        self.production = randint(*production_rng)
        board[loc]      = self

    def __repr__(self):
        data = [self.char, self.num]
        if show_ships or self == betelgeuse.show_ships_player:
            data.append("%s:%s" % (self.production, self.ships))
        return sjoin(data, space)

    def go(self):
        if betelgeuse.turn % star_turns == 0:
            self.ships += self.production if (self in players) else (self.production // 2)


class BetelgeuseBoard(Board):
    stat = "turn: %d"

    def random_blank(self) : return rndchoice(self.locations("blank"))
    def status(self)       : print(self.stat % betelgeuse.turn)


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

    def stars(self)       : return [s for s in stars if s==self]
    def other_stars(self) : return [s for s in stars if s!=self]

    def send(self, *args):
        fleets.append( Fleet(self.char, *args) )

    def make_random_moves(self):
        moves = [self.random_move(star) for star in self.stars()]
        for move in moves:
            if move: self.send(*move)

    def random_move(self, star):
        def dist(star2): return board.dist(star, star2)

        if random() < send_chance and star.ships >= send_cutoff:
            targets = sorted(self.other_stars(), key=dist)
            if not targets: return None

            ships = randint(star.ships // 2, star.ships)
            return star, first(targets), ships


class Betelgeuse(object):
    winmsg            = "Player %s wins!"
    turn              = 1
    show_ships_player = None

    def check_end(self):
        pchars = set(sf.char for sf in stars+fleets if sf.char != neutral_char)

        if len(pchars) == 1:
            board.draw()
            print(nl, self.winmsg % first(pchars))
            sys.exit()


class BasicInterface(object):
    def run(self):
        self.textinput = TextInput("%hd %hd %d", board, accept_blank=True)

        while True:
            for player in players:
                betelgeuse.show_ships_player = None if player.ai else player
                board.draw()
                player.make_random_moves() if player.ai else self.make_moves(player)
                betelgeuse.check_end()

            for sf in stars + fleets: sf.go()
            betelgeuse.turn += 1

    def make_moves(self, player):
        while True:
            cmd = self.get_move(player)
            if not cmd: break
            player.send(*cmd)
            board.draw()

    def get_move(self, player):
        while True:
            try:
                return self._get_move(player)
            except (IndexError, AssertionError):
                print(self.textinput.invalid_move)

    def _get_move(self, player):
        cmd = self.textinput.getinput()
        if not cmd: return

        src, goal, ships = cmd
        src, goal = stars[src], stars[goal]
        assert src == player and src.ships >= ships
        return src, goal, ships


if __name__ == "__main__":
    board      = BetelgeuseBoard(size, Blank, padding=padding, pause_time=pause_time)
    betelgeuse = Betelgeuse()
    fleets     = []
    stars      = [Star(board.random_blank(), n) for n in range1(num_stars)]
    players    = [Player(c) for c in player_chars]

    for n, player in enumerate(players):
        stars[n].char = player.char

    try: BasicInterface().run()
    except KeyboardInterrupt: sys.exit()
