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


def joins(iterable, sep=' '):
    return sep.join( [unicode(x) for x in iterable] )
