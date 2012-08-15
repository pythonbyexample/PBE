#!/usr/bin/env python

# Imports {{{
import math
from string import join
from random import randint
# }}}

def unwrap(x, y=None):
    return x if y==None else (x,y)

def joins(iterable, sep=' '):
    return join([unicode(x) for x in iterable], sep)

def joinst(iterable, sep=' '):
    """Join iterable elements, converted to string, using last (top) item of list elements."""
    return join([unicode(x[-1]) for x in iterable], sep)

def close(val, val2, val3):
    """Is val close to either val2 or val3?"""
    if abs(val-val2) <= 1 or abs(val-val3) <= 1: return True

def writeln(*args):
    out.write(joins(args) + '\n')

def writeln2(*args):
    writeln(*args)
    writeln()

def dist(loc1, loc2):
    x1,y1 = loc1
    x2,y2 = loc2
    return math.sqrt(abs(x2-x1)**2 + abs(y2-y1)**2)

def roll():
    return randint(0, 1)
