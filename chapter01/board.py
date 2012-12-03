from __future__ import print_function, unicode_literals, division
import math
from time import sleep

from utils import ujoin, range1, enumerate1

nl    = '\n'
space = ' '


class BaseTile(object):
    def __init__(self, loc=None):
        self.loc = loc
        setattr(self, self.__class__.__name__.lower(), True)


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

    def __eq__(self, other):
        return self.loc == getattr(other, "loc", None)

    def __ne__(self, other):
        return not self.__eq__(other)

Dir = Loc   # Directions (e.g. 0,1=right) work the same way but should have a different name for clarity

class BaseBoard(object):
    stackable  = False

    def __init__(self, size, num_grid=False, padding=(0, 0), pause_time=0.2, screen_sep=5, init_tiles=True):
        if isinstance(size, int):
            size = size, size   # handle square board
        self.width, self.height = size

        self.num_grid    = num_grid
        self.xpad        = padding[0]
        self.ypad        = padding[1]
        self.pause_time  = pause_time
        self.screen_sep  = screen_sep
        self.init_tiles  = init_tiles     # place tiles in __init__; otherwise use place_tiles() post-init

        self.tiletpl     = "%%%ds" % (padding[0] + 1)
        self.directions()

    def __iter__(self):
        return ( self[Loc(x, y)] for y in range(self.height) for x in range(self.width) )

    def tiles(self, *attrs):
        return ( t for t in self if all(getattr(t, attr) for attr in attrs) )

    def not_tiles(self, *attrs):
        return ( t for t in self if all(not getattr(t, attr) for attr in attrs) )

    def locations(self, *attrs):
        locs = (Loc(x, y) for y in range(self.height) for x in range(self.width))
        return (l for l in locs if all(getattr(self[loc], attr) for attr in attrs))

    def not_locations(self, *attrs):
        locs = (Loc(x, y) for y in range(self.height) for x in range(self.width))
        return ( l for l in locs if all(not getattr(self[loc], attr) for attr in attrs) )

    def ploc(self, tile_loc):
        """Parse location out of tile-or-loc `tile_loc`."""
        if isinstance(tile_loc, Loc) : return tile_loc
        else                         : return tile_loc.loc

    def draw(self, pause=None):
        pause = pause or self.pause_time
        print(nl * self.screen_sep)

        if self.num_grid:
            print(space, space*(self.xpad + 1), ujoin( range1(self.width), space, self.tiletpl ), nl * self.ypad)

        for n, row in enumerate1(self.board):
            args = [self.tiletpl % n] if self.num_grid else []
            if self.stackable:
                row = (tile[-1] for tile in row)
            args = [space] + args + [ujoin(row, space, self.tiletpl), nl * self.ypad]
            print(*args)

        self.status()
        sleep(pause)

    def status(self):
        pass

    def valid(self, loc):
        return bool( loc.x >= 0 and loc.y >= 0 and loc.x <= self.width-1 and loc.y <= self.height-1 )

    def directions(self):
        """Create list and dict of eight directions, going from up clockwise."""
        dirs          = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        self.dirlist  = [Dir(*d) for d in (dirs[0], dirs[2], dirs[4], dirs[6])]
        self.dirlist2 = [Dir(*d) for d in dirs]
        self.dirnames = dict(zip(self.dirlist2, "up ru right rd down ld left lu".split()))

    def neighbour_locs(self, tile_loc):
        """Return the generator of neighbour locations of `tile`."""
        x, y = self.ploc(tile_loc)
        coords = (-1,0,1)
        locs = set((x+n, y+m) for n in coords for m in coords) - set( [(x,y)] )
        return ( Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) )

    def neighbours(self, tile_loc):
        """Return the generator of neighbours of `tile`."""
        return (self[loc] for loc in self.neighbour_locs(tile_loc))

    def neighbour_cross_locs(self, tile_loc):
        """Return a generator of neighbour 'cross' (i.e. no diagonal) locations of `tile`."""
        x, y = self.ploc(tile_loc)
        locs = ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
        return [ Loc(*tpl) for tpl in locs if self.valid(Loc(*tpl)) ]

    def cross_neighbours(self, tile_loc):
        """Return the generator of 'cross' (i.e. no diagonal) neighbours of `tile`."""
        return (self[loc] for loc in self.neighbour_cross_locs(tile_loc))

    def make_tile(self, loc):
        """Make a tile using `self.def_tile`. If def_tile is simply a string, return it, otherwise instantiate with x, y as arguments."""
        return self.def_tile if isinstance(self.def_tile, basestring) else self.def_tile(loc)

    def move(self, tile_loc, newloc):
        loc          = self.ploc(tile_loc)
        item         = self[loc]
        self[newloc] = item
        self[loc]    = self.make_tile(loc)
        item.loc     = newloc

    def nextloc(self, tile_loc, dir, n=1):
        """Return location next to `tile_loc` point in direction `dir`."""
        loc = self.ploc(tile_loc)
        loc = Loc(loc.x + dir.x*n, loc.y + dir.y*n)
        return loc if self.valid(loc) else None

    def next_tile(self, tile_loc, dir, n=1):
        loc = self.nextloc(tile_loc, dir, n)
        return self[loc] if loc else None

    def dist(self, tile_loc1, tile_loc2):
        l1, l2 = self.ploc(tile_loc1), self.ploc(tile_loc2)
        return math.sqrt( abs(l2.x - l1.x)**2 + abs(l2.y - l1.y)**2  )


class Board(BaseBoard):
    def __init__(self, size, def_tile, **kwargs):
        super(Board, self).__init__(size, **kwargs)

        self.def_tile = def_tile
        xrng, yrng    = range(self.width), range(self.height)
        maketile      = self.make_tile if self.init_tiles else lambda loc: None

        self.board    = [ [maketile(Loc(x, y)) for x in xrng] for y in yrng ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x]

    def __setitem__(self, tile_loc, item):
        loc                      = self.ploc(tile_loc)
        self.board[loc.y][loc.x] = item

    def __delitem__(self, tile_loc):
        loc                      = self.ploc(tile_loc)
        self.board[loc.y][loc.x] = self.make_tile(loc)

    def place_tiles(self):
        for loc in self.locations():
            self[loc] = self.make_tile(loc)


class StackableBoard(BaseBoard):
    stackable = True

    def __init__(self, size, def_tile, **kwargs):
        super(StackableBoard, self).__init__(size, **kwargs)

        self.def_tile = def_tile
        xrng, yrng    = range(self.width), range(self.height)
        maketile      = self.make_tile if self.init_tiles else (lambda loc: None)

        self.board    = [ [[maketile(Loc(x, y))] for x in xrng] for y in yrng ]

    def __getitem__(self, loc):
        return self.board[loc.y][loc.x][-1]

    def __setitem__(self, tile_loc, item):
        loc = self.ploc(tile_loc)
        self.board[loc.y][loc.x].append(item)

    def __delitem__(self, tile_loc):
        loc = self.ploc(tile_loc)
        del self.board[loc.y][loc.x][-1]

    def place_tiles(self):
        for loc in self.locations():
            del self[loc]
            self[loc] = self.make_tile(loc)

    def items(self, tile_loc):
        loc = self.ploc(tile_loc)
        return self.board[loc.y][loc.x]

    def move(self, tile_loc, newloc):
        loc          = self.ploc(tile_loc)
        item         = self[loc]
        self[newloc] = item
        item.loc     = newloc
        self.items(loc).remove(item)
