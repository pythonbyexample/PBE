#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from time import sleep

from utils import TextInput, AttrToggles, enumerate1, range1, ujoin, flatten, nextval, first
from board import Board, Loc

size       = 5, 5
num_ships  = 3
pause_time = 0.4

nl         = '\n'
space      = ' '
blank      = '.'
tiletpl    = '%3s'
shipchar   = '#'
sunkship   = '%'
hitchar    = '*'
padding    = 2, 1

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
        super(BattleshipBoard, self).__init__(size, Blank, num_grid=True, padding=padding,
                                              pause_time=0, screen_sep=0)

    def draw2(self):
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
        sleep(pause_time)

    def check_end(self, player):
        if all(ship.is_hit for ship in player.board.ships()):
            self.game_lost(player)

    def game_lost(self, player):
        self.draw()
        print(self.losemsg % player.num)
        sys.exit()


class Test(object):
    def run(self):
        # board is only used to check if location is within range (using board.valid())
        self.textinput = TextInput(first(players).board, "loc")

        while True:
            for player in players:
                bship.draw()
                tile = self.ai_move(player) if player.ai else self.get_move(player)
                tile.hit()
                bship.check_end(player.enemy())
            print(divider)

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
