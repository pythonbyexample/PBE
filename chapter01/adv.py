#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

""" a text adventure game
"""

from random import randint, random
from random import choice as randchoice
from collections import defaultdict
from copy import copy

from utils import Loop, Container, TextInput, first, sjoin, nl, space
from board import StackableBoard, Loc, BaseTile

roomchance  = Container(door=0.8, shaky_floor=0.01)
itemchance  = Container(Gem=0.1, Key=0.05, Gold=0.25, Anvil=0.01)
border      = Container(tl='╭', tr='╮', bl='╰', br='╯', horiz='─', vertical='│')
size        = 4
doorchar    = '⌺'
roomchar    = '▢'
player_char = '☺'
absdirs     = range(4)

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

    def rotate_cw(self, n=1):
        for _ in range(n):
            self.items.append(self.items.pop(0))
        self.update_attr()


class AdvBoard(StackableBoard):
    def nlocs(self, loc):
        x, y = loc
        locs = ((x, y-1), (x+1, y), (x, y+1), (x-1, y))
        locs = [Loc(*tup) for tup in locs]
        return [(loc if self.valid(loc) else None) for loc in locs]

    def center(self):
        return Loc(self.width // 2, self.height // 2)


class Room(object):
    item = None

    def __init__(self, loc):
        self.loc         = loc
        self.doors       = list(self.gendoors())
        # print("self.doors", self.doors)
        self.item        = genitem()
        self.shaky_floor = bool(random() < roomchance.shaky_floor)
        board[loc]       = self

    def __str__(self):
        return roomchar

    def gendoors(self):
        inverse_dirs = (2,3,0,1)
        for rd, nd, nloc in zip(absdirs, inverse_dirs, board.nlocs(self.loc)):
            if not nloc:
                yield False
            else:
                room = board.get_instance(Room, nloc)
                yield bool( (random()<roomchance.door or room and room.doors[nd]) )

    def show_doors(self, doors):
        d     = "%s"
        h, v  = border.horiz, border.vertical
        walls = ''.join([h*13, nl, v, space, d, space, v, space, d, space, v, space, d, space, v, nl])
        return walls % tuple((doorchar if d else space) for d in doors)


class PlayerDir(object):
    dir      = DirLoop(absdirs, name="dir")
    bearings = "North East South West".split()

    def __init__(self, player):
        self.player = player
        self.update()
        self.update_doors()

    def update(self, dirnum=0):
        self.dir.cw(dirnum)
        self.absdir = DirLoop(board.dirlist).cw(self.dir.dir)

    def update_doors(self):
        self.doors  = DirLoop(copy(self.player.room.doors))
        self.doors.rotate_cw(self.dir.dir)
        self.viewdoors = [self.doors[d] for d in (3,0,1)]
        descdoors      = ["on the left", "in front", "on the right"]
        self.descdoors = [d[1] for d in zip(self.viewdoors, descdoors) if d[0]]

    def bearing(self):
        return "Bearing: " + self.bearings[self.dir.dir]


class Player(object):
    items     = defaultdict(int)
    invtpl    = "%20s %4d"
    bump_wall = "You bump into the wall"

    def __init__(self, room):
        self.room       = room
        self.loc        = room.loc
        board[self.loc] = self
        self.dir        = PlayerDir(self)
        self.messages   = []

    def __str__(self):
        return player_char

    def move(self, ndir):
        if not self.dir.doors[ndir]:
            print(self.bump_wall)
            return
        self.messages = ["You enter a room.", nl]

        self.dir.update(ndir)
        newloc    = board.nextloc(self, self.dir.absdir)
        self.room = Room(newloc) if board.empty(newloc) else board[newloc]
        board.move(self, newloc)
        self.dir.update_doors()

    def forward(self) : self.move(0)
    def right(self)   : self.move(1)
    def back(self)    : self.move(2)
    def left(self)    : self.move(3)

    def pickup(self):
        if self.room.item:
            self.items[self.room.item] += 1
            self.room.item = None

    def inventory(self):
        for item in self.items.items():
            print(invtpl % item)

    def roomview(self):
        L = self.messages
        L.append(self.room.show_doors(self.dir.viewdoors))

        if room.item:
            L.append("You see %s lying on the floor." % a_an(str(room.item)))

        self.doormsg()
        return nl.join(L)

    def doormsg(self):
        descdoors = self.dir.descdoors

        if descdoors:
            msg  = "You see a door "
            end  = " of you."
            _and = " and "

            if len(descdoors) == 1:
                msg += first(descdoors) + end
            elif len(descdoors) == 2:
                msg += sjoin(descdoors, _and) + end
            else:
                last = descdoors.pop()
                msg += sjoin(descdoors, ", ") + _and + last + end

            self.messages.append(msg)

    def map(self):
        board.draw()


class Adv(object):
    pass

class BasicInterface(object):
    def run(self):
        commands = dict(a="left", s="back", w="forward", d="right", p="pickup", i="inventory", m="map")

        while True:
            print(player.dir.bearing())
            print(player.roomview())
            cmd = TextInput("(a|s|w|d|p|i|m)").getval()
            getattr(player, commands[cmd])()
            print(nl)


def genitem():
    for name, chance in itemchance.items():
        if random() <= chance:
            return globals()[name]()

def a_an(item):
    return "an " + item if item.startswith('A') else "a " + item


if __name__ == "__main__":
    board  = AdvBoard(size, space)
    room   = Room(board.center())
    player = Player(room)
    BasicInterface().run()
