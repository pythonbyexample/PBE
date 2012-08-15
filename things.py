from random import randint
from shared import *


class Thing(object):
    def __init__(self, field, ttype, location, alive=True):
        self.loc      = location
        self.ttype    = ttype
        self.field    = field
        self.program  = []
        self.movement = 1.5
        self.alive    = alive
        self.is_wall  = bool(self.ttype==wall)
        field.put(self)

    def __str__(self):
        return self.ttype

    def remove(self):
        self.field.remove(self)
        things.remove(self)

    def movep(self):
        """If we have a program, try to move the next step in it."""
        if self.program:
            dir = self.program[0]
            if self.move(dir) and self.program:
                del self.program[0]
            self.movement += 1

    def move(self, direction):
        """ Move in `direction` if enough movement points are available
            If path is blocked, remove all immediate moves in the same direction.
        """
        dirs = dict(r=0, l=1, d=2, u=3, ru=4, rd=5, ld=6, lu=7)
        if isinstance(direction, str):
            direction = dirs[direction]

        cost = 1 if direction<4 else 1.5
        if self.movement >= cost:
            newloc = self.field.move(direction, self.loc, self)
            if newloc:
                self.loc = newloc
            else:
                self.program_removedir(direction)
            self.movement -= cost
            return True

    def program_removedir(self, direction):
        """Remove all immediate movement in `direction`."""
        p = self.program
        while p and p[0] == direction:
            del p[0]

    def randprogram(self, length):
        """Generate random move program of given `length`, consisting of segments of random length (from 1 to 5)."""
        p = []
        while len(p) < length:
            p.extend( [randint(0,7)] * randint(1,6) )
        self.program = p[:length]

    def neighbours(self):
        return self.field.neighbours(self.loc)

    def live_neighbours(self):
        return self.field.live_neighbours(self.loc)


class Things(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.lst = []

    def remove(self, thing):
        self.lst.remove(thing)

    def __iter__(self):
        return iter(self.lst)

    def append(self, t):
        self.lst.append(t)

    def generate(self):
        for _ in range(num_things):
            t = Thing(fld, cell, fld.random_empty())
            t.randprogram(randint(10,100))
            self.append(t)
