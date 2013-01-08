#!/usr/bin/env python3

from random import shuffle

scaleorder = int(raw_input('Please enter a number for an n*n square: '))
topleft    = int(raw_input('Please enter the top left number for the square: '))
firstrow   = range(topleft, scaleorder+topleft)
shuffle(firstrow)

print firstrow
