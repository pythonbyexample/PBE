#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
from random import random, randint

blank   = '.'
char    = '@'
loc     = 0
loc2    = 0

length  = 150
lastind = length - 1

track   = [blank]*length
track2  = [[blank] for _ in range(length)]


def move(dir, n):
    """Move `n` times in `dir` direction."""
    global loc
    track[loc] = blank
    loc = envelope(loc + dir*n)
    track[loc] = char

def move2(dir, n):
    """Move `n` times in `dir` direction."""
    global loc2
    track2[loc2].remove(char)
    loc2 = envelope(loc2 + dir*n)
    track2[loc2].append(char)

def display():
    print(''.join(track)); print()

def display2():
    print(''.join( [x[-1] for x in track2] ))
    print()

def envelope(loc):
    """Return `loc`, fixing out of bounds values if needed."""
    if loc < 0         : return 0
    elif loc > lastind : return lastind
    return loc


class Dice(object):
    def __init__(self, num=2, sides=6):
        self.num   = num
        self.sides = sides

    def roll(self):
        return [randint(1, self.sides) for _ in range(self.num)]

    def rollsum(self):
        return sum(self.roll())


def main():
    display()
    track[loc] = char
    display()
    move(1, 10)
    move(-1, 2)
    display()

    display2()
    track2[loc2].append(char)
    move2(-1, 10)
    display2()
    move2(1, 10)
    move2(-1, 2)
    display2()

    dice = Dice()
    print(dice.roll())
    print(dice.rollsum())
    print()

    x = dice.rollsum()
    print("x", x)
    move2(1, x)
    display2()


main()
