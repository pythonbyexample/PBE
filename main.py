#!/usr/bin/env python

# Imports {{{
""" pytut game
dirs: 0:up; clockwise
"""

from random import randint, random
from time import sleep

import shared
from shared import *
from field import Field, Location, wall
from corridors import Corridors, Path
from things import Thing, Things
from rules import Rules

rule       = "lifend"
period     = 200
interval   = 0.1
num_things = 90
out        = open("out", 'w')
shared.out = out
# }}}


class Rectangle(object):
    def __init__(self, loc1, loc2):
        self.c1 = loc1
        self.c3 = loc2
        self.c2 = Location(loc2.x, loc1.y)
        self.c4 = Location(loc1.x, loc2.y)
        x1, x2, y1, y2 = loc1.x, loc2.x, loc1.y, loc2.y
        self.width, self.height = x2-x1+1, y2-y1+1
        self.center = x1 + int((x2-x1)/2), y1 + int((y2-y1)/2)

        # tunnel points, facing directions 0-3 (see main.py docstring)
        self.tpoints = [ [],[],[],[] ]
        for x in range(x1+1, x2):
            self.tpoints[0].append( (x, y1-1) )
            self.tpoints[2].append( (x, y2+1) )
        for y in range(y1+1, y2):
            self.tpoints[3].append( (x1-1, y) )
            self.tpoints[1].append( (x2+1, y) )

    def __str__(self):
        c1, c3 = self.c1, self.c3
        return "<size:%dx%d  x:%d-%d, y:%d-%d>" % (self.width, self.height, c1.x, c3.x, c1.y, c3.y)

    def intersect(self, r):
        ax1, ax2, bx1, bx2 = self.c1.x, self.c3.x, r.c1.x, r.c3.x
        ay1, ay2, by1, by2 = self.c1.y, self.c3.y, r.c1.y, r.c3.y
        return ax1 <= bx2 and ax2 >= bx1 and ay1 <= by2 and ay2 >= by1

    def larger(self):
        """Return rectangle one step larger in all directions."""
        c1, c3 = self.c1, self.c3
        return Rectangle( Location(c1.x-1, c1.y-1), Location(c3.x+1, c3.y+1) )

    def corner_values(self):
        return [fld.value(l) for l in (self.c1, self.c2, self.c3, self.c4)]

    def fill(self, ttype, alive=False):
        c1, c3 = self.c1, self.c3
        for y in range(c1.y, c3.y+1):
            for x in range(c1.x, c3.x+1):
                if ttype == ' ':
                    fld.remove(wall, Location(x,y))
                else:
                    Thing(fld, ttype, Location(x, y), alive)

    def near(self, x, y=None):
        """Is location on the border of the rectangle?"""
        x, y = unwrap(x, y)
        x1, y1 = self.c1.x, self.c1.y
        x2, y2 = self.c3.x, self.c3.y
        if (x+1 == x1 or x-1 == x2) and y1 <= y <= y2: return True
        if (y+1 == y1 or y-1 == y2) and x1 <= x <= x2: return True

    def rnd_perim_point(self):
        """ Return random point on the perimeter & direction facing away from the room.

            dirs: 0=up, clockwise
        """
        x1, y1 = self.c1.x, self.c1.y
        x2, y2 = self.c3.x, self.c3.y

        for _ in range(99):
            if roll():
                y = randint(y1+1, y2-1)
                if roll():
                    x = x1-1
                    dir = 3
                else:
                    x = x2
                    dir = 1
            else:
                x = randint(x1+1, x2-1)
                if roll():
                    y = y1-1
                    dir = 0
                else:
                    y = y2
                    dir = 2

            if fld.valid(x, y) and fld.value(x, y) == wall:
                return (x, y), dir


# ===============================================================================================

def reverse_dir(dir):
    """See main.py docstring."""
    if dir in (0,2): return 2 - dir
    if dir in (1,3): return 4 - dir

def add_walls():
    for x in range(5, 80, 4):
        L = Location
        locs = []
        for y in range(2, 10):
            locs.append(L(x,y))
            locs.append(L(x+1,y))
        for l in locs:
            Thing(fld, wall, l, False)


def add_rooms():
    L   = Location
    upper = 20 if random()>0.65 else 10
    num = randint(5, upper)
    lst = []
    writeln("num", num)

    for _ in range(num):
        loc1 = L(fld.random())
        maxx, maxy = 12, 7
        if random() > 0.8:
            maxx += randint(0,12)
            maxy += randint(0,7)
        loc3 = L( loc1.x + randint(4, maxx), loc1.y + randint(3, maxy) )
        if not fld.valid(loc3):
            continue
        if loc1.x==0 or loc1.y==0:
            continue
        if loc3.x==(fld.maxx-1) or loc3.y==(fld.maxy-1):
            continue

        rect = Rectangle(loc1, loc3)
        larger = rect.larger()
        if any(larger.intersect(r) for r in lst):
            continue
        rect.fill(' ')

        lst.append(rect)
    writeln2('_', _)
    return lst


def main():
    rules    = Rules()
    rulefunc = getattr(rules, rule)
    lastfld  = None
    # t = Thing(fld, cell, Location(0,0))
    # t.program = list("ddrrrull")
    # things.generate()
    rooms = add_rooms()
    # for r in rooms:
        # for l in r.tpoints: fld.put('*', Location(l))
    # print [str(r) for r in rooms]
    corridors = Corridors(fld, rooms)
    corridors.create()
    fld.display()
    return

    for i in range(period):
        rules.n = i
        for thing in things: thing.movep()
        # if p: t.movep()
        for location in fld:
            val = fld.value(location)
            rulefunc(fld, location, val, len(fld.live_neighbours(location)))

        fld.display()
        print ' ' + "%d/%d add:%d" % (i+1, period, rules.add)
        sleep(interval)
        lastfld = fld.field


if __name__ == "__main__":
    fld    = Field()
    things = Things()
    try: main()
    except KeyboardInterrupt: pass
