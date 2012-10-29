from copy import copy
from random import randint


class Loc(object):
    """Tile location on the grid with x, y coordinates."""
    __slots__ = ['x', 'y', 'loc']

    def __init__(self, x, y):
        self.loc = x, y
        self.x, self.y = x, y

    def __str__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)

    def moved(self, x, y):
        """ Return a new Loc moved according to delta modifiers `x` and `y`,
            e.g. 1,0 to move right.
        """
        return Loc(self.x + x, self.y + y)


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
    def __init__(self, num=2, sides=6):
        self.num   = num
        self.sides = sides

    def roll(self):
        return [randint(1, self.sides) for _ in range(self.num)]

    def rollsum(self):
        return sum(self.roll())


def ujoin(iterable, sep=' '):
    return sep.join( [unicode(x) for x in iterable] )

def itersplit(it, check):
    """Split iterator `it` in two lists: first that passes `check` and second that does not."""
    return [x for x in it if check(x)], \
           [x for x in it if not check(x)]

def enumerate1(it):
    """Enumerate iterator `it` using 1-based indexing."""
    return ((n+1, x) for n, x in enumerate(it))

def envelope(value, minval, maxval):
    """Adjust `value` to be within min/max bounds."""
    return min(max(val, minval), maxval)
