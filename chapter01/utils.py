#!/usr/bin/env python

import sys
from copy import copy
from random import randint

from board import Loc

sentinel = object()
space    = ' '

class InvalidCode(Exception):
    def __init__(self, val) : self.val = val
    def __str__(self)       : return repr(self.val)


class Loop(object):
    """ Loop over a list of items in forward / backward direction, keeping track of current item,
        which is available as `item` attribute by default, or under a custom `name` provided to init.
    """
    def __init__(self, items, name="item", index=0):
        self.items   = items
        self.index   = index
        self.name    = name
        self.lastind = len(self.items) - 1
        self.update_attr()

    def next(self):
        self.index = self.index+1 if self.index < self.lastind else 0
        self.update_attr()

    def prev(self):
        self.index = self.index-1 if self.index > 0 else self.lastind
        self.update_attr()

    def update_attr(self):
        self.item = self.items[self.index]
        setattr(self, self.name, self.items[self.index])

    def __eq__(self, value):
        return bool(self.item == value)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return repr(self.item)

    def __bool__(self):
        return bool(self.item)

    def __add__(self, other):
        return self.item + other

    def __sub__(self, other):
        return self.item - other

    def __radd__(self, other):
        return self.item + other

    def __rsub__(self, other):
        return other - self.item


class AttrToggles(object):
    """Inverse-toggle two boolean attributes when one of a pair is toggled; `attribute_toggles` is a list of tuples."""
    attribute_toggles = []

    def __setattr__(self, attr, val):
        object.__setattr__(self, attr, val)
        toggles = self.attribute_toggles

        if attr in flatten(toggles):
            for attrs in toggles:
                if attr in attrs:
                    attrs = set(attrs) - set([attr])
                    for attr in attrs:
                        object.__setattr__(self, attr, not val)


class Dice(object):
    """Roll multiple dice."""
    def __init__(self, num=2, sides=6):
        self.num   = num
        self.sides = sides

    def roll(self):
        return [randint(1, self.sides) for _ in range(self.num)]

    def rollsum(self):
        return sum(self.roll())


class TextInput(object):
    inv_inp = "Invalid input"

    def __init__(self, board, fmt="loc", prompt="> ", quit_key='q', inv_inp=None):
        self.board    = board
        self.fmt      = fmt.split()
        self.prompt   = prompt
        self.quit_key = quit_key
        self.inv_inp  = inv_inp or self.inv_inp

    def parse_input(self):
        while 1:
            try: return self._parse_input()
            except (IndexError, ValueError, TypeError, KeyError), e:
                print(self.invalid_inp)

    def _parse_input(self):
        inp = raw_input(self.prompt).strip()
        if inp == self.quit_key: sys.exit()

        inp      = inp.split() if space in inp else list(inp)
        command  = []
        handlers = {"%d": int, "%f": float, "%s": str}

        for n, code in enumerate(self.fmt):

            if code == "loc":
                x, y = inp.pop(0), inp.pop(0)
                loc = Loc( int(x)-1, int(y)-1 )
                if not self.board.valid(loc):
                    raise IndexError
                command.append(loc)

            elif code in handlers:
                command.append( handlers.get(code)(inp.pop(0)) )

            else:
                raise InvalidCode(code)

        return command



def ujoin(iterable, sep=' ', tpl='%s'):
    return sep.join( [tpl % unicode(x) for x in iterable] )

def itersplit(it, check):
    """Split iterator `it` in two lists: first that passes `check` and second that does not."""
    return [x for x in it if check(x)], \
           [x for x in it if not check(x)]

def enumerate1(it):
    """Enumerate iterator `it` using 1-based indexing."""
    return ((n+1, x) for n, x in enumerate(it))

def range1(x):
    return range(1, x+1)

def envelope(value, minval, maxval):
    """Adjust `value` to be within min/max bounds."""
    return min(max(val, minval), maxval)

def flatten(iterable):
    return [item for sublist in iterable for item in sublist]

def human_readable(val):
    return val + 1

def py_readable(val):
    return val - 1

def timefmt(sec):
    return "%d:%02d" % (sec/60, sec%60)

def parse_hnuminput(iterable):
    """Convert a list of 'human input' 1-indexed string values to 0-indexed integers."""
    return [int(val)-1 for val in iterable]

def lastind(iterable):
    return len(iterable) - 1

def nextval(iterable, value):
    """Next value of `iterable` after `value`, wrapping around at the end."""
    i = iterable.index(value)
    i = 0 if i >= lastind(iterable) else i+1
    return iterable[i]

def first(iterable):
    return next(iter(iterable))
