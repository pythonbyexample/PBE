#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from time import sleep
from itertools import cycle

from utils import TextInput, AttrToggles, enumerate1, range1, ujoin, flatten, nextval, first, space, nl
from board import Board, Loc, BaseTile

size       = 5, 5
num_ships  = 3
pause_time = 0.1

blank      = '.'
shipchar   = '#'
sunkship   = '%'
hitchar    = '*'
padding    = 2, 1

players    = [1, 2]
ai_players = [1, 2]
divider    = '-' * (size[0] * 4 + 6)


class Tile(BaseTile, AttrToggles):
    """Tile that may be a ship or blank space (water)."""
    ship              = False
    is_hit            = False
    hidden            = True
    revealed          = False
    attribute_toggles = [("hidden", "revealed")]

    def __repr__(self):
        return blank if self.hidden else self.char

    def hit(self):
        self.is_hit   = True
        self.revealed = True
        self.char     = sunkship if self.ship else hitchar


class Blank(Tile) : char = blank
class Ship(Tile)  : char = shipchar


class BattleshipBoard(Board):
    def random_blank(self) : return rndchoice(self.tiles_not("ship"))
    def random_unhit(self) : return rndchoice(self.tiles_not("is_hit"))

    def next_validloc(self, start, dir, n):
        loc = self.nextloc(start, dir, n)
        if loc and not any(t.ship for t in self.cross_neighbours(loc)):
            return loc

    def random_placement(self, ship):
        """Return list of random locations for `ship` length."""
        while True:
            start = self.random_blank()
            dir   = rndchoice(self.dirlist)
            locs  = [ self.next_validloc(start, dir, n) for n in range(ship) ]
            if all(locs): break

        return locs


class Player(object):
    def __init__(self, num):
        """Create player's board and randomly place `num_ships` ships on it."""
        self.num   = num
        self.ai    = bool(num in ai_players)
        B          = BattleshipBoard(size, Blank, num_grid=True, padding=padding, pause_time=0, screen_sep=0)
        self.board = B

        for ship in range1(num_ships):
            for loc in B.random_placement(ship):
                B[loc] = Ship(loc)

        if not self.ai:
            for tile in B: tile.revealed = True

    def enemy(self): return nextval(players, self)


class Battleship(object):
    losemsg = "All ships are sunk! Player %s loses the game!"

    def draw(self):
        p1, p2 = players
        print(nl*5)
        p1.board.draw()
        print(divider)
        p2.board.draw()
        sleep(pause_time)

    def check_end(self, player):
        if all(ship.is_hit for ship in player.board.tiles("ship")):
            self.draw()
            print(self.losemsg % player.num)
            sys.exit()


class Test(object):
    def run(self):
        # board is only used to check if location is within range (using board.valid())
        self.textinput = TextInput( board=first(players).board )

        for player in cycle(players):
            bship.draw()
            tile = self.ai_move(player) if player.ai else self.get_move(player)
            tile.hit()
            bship.check_end(player.enemy())

    def get_move(self, player):
        """Get user command and return the tile to attack."""
        return player.enemy().board[ self.textinput.getloc() ]

    def ai_move(self, player):
        """Very primitive 'AI', always hits a random location."""
        return player.enemy().board.random_unhit()


if __name__ == "__main__":
    players = [Player(p) for p in players]
    bship   = Battleship()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
