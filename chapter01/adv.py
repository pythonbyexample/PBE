#!/usr/bin/env python3

""" a text adventure game
"""

from random import randint
from time import sleep
from collections import defaultdict
from itertools import zip_longest

from utils import Loop, Container, range1, first, sjoin, nl
from board import Board, Loc, BaseTile

itemchance = Container(door=0.6, weak_floor=0.01, )
size       = 2000, 2000


class Item(BaseTile):
    gem = key = gold = anvil = False
    def __eq__(self, other):
        return self.__class__ == other.__class__

class Gem(Item)   : pass
class Key(Item)   : pass
class Gold(Item)  : pass
class Anvil(Item) : pass


class DirLoop(Loop):
    def cw(self, n=1)  : super(DirLoop, self).next(n)
    def ccw(self, n=1) : super(DirLoop, self).prev(n)


class AdvBoard(Board):
    def center(self):
        wm, hm = self.width / 2, self.height / 2
        return self[Loc(wm, hm)]


class Room(object):
    doors = defaultdict(bool)
    item  = None

    def __init__(self, loc):
        self.loc   = loc
        board[loc] = self
        for rd, nd, room in zip_longest(board.dirlist, (2,3,0,1), board.neighbours(loc)):
            self.doors[rd] = bool( (room and room.doors[nd]) or random() < chance_of_door )
        self.item = randchoice((None, Gem(), Key(), Gold()))



class Player(object):
    dir    = DirLoop(range(3), name=dir)
    items  = defaultdict(int)
    invtpl = "%20s %4d"

    def __init__(self, loc):
        self.loc  = loc
        self.room = board[loc]

    def move(self, ndir):
        self.dir.cw(ndir)
        absdir   = DirLoop(board.dirlist).cw(self.dir.dir)
        self.loc = self.loc.moved(absdir)

        if not board[self.loc]:
            Room(self.loc)

    def pickup(self):
        item = self.room.item
        if item:
            self.items[item] += 1
            self.room.item = None

    def inventory(self):
        for item in self.items.items():
            print(invtpl % item)


if __name__ == "__main__":
    # SlotMachine().run(pause_time)
    test()
