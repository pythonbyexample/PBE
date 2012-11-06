#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
from random import random, randint
from utils import Dice, envelope

blank   = '.'
char    = '@'
nl      = '\n'
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
    loc = envelope(loc + dir*n, lastind)
    track[loc] = char

def move2(dir, n):
    """Move `n` times in `dir` direction."""
    global loc2
    track2[loc2].remove(char)
    loc2 = envelope(loc2 + dir*n, lastind)
    track2[loc2].append(char)

def display():
    print(''.join(track), nl)

def display2():
    print(''.join(x[-1] for x in track2), nl)

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
    print(dice.roll(), dice.rollsum(), nl)

    x = dice.rollsum()
    print("x", x)
    move2(1, x)
    display2()

main()
