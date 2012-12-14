#!/usr/bin/env python3

""" achief - simple and quick gamification
"""

import sys
from time import sleep
import os.path
import shelve
from utils import Container, getitem, lastind, nl, space

savefn     = "~/.achief.dat"
ranks      = "Page Squire Knight-Errant Knight Minister Chancellor".split()

badges     = '𝅪𝅫𝅬❖'
fullbadge  = badges[-1]
adv_badges = ('✬', 'ਠ', 'ತ', 'હ')


class Task(object):
    points = 0
    tpl = "%d points | level %d | rank %s"

    def __init__(self, name):
        self.name = name

    def add(self, n=1):
        self.points += n

    def remove(self, n=1):
        self.points = max(0, self.points - n)

    def display(self):
        level = self.points // 10
        rank  = getitem(ranks, level // 10, default=ranks[-1])
        print(self.tpl % (self.points, level, rank))
        print(self.get_badges(level))

    def get_badges(self, level):
        blvl = level % 12
        # number of full basic badges, type of last basic badge (may be 1,2,3 notches or full)
        num_full, last_badge = blvl//4, blvl%4


        last_badge = badges[last_badge-1] if last_badge else ''
        line       = fullbadge * num_full + last_badge

        lines      = self.advanced_badges(level)
        lines.append(space.join(line))
        return nl.join(l.center(8) for l in lines if l)

    def advanced_badges(self, level):
        # adv_blvl represents number of advanced badges at each level, e.g. [3,1,2,0] means 3 of
        # lowest-level advanced badges, 1 adv. badge at 2nd level, etc.
        num_levels = len(adv_badges)
        blevels    = [0] * num_levels
        blevels[0] = level // 12

        for n, levels in enumerate(blevels[:-1]):
            max_badges = num_levels - n
            blevels[n+1], blevels[n] = levels // max_badges, levels % max_badges

        numbered = reversed(list(enumerate(blevels)))
        lines    = [adv_badges[n] * count for n, count in numbered]

def test():
    for x in range(0, 500, 1):
        print(x)
        print(Task('x').get_badges(x), nl*5)


if __name__ == "__main__":
    try                      : test()
    except KeyboardInterrupt : sys.exit()
