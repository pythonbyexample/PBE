#!/usr/bin/env python

# Imports {{{
import sys
from random import randint
from copy import deepcopy

from shared import *

dimensions = 90, 30
wall       = u'\u25af'
# }}}


class Field(object):
    def __init__(self):
        self.maxx, self.maxy = dimensions
        self.blank = [ [[' '] for _ in range(self.maxx)] for _ in range(self.maxy) ]
        self.clear()
        # for loc in self: Thing(self, wall, loc, False)
        for loc in self: self.put(wall, loc)

    def is_empty(self):
        return self.field == self.blank

    def clear(self, loc=None):
        if loc: self.field[loc.y][loc.x] = [' ']
        else:   self.field = deepcopy(self.blank)

    def display(self):
        topleft, topright, bottomleft, bottomright, horizontal, vertical = u"\u250c \u2510 \u2514 \u2518 \u2500 \u2502".split()

        # print '\n'*45
        print ' ' + topleft + horizontal*self.maxx + topright
        for n, row in enumerate(self.field):
            print ' ' + vertical + joinst(row, '') + vertical,
            if n%8 == 0: print '-'
            else: print
        print ' ' + bottomleft + horizontal*self.maxx + bottomright
        print ' ',
        for x in range(8):
            sys.stdout.write(' '*9 + '|')
        print

    def put(self, thing, loc=None):
        if not loc: loc = thing.loc
        self.field[loc.y][loc.x].append(thing)

    def __iter__(self):
        for y in range(self.maxy):
            for x in range(self.maxx):
                yield Location(x, y)

    def move(self, dir, item):
        """0/1 right/left; 2/3 down/up; 4/5 r-up/down; 6/7 l-up/down."""
        dir    = int(dir)
        x2, y2 = item.loc.x, item.loc.y

        if   dir == 0: x2 += 1
        elif dir == 1: x2 -= 1
        elif dir == 2: y2 += 1
        elif dir == 3: y2 -= 1
        elif dir == 4: x2 += 1; y2 += 1
        elif dir == 5: x2 += 1; y2 -= 1
        elif dir == 6: x2 -= 1; y2 -= 1
        elif dir == 7: x2 -= 1; y2 += 1
        loc2 = Location(x2, y2)

        if self.empty(loc2):
            self.remove(item)
            item.loc = loc2
            self.put(item)
            return loc2

    def valid(self, x, y=None):
        x, y = unwrap(x, y)
        if x+1 <= self.maxx and y+1 <= self.maxy and x >= 0 and y >= 0:
            return True

    def near_border(self, x, y=None):
        x, y = unwrap(x, y)
        if x+1 == self.maxx or y+1 == self.maxy or x == 0 and y == 0:
            return True

    def empty(self, loc):
        if self.valid(loc) and self.values(loc) == [' ']:
            return True

    def remove(self, item, loc=None):
        loc = loc or item.loc
        l = self.field[loc.y][loc.x]
        if item in l: l.remove(item)

    def value(self, x, y=None):
        return self.values(x, y)[-1]

    def values(self, x, y=None):
        x, y = unwrap(x, y)
        if self.valid(x, y): return self.field[y][x]

    def random(self):
        return randint(0, self.maxx-1), randint(0, self.maxy-1)

    def random_empty(self):
        for _ in range(999):
            l = Location(self.random())
            if self.empty(l): return l

    def all_neighbours(self, loc):
        """Return the list of neighbours of `loc`."""
        x, y = loc
        lst = [
               # clockwise from upper left
               (x-1 , y-1),
               (x   , y-1),
               (x+1 , y-1),
               (x+1 , y),
               (x+1 , y+1),
               (x   , y+1),
               (x-1 , y+1),
               (x-1 , y),
               ]
        return [self.value(*l) for l in lst if self.valid(*l)]

    def neighbours(self, loc):
        return [x for x in self.all_neighbours(loc) if x!=' ']

    def live_neighbours(self, loc):
        return [x for x in self.neighbours(loc) if x.alive]


class Location(object):
    def __init__(self, x, y=None):
        x, y = unwrap(x, y)
        self.loc = x, y
        self.x, self.y = x, y

    def __str__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)
