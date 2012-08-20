#!/usr/bin/env python

# Imports {{{
import sys
from random import randint
from copy import deepcopy

from shared import *

dimensions = 8, 8
# }}}



class Loc(object):
    def __init__(self, x, y=None):
        x, y = unwrap(x, y)
        self.loc = x, y
        self.x, self.y = x, y

    def __str__(self):
        return str(self.loc)

    def __repr__(self):
        return str(self.loc)

    def __iter__(self):
        return iter(self.loc)

    def move(self, dir):
        self.x += dir[0]
        self.y += dir[1]
        self.loc = self.x, self.y

    def valid(self):
        from reversi import dimensions
        return bool( 0 <= self.x < dimensions[0] and 0 <= self.y < dimensions[1] )
