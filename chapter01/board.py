from __future__ import print_function, unicode_literals, division
from utils import ujoin


class Loc(object):
    def __init__(self, x, y):
        self.loc = x, y
        self.x, self.y = x, y

    def __repr__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)

    def moved(self, x, y):
        """ Return a new Loc moved according to delta modifiers `x` and `y`,
            e.g. 1,0 to move right.
        """
        return Loc(self.x + x, self.y + y)

# Direction (e.g. 0,1=right) works the same way but should have a different name for clarity
Dir = Loc

class CommonBoard(object):

    def __init__(self, size, tiletpl="%s"):
        if isinstance(size, int):
            size = size, size   # handle square board
        self.width, self.height = size
        self.tiletpl = tiletpl
        self.directions()

    def __iter__(self):
        return ( self[Loc(x, y)] for y in range(self.height) for x in range(self.width) )

    def locations(self):
        return (Loc(x, y) for y in range(self.height) for x in range(self.width))

    def valid(self, loc):
        return bool( loc.x >= 0 and loc.y >= 0 and loc.x <= self.width-1 and loc.y <= self.height-1 )

    def directions(self):
        """Create list and dict of eight directions, going from up clockwise."""
        dirs          = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        self.dirlist  = [Dir(*d) for d in (dirs[0], dirs[2], dirs[4], dirs[6])]
        self.dirlist2 = [Dir(*d) for d in dirs]
        self.dirnames = dict(zip(self.dirlist2, "up ru right rd down ld left lu".split()))

    def neighbour_locs(self, tile):
        """Return the generator of neighbour locations of `tile`."""
        x, y = tile.loc
        coords = (-1,0,1)
        locs = set((x+n, y+m) for n in coords for m in coords) - set( [(x,y)] )
        return ( Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) )

    def neighbours(self, tile):
        """Return the generator of neighbours of `tile`."""
        return (self[loc] for loc in self.neighbour_locs(tile))

    def neighbour_cross_locs(self, tile):
        """Return a generator of neighbour 'cross' (i.e. no diagonal) locations of `tile`."""
        x, y = tile.loc
        locs = ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
        return [ Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) ]

    def cross_neighbours(self, tile):
        """Return the generator of 'cross' (i.e. no diagonal) neighbours of `tile`."""
        return (self[loc] for loc in self.neighbour_cross_locs(tile))

    def make_tile(self, loc):
        """Make a tile using `self.def_tile`. If def_tile is simply a string, return it, otherwise instantiate with x, y as arguments."""
        return self.def_tile if isinstance(self.def_tile, basestring) else self.def_tile(loc)

    def move(self, item_or_loc, newloc):
        if isinstance(item_or_loc, Loc):
            loc  = item_or_loc
            item = self[loc]
        else:
            item = item_or_loc
            loc  = item_or_loc.loc

        self[newloc] = item
        self[loc]    = self.make_tile(loc)
        item.loc     = newloc


class Board(CommonBoard):
    def __init__(self, size, def_tile, **kwargs):
        super(Board, self).__init__(size, **kwargs)

        self.def_tile = def_tile
        xrng, yrng    = range(self.width), range(self.height)
        self.board    = [ [self.make_tile(Loc(x, y)) for x in xrng] for y in yrng ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x] = item

    def __delitem__(self, loc):
        self.board[loc.y][loc.x] = self.make_tile(loc)

    def draw(self):
        for row in self.board:
            print(ujoin(row, '', tpl=self.tiletpl))


class StackableBoard(CommonBoard):
    def __init__(self, size, def_tile, **kwargs):
        super(StackableBoard, self).__init__(size, **kwargs)

        self.def_tile = def_tile
        xrng, yrng    = range(self.width), range(self.height)
        self.board    = [ [[self.make_tile(Loc(x, y))] for x in xrng] for y in yrng ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x][-1]

    def items(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.board[loc.y][loc.x].append(item)

    def __delitem__(self, loc):
        del self.board[loc.y][loc.x][-1]

    def draw(self):
        for row in self.board:
            print(ujoin( (i[-1] for i in row), tpl=self.tiletpl))
