#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

""" a text adventure game
"""

from random import randint, random
from random import choice as randchoice
from time import sleep
from collections import defaultdict
from operator import itemgetter
from copy import copy

from utils import Loop, Container, TextInput, range1, first, sjoin, nl, space
from board import StackableBoard, Loc, BaseTile

roomchance  = Container(door=0.8, shaky_floor=0.01)
itemchance  = Container(Gem=0.1, Key=0.05, Gold=0.25, Anvil=0.01)
border      = Container(tl='╭', tr='╮', bl='╰', br='╯', horiz='─', vertical='│')
size        = 10, 10
doorchar    = '⌺'
roomchar    = '#'
player_char = '@'

"""
─────────────
|   |   |   |
| ⌺ | ⌺ | ⌺ |
─────────────

"""


class Item(BaseTile):
    gem = key = gold = anvil = False

    def __init__(self):
        super().__init__(self)
        self.name = self.__class__.__name__

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __str__(self):
        if self.gold : return "piece of gold"
        else         : return self.name

    def __hash__(self):
        return hash(self.name)


class Gem(Item)   : pass
class Key(Item)   : pass
class Gold(Item)  : pass
class Anvil(Item) : pass


class DirLoop(Loop):
    def cw(self, n=1)  : return super(DirLoop, self).next(n)
    def ccw(self, n=1) : return super(DirLoop, self).prev(n)


class AdvBoard(StackableBoard):
    def nlocs(self, tile_loc):
        x, y = self.ploc(tile_loc)
        locs = ((x, y-1), (x+1, y), (x, y+1), (x-1, y))
        locs = [Loc(*tup) for tup in locs]
        return [(loc if self.valid(loc) else None) for loc in locs]

    def center(self):
        return Loc(self.width // 2, self.height // 2)


class Room(object):
    item = None

    def __init__(self, loc):
        self.doors   = defaultdict(bool)
        self.loc     = loc
        board[loc]   = self
        inverse_dirs = (2,3,0,1)
        # print("loc", loc)

        for rd, nd, nloc in zip(range(4), inverse_dirs, board.nlocs(loc)):
            if nloc:
                # print("nloc", nloc)

                room = board.get_instance(Room, nloc)
                self.doors[rd] = bool( (random()<roomchance.door or room and room.doors[nd]) )

        # print("self.doors", self.doors)
        self.item        = genitem()
        self.shaky_floor = bool(random() < roomchance.shaky_floor)

    def __str__(self):
        return roomchar

    def show_doors(self, doors):
        d     = "%s"
        h, v  = border.horiz, border.vertical
        walls = ''.join([h*13, nl, v, space, d, space, v, space, d, space, v, space, d, space, v])
        return walls % tuple(doors)


class Player(object):
    dir    = DirLoop(range(4), name="dir")
    items  = defaultdict(int)
    invtpl = "%20s %4d"

    def __init__(self, loc):
        self.loc   = loc
        self.room  = Room(loc)
        self.doors = []
        board[loc] = self


    def __str__(self):
        return player_char

    def move(self, ndir):
        doordict = dict(zip((3,0,1), self.doors))
        if ndir!=2 and not doordict[ndir]:
            print("You bump into the wall")
            return

        self.dir.cw(ndir)
        absdir    = DirLoop(board.dirlist).cw(self.dir.dir)
        newloc    = board.nextloc(self, absdir)
        self.room = board[newloc]

        if board[newloc] == space:
            self.room = Room(newloc)
        board.move(self, newloc)
        # print("self.dir.dir", self.dir.dir)

    def forward(self) : self.move(0)
    def right(self)   : self.move(1)
    def back(self)    : self.move(2)
    def left(self)    : self.move(3)

    def pickup(self):
        self.items[self.room.item] += 1
        self.room.item = None

    def inventory(self):
        for item in self.items.items():
            if item: print(invtpl % item)

    def roomview(self):
        room      = self.room
        doorsdir  = copy(self.dir)
        doors     = doorsdir.ccw(), doorsdir.cw(), doorsdir.cw()
        doors     = [room.doors[d] for d in doors]
        doordirs  = ["on the left", "in front", "on the right"]

        doorchars = (doorchar if d else space for d in doors)
        L         = []

        L.append(self.room.show_doors(doorchars))
        L.append("You enter a room.")

        if room.item:
            L.append("You see %s lying on the floor." % a_an(str(room.item)))

        doordirs   = [d[1] for d in zip(doors, doordirs) if d[0]]
        self.doors = doors
        self.doors_desc(doordirs, L)
        return L

    def doors_desc(self, doordirs, L):
        if doordirs:
            msg = "You see a door "
            end = " of you."

            if len(doordirs) == 1:
                msg += first(doordirs) + end
            elif len(doordirs) == 2:
                msg += sjoin(doordirs, " and ") + end
            else:
                msg += sjoin(doordirs[:2], ", ") + " and %s" + end
                msg = msg % doordirs[2]

            L.append(msg)


class Adv(object):
    pass

class BasicInterface(object):
    commands = dict(a="left", s="back", w="forward", d="right", p="pickup", i="inventory")

    def run(self):
        self.textinput = TextInput("(a|s|w|d|p|i)")

        while True:
            print( nl.join(player.roomview()) )
            cmd = self.textinput.getval()
            getattr(player, self.commands[cmd])()
            board.draw()


def genitem():
    for name, chance in sorted(itemchance.items(), key=itemgetter(1)):
        if random() <= chance:
            return globals()[name]()

def a_an(item):
    return "an " + item if item.startswith('A') else "a " + item


if __name__ == "__main__":
    board  = AdvBoard(size, space)
    player = Player(board.center())
    BasicInterface().run()
