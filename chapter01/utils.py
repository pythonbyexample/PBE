from copy import copy


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

def joins(iterable, sep=' '):
    return sep.join( [unicode(x) for x in iterable] )
