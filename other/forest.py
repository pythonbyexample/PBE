#!/usr/bin/env python

from random import random, choice
from string import join
from time import sleep

period = 500


class Soil(object):
    weight = 10000


class Tree(object):
    age    = 0
    maxage = 3000
    weight = 50

    def __str__(self):
        return "<Tree: %d>" % self.weight

    def grow(self):
        """Grow unless tree dies of old age or a random death."""
        self.age += 1
        if self.age == self.maxage:
            self.die()
            return
        if not self.survive_roll():
            return
        self.weight += 10
        soil.weight -= 10

    def survive_roll(self):
        if random() > 0.99:
            self.die()
        else:
            return 1

    def die(self):
        trees.remove(self)
        soil.weight += self.weight


class Insect(object):
    age    = 0
    maxage = 4
    weight = 1

    def __str__(self):
        return "<Insect %d: %d>" % (id(self), self.weight)

    def eat(self):
        """Eat unless insect dies of old age or a random death."""
        self.age += 1
        if self.age == self.maxage:
            self.die()
            return
        if not self.survive_roll():
            return
        choice(trees).weight -= 1
        self.weight += 1

    def survive_roll(self):
        if random() > 0.85:
            self.die()
        else:
            return 1

    def die(self):
        insects.remove(self)
        soil.weight += self.weight


def joins(iterable):
    return join([str(x) for x in iterable])

def display(cycle):
    print '\n'*35
    print "[%d/%d] soil: %d" % (cycle, period, soil.weight),
    print "oldest tree: %d" % sorted([t.age for t in trees])[-1]
    print "%d trees (weights): %s" % (len(trees), joins( sorted([t.weight for t in trees]) ))
    print "%d insects (weights): %s" % (len(insects), joins( sorted([i.weight for i in insects]) ))
    sleep(0.1)

def main():
    for x in range(period):
        for tree in trees: tree.grow()
        for insect in insects: insect.eat()

        if random() > 0.9: trees.append(Tree())
        insects.extend([Insect() for _ in range(10)])
        display(x+1)


soil    = Soil()
trees   = [Tree() for _ in range(10)]
insects = [Insect() for _ in range(150)]


if __name__ == "__main__":
    main()
