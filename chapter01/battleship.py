#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from time import sleep
from itertools import cycle

from utils import enumerate1, range1, parse_hnuminput, ujoin, flatten, AttrToggles, nextval
from board import Board, Loc

size       = 5, 5
num_ships  = 3
pause_time = 0.1

nl         = '\n'
prompt     = '> '
space      = ' '
tiletpl    = '%3s'
shipchar   = '#'
sunkship   = '%'
blank      = '.'
hitchar    = '*'
quit_key   = 'q'

players    = [1, 2]
ai_players = [1, 2]
divider    = '-' * (size[0]*4 + 6)


class Tile(AttrToggles):
    """Tile that may be a ship or blank space (water)."""
    ship              = False
    is_hit            = False
    hidden            = True
    revealed          = False
    attribute_toggles = [("hidden", "revealed")]

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return blank if self.hidden else self.char


class Blank(Tile):
    char = blank

    def hit(self):
        self.is_hit   = True
        self.revealed = True
        self.char     = hitchar

class Ship(Tile):
    char = shipchar
    ship = True

    def hit(self):
        self.is_hit   = True
        self.revealed = True
        self.char     = sunkship


class BattleshipBoard(Board):
    def __init__(self, size):
        super(BattleshipBoard, self).__init__(size, Blank, tiletpl=tiletpl)

    def draw(self):
        print(space*3, ujoin(range1(self.width), tpl=tiletpl), nl )
        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, tpl=tiletpl), nl)

    def all_unhit(self):
        return [tile for tile in self if not tile.is_hit]

    def ships(self):
        return [tile for tile in self if tile.ship]

    def random_unhit(self):
        return rndchoice(self.all_unhit())

    def valid_hidden(self, loc):
        return bool(self.valid(loc) and self[loc].hidden)

    def getloc(self, start, dir, n):
        """Return location offset from `start` point by `n` tiles in direction `dir`."""
        return Loc(start.x + dir.x*n, start.y + dir.y*n)

    def random_blank(self):
        return rndchoice( [tile for tile in self if not tile.ship] )

    def allow_placement(self, locs):
        """Check that `locs` are valid and have no neighbouring ships."""
        if not all(self.valid(loc) for loc in locs):
            return False
        ncl = self.neighbour_cross_locs
        neighbours = set(flatten( [ncl(self[loc]) for loc in locs] ))
        return not any( self[loc].ship for loc in neighbours )

    def random_placement(self, ship):
        """Return list of random locations for `ship` length."""
        dirs  = [Loc(*d) for d in ((1,0), (0,1), (-1,0), (0,-1))]

        while True:
            start = self.random_blank().loc
            dir   = rndchoice(dirs)
            locs  = [ self.getloc(start, dir, n) for n in range(ship) ]
            if self.allow_placement(locs):
                break
        return locs


class Player(object):
    def __init__(self, num):
        """Create player's board and randomly place `num_ships` ships on it."""
        self.num = num
        B = self.board = BattleshipBoard(size)

        for ship in range1(num_ships):
            for loc in B.random_placement(ship):
                B[loc] = Ship(loc)

        self.ai = bool(self.num in ai_players)

        if not self.ai:
            for tile in B:
                tile.revealed = True

    def enemy(self):
        return nextval(players, self)


class Battleship(object):
    losemsg = "All ships are sunk! Player %s loses the game!"

    def draw(self):
        p1, p2 = players

        print(nl*5)
        p1.board.draw()
        print(divider)
        p2.board.draw()

    def check_end(self, player):
        if all(ship.is_hit for ship in player.board.ships()):
            self.game_lost(player)

    def game_lost(self, player):
        self.draw()
        print(self.losemsg % player.num)
        sys.exit()


class Test(object):
    def run(self):
        for player in cycle(players):
            bship.draw()
            tile = self.ai_move(player) if player.ai else self.get_move(player)
            tile.hit()
            bship.check_end(player.enemy())
            sleep(pause_time)

        print(divider)

    def get_move(self, player):
        while True:
            try: return self._get_move(player)
            except (IndexError, ValueError, TypeError): pass

    def _get_move(self, player):
        """ Get user command and reveal the tile; check if game is won/lost.
            User input can be with a space e.g. 10 5 or without a space when possible e.g. 35.
        """
        inp = raw_input(prompt)
        if inp == quit_key: sys.exit()

        inp   = inp.split() if space in inp else inp
        x, y  = parse_hnuminput(inp)
        enemy = player.enemy()
        return enemy.board[ Loc(x, y) ]

    def ai_move(self, player):
        """Very primitive `AI', always hits a random location."""
        enemy = player.enemy()
        return enemy.board.random_unhit()


if __name__ == "__main__":
    players = [Player(p) for p in players]
    bship   = Battleship()

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
