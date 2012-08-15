#!/usr/bin/env python

# Imports {{{
import sys
from random import randint
from copy import deepcopy

from ..shared import *

dimensions = 8, 8
# }}}


class Board(object):
    def __init__(self):
        self.maxx, self.maxy = dimensions
        self.blank = [ [[' '] for _ in range(self.maxx)] for _ in range(self.maxy) ]
        self.clear()
        for loc in self: self.put(wall, loc)

    def is_empty(self):
        return self.board == self.blank

    def clear(self, loc=None):
        if loc: self.board[loc.y][loc.x] = [' ']
        else:   self.board = deepcopy(self.blank)

    def display(self):
        pass

    def put(self, thing, loc=None):
        if not loc: loc = thing.loc
        self.board[loc.y][loc.x].append(thing)

    def __iter__(self):
        for y in range(self.maxy):
            for x in range(self.maxx):
                yield Loc(x, y)

    def valid(self, loc):
        return bool(0 <= loc.x < self.maxx and 0 <= loc.y < self.maxy)

    def near_border(self, loc):
        x, y = loc
        if x+1 == self.maxx or y+1 == self.maxy or x == 0 and y == 0:
            return True

    def empty(self, loc):
        return bool(self.valid(loc) and self.values(loc) == [' '])

    def remove(self, item, loc=None):
        loc = loc or item.loc
        l = self.board[loc.y][loc.x]
        if item in l: l.remove(item)

    def value(self, loc):
        return self.values(loc)[-1]

    def values(self, loc):
        if self.valid(loc): return self.board[loc.y][loc.x]

    def random(self):
        return randint(0, self.maxx-1), randint(0, self.maxy-1)

    def random_empty(self):
        for _ in range(999):
            l = Loc(self.random())
            if self.empty(l): return l


class Loc(object):
    def __init__(self, x, y=None):
        x, y = unwrap(x, y)
        self.loc = x, y
        self.x, self.y = x, y

    def __str__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)
