import itertools
from random import random, choice, randint

from field import wall, Location
from shared import *
"""
Simplify path finding? * available starting points; - and |: available doorways

   |*
   |*
   #
--##
**


     **
   ##--
   #
  *|

"""


class Path(object):
    def __init__(self):
        self.path = []

    @classmethod
    def clear(cls, fld, path, val=None):
        for l in path:
            if val: fld.put(val, Location(l))
            else: fld.remove(wall, Location(l))

    @classmethod
    def random(cls, fld, rooms):
        """Random path to connect any 2 rooms."""
        room = choice(rooms)
        loc_dir = room.rnd_perim_point()
        if not loc_dir: return
        loc, dir = loc_dir
        path = [loc]
        while 1:
            loc = cls.next(loc, dir)
            path.append(loc)
            if not fld.valid(loc) or fld.empty(loc):
                break
            if fld.near_border(loc):
                break
            if any(r.near(loc) and r!=room for r in rooms):
                cls.clear(fld, path)
                return True
            nb = fld.all_neighbours(loc)
            if any([n==' ' for n in nb]):
                break
            if len(path)>3 and cls.near(path[:-3], loc):
                break
            if random() > 0.9:
                dir = cls.turn_dir(dir)

    @classmethod
    def next(cls, loc, dir):
        x, y = loc
        if   dir == 0: return x, y-1
        elif dir == 1: return x+1, y
        elif dir == 2: return x, y+1
        elif dir == 3: return x-1, y

    @classmethod
    def turn_dir(cls, dir):
        """Return random direction perpendicular to `dir`."""
        dirs = ((0,2), (1,3))
        return choice( dirs[0 if dir in dirs[1] else 1] )

    @classmethod
    def near(cls, path, loc):
        x, y = loc
        for x2, y2 in path:
            if abs(x-x2) == 1 and abs(y-y2) == 1:
                return True


    def extend(self, x, y, axis, end, step):
        """Extend `path` by stepping through from `loc` to `end` along `axis`, using `step`."""
        # if axis : seg = [(x,y) for y in range(min(y,y2), max(y,y2)+1)]
        # else    : self.path.extend([(x,y) for x in range(min(x,x2), max(x,x2)+1)])
        if axis : self.path.extend([(x,y) for y in range(y, end+step, step)])
        else    : self.path.extend([(x,y) for x in range(x, end+step, step)])
        return self.path[-1]

    def create(self, r1, r2):
        """ Connect two rooms with a corridor.
            corners: c1 is upper left; clockwise
        """
        if r1.c1.x > r2.c1.x:
            r1, r2 = r2, r1

        c2, c3 = r1.c2, r1.c3
        x = c2.x + 1
        c1, c4 = r2.c1, r2.c4
        mode = 3
        if   c1.x-x >= 5    : mode = 1
        elif 0 < c1.x-x < 5 : mode = 2

        y = randint(c2.y+1, c3.y-1)

        modes = (self.mode1, self.mode2, self.mode3)
        modes[mode-1](x, y, r1, r2, c1, c2, c4)
        return self.path

    def mode1(self, x, y, r1, r2, c1, c2, c4):
        """mode 1: right, down, right"""
        x2 = c1.x-1
        y2 = randint(c1.y+1, c4.y-1)
        self.path.append((x,y))
        x += 1

        step = 1 if y<y2 else -1
        x, y = self.extend(x, y, 1, y2, step)
        self.extend(x, y, 0, x2, 1)

    def mode2(self, x, y, r1, r2, c1, c2, c4):
        """mode 2: right, down"""
        c2 = r2.c2
        y2 = c2.y + 1
        x2 = randint(c1.x+1, c2.x-1)
        self.path.append((x,y))
        x += 1

        x, y = self.extend(x, y, 0, x2, 1)
        step = 1 if y<y2 else -1
        self.extend(x, y, 1, y2, step)

    def mode3(self, x, y, r1, r2, c1, c2, c4):
        """mode 3: down, left/right, down OR just down"""
        if r1.c1.y > r2.c1.y: r1,r2 = r2,r1
        y  = r1.c3.y + 1
        y2 = r2.c1.y - 1

        if abs(y-y2) < 2:

            # find x axis line common to both rooms
            xset = set( range(r1.c1.x, r1.c2.x) )
            x2set = set( range(r2.c1.x, r2.c2.x) )
            intersection = list(xset & x2set)
            if intersection:
                self.extend(choice(intersection), y, 1, y2, 1)
            else:
                # horizontally right next to each other, tunnel down from corner to corner
                x = max(r1.c1.x, r2.c1.x)
                self.extend(x, y-1, 1, r2.c2.y, 1)
        else:
            x  = randint(r1.c4.x+1, r1.c3.x-1)
            x2 = randint(r2.c1.x+1, r2.c2.x-1)
            self.path.append((x,y))
            y += 1

            step = 1 if x<x2 else -1
            if x != x2:
                x, y = self.extend(x, y, 0, x2, step)
            self.extend(x, y, 1, y2, 1)


class Corridors(object):
    def __init__(self, fld, rooms):
        self.fld = fld
        self.rooms = rooms

    def find_closest(self, room, rooms):
        """UNUSED"""
        distances = sorted( [(dist(room.center, r.center), r) for r in rooms] )
        return distances[0][1]

    def create(self):
        """ Connect rooms with corridors.

            - create all possible combinations of each 2 rooms
            - while there are unconnected rooms, connect closest connected and unconnected room
            - add one random corridor
        """
        rcomb = [set(x) for x in itertools.combinations(self.rooms, 2)]
        connected, unconnected = [self.rooms[0]], self.rooms[1:]

        while unconnected:
            room_dist = []

            # create dist/room list for pairs of unconnected/connected rooms
            for r1, r2 in rcomb:
                if r1 in connected and r2 in connected     : continue
                if r1 in unconnected and r2 in unconnected : continue
                room_dist.append( (dist(r1.center, r2.center), (r1,r2)) )

            # get closest rooms and set r1 to unconnected
            r1, r2 = sorted(room_dist)[0][1]
            if r1 in connected: r1,r2 = r2,r1

            self.connect_rooms(r1, r2)
            connected.append(r1)
            unconnected.remove(r1)

        if random() > 0.4:
            for _ in range(99):
                if Path.random(self.fld, self.rooms): break

    def connect_rooms(self, r1, r2):
        Path.clear( self.fld, Path().create(r1, r2) )
