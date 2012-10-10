#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
from random import random

class Tree(object):
    height = 0

    def __repr__(self):
        return "<'%s' tree, %.1fft>" % (self.__class__.__name__, self.height)

    def grow(self):
        self.height += self.growth_rate + self.growth_rate * random() / 3

class Bamboo(Tree):
    growth_rate = 10

class Birch(Tree):
    growth_rate = 1.2


def main():
    trees = Bamboo(), Bamboo(), Birch(), Birch()
    print(trees, '\n')

    for tree in trees: tree.grow()
    print(trees, '\n')

    for _ in range(5):
        for tree in trees: tree.grow()
    print(trees, '\n')


main()
