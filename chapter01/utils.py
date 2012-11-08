#!/usr/bin/env python

from copy import copy
from random import randint


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

    def update_attr(self):
        setattr(self, self.name, self.items[self.index])

    def prev(self):
        self.index = self.index-1 if self.index > 0 else self.lastind
        self.update_attr()


class Dice(object):
    """Roll multiple dice."""
    def __init__(self, num=2, sides=6):
        self.num   = num
        self.sides = sides

    def roll(self):
        return [randint(1, self.sides) for _ in range(self.num)]

    def rollsum(self):
        return sum(self.roll())


def ujoin(iterable, sep=' ', tpl=u"%s"):
    return sep.join( [tpl % x for x in iterable] )

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

def to_pyreadable(iterable):

    """Convert a list of 1-indexed string values to 0-indexed python integers."""

    return (int(val)-1 for val in iterable)


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

class X(AttrToggles):
    hidden = True
    revealed = False
    attribute_toggles = [("hidden", "revealed")]

if __name__ == "__main__":
    x=X()
    print("x.hidden", x.hidden)
    print("x.revealed", x.revealed)

    x.hidden=False
    print
    print("x.hidden", x.hidden)
    print("x.revealed", x.revealed)

    x.hidden=True
    print
    print("x.hidden", x.hidden)
    print("x.revealed", x.revealed)
