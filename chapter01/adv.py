#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

""" a text adventure game
"""

from random import randint
from random import choice as randchoice
from time import sleep
from collections import defaultdict
from itertools import zip_longest
from operator import itemgetter

from utils import Loop, Container, range1, first, sjoin, nl
from board import StackableBoard, Loc, BaseTile

roomchance = Container(door=0.6, shaky_floor=0.01)
itemchance = Container(Gem=0.1, Key=0.05, Gold=0.25, Anvil=0.01)
size       = 2000, 2000
doorchar = '⌺'


class Item(BaseTile):
    gem = key = gold = anvil = False

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __str__(self):
        if self.gold: return "piece of gold"


class Gem(Item)   : pass
class Key(Item)   : pass
class Gold(Item)  : pass
class Anvil(Item) : pass


class DirLoop(Loop):
    def cw(self, n=1)  : super(DirLoop, self).next(n)
    def ccw(self, n=1) : super(DirLoop, self).prev(n)


class AdvBoard(StackableBoard):
    def center(self):
        return Loc(self.width / 2, self.height / 2)


class Room(object):
    doors = defaultdict(bool)
    item  = None

    def __init__(self, loc):
        self.loc     = loc
        board[loc]   = self
        inverse_dirs = (2,3,0,1)

        for rd, nd, nloc in zip_longest(range(4), inverse_dirs, board.neighbour_locs(loc)):
            if nloc:
                room = board[nloc]
                self.doors[rd] = bool( (random()<roomchance.door or room and room.doors[nd]) )

        self.item        = genitem()
        self.shaky_floor = bool(random() < roomchance.shaky_floor)


class Player(object):
    dir    = DirLoop(range(3), name=dir)
    items  = defaultdict(int)
    invtpl = "%20s %4d"

    def __init__(self, loc):
        self.loc  = loc
        self.room = board[loc]

    def move(self, ndir):
        self.dir.cw(ndir)
        absdir = DirLoop(board.dirlist).cw(self.dir.dir)
        board.move(self, board.nextloc(self, absdir))

        if not board[self.loc]:
            Room(self.loc)

    def pickup(self):
        self.items[self.room.item] += 1
        self.room.item = None

    def inventory(self):
        for item in self.items.items():
            if item: print(invtpl % item)

    def roomview(self):
        room     = self.room
        doorsdir = copy(self.dir)
        doors    = doorsdir.prev(), doorsdir.next(), doorsdir.next()
        doors    = [room.doors[d] for d in doors]
        doordirs = ["on the left", "in front", "on the right"]

        L = []
        L.append(space.join(doorchar if d else space for d in doors))
        L.append("You enter a room.")

        if room.item:
            L.append("You see %s lying on the floor." % a_an(room.item))

        doordirs = [d[1] for d in zip(doors, doordirs) if d[0]]
        self.doors_desc(doordirs, L)
        return L

    def doors_desc(self, doordirs, L):
        if doordirs:
            msg = "You see a door "

            if len(doordirs) == 1:
                msg += first(doordirs) + " of you."
            elif len(doordirs) == 2:
                msg += sjoin(doordirs, " and ") + " of you."
            else:
                msg += sjoin(doordirs[:2], ", ") + "and %s of you."
                msg = msg % doordirs[2]

            L.append(msg)


def genitem():
    for name, chance in sorted(itemchance.items(), key=itemgetter(1)):
        if random() <= chance:
            return locals()[name]()

def a_an(item):
    return "an " + item if item.startswith('A') else "a " + item


if __name__ == "__main__":
    board  = AdvBoard(size, None)
    player = Player(board.center())
