#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
from random import random, randint
from utils import Dice, envelope, lastind, nl

blank  = '.'
char   = '@'
loc    = 0
length = 79
ahead  = 1
back   = -1
track  = [blank] * length


def move(dir, n):
    """Move `n` times in `dir` direction."""
    global loc
    track[loc] = blank

    loc = envelope(loc + dir*n, 0, lastind(track))
    track[loc] = char

def display():
    print(''.join(track), nl)

def demo1():
    print("demo1")
    display()
    track[loc] = char
    display()
    move(ahead, 10)
    display()
    move(back, 2)
    display()


# Part 2

loc2   = 0
track2 = [[blank] for _ in range(length)]

def move2(dir, n):
    global loc2
    track2[loc2].remove(char)

    loc2 = envelope(loc2 + dir*n, 0, lastind(track2))
    track2[loc2].append(char)

def display2():
    print( ''.join( x[-1] for x in track2 ), nl )

def demo2():
    print("demo2")

    display2()
    track2[loc2].append(char)
    move2(back, 10)
    display2()
    move2(ahead, 10)
    move2(back, 2)
    display2()

    dice = Dice()
    print(dice.roll())

    x = dice.rollsum()
    print("x =", x)
    move2(ahead, x)
    display2()


demo1()
demo2()
