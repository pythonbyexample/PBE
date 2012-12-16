#!/usr/bin/env python3

""" achief - simple and quick gamification
"""

import sys
from time import sleep
import os.path
import shelve
from optparse import OptionParser

from utils import Container, getitem, lastind, nl, space

savefn        = "~/.achief.dat"
ranks         = "Page Squire Knight-Errant Knight Minister Chancellor".split()

badges        = '𝅪𝅫𝅬❖'
fullbadge     = badges[-1]
adv_badges    = ('✬', 'ਠ', 'હ', 'ತ')
last_task_key = "ACHIEF_LAST_TASK"


class Task(object):
    points = level = 0
    tpl    = "%d points | level %d | rank %s"

    def __init__(self, name):
        self.name = name

    def add(self, n=1):
        self.points = max(0, self.points + n)
        self.level  = self.points // 10

    def display(self):
        rank  = getitem(ranks, self.level // 10, default=ranks[-1])
        print(self.tpl % (self.points, self.level, rank))
        print(self.get_badges(self.level))

    def get_badges(self, level):
        lines = self.advanced_badges(level) + [ self.basic_badges(level) ]
        lines = [space.join(line) for line in lines]

        return nl.join(l.center(16) for l in lines if l)

    def basic_badges(self, level):
        blvl = level % 12

        # number of full basic badges, type of last basic badge (may be 1,2,3 notches or full)
        num_full, last_badge = blvl//4, blvl%4

        last_badge = badges[last_badge-1] if last_badge else ''
        return fullbadge * num_full + last_badge

    def advanced_badges(self, level):
        """Pyramid is filled out at level=1339."""
        # adv_blvl represents number of advanced badges at each level, e.g. [3,1,2,0] means 3 of
        # lowest-level advanced badges, 1 adv. badge at 2nd level, etc.
        num_levels = len(adv_badges)
        blevels    = [0] * num_levels
        blevels[0] = level // 12

        for n, levels in enumerate(blevels[:-1]):
            max_badges = num_levels - n + 1
            blevels[n+1], blevels[n] = blevels[n] // max_badges, blevels[n] % max_badges

        numbered = reversed(list(enumerate(blevels)))
        return [adv_badges[n] * count for n, count in numbered]


class Tasks(object):
    tpl = "%15s %5d %5d"

    def __init__(self):
        self.tasks = shelve.open(os.path.expanduser(savefn))
        self.last  = self.tasks.get(last_task_key)

    def close(self):
        self.tasks.close()
        self.tasks[last_task_key] = self.last

    def new(self, name):
        self.tasks[name] = Task(name)

    def delete(self, name):
        if name in self.tasks:
            del self.tasks[name]

    def add(self, name, n=1):
        if name not in self.tasks:
            self.new(name)
        self.tasks[name].add(n)
        self.last = name

    def list(self):
        for task in self.tasks.values():
            print(self.tpl % (task.name, task.points, task.level))

def test():
    print(Task('x').get_badges(1439), nl*5)

    for x in range(0, 5000, 10):
        print(x)
        print(Task('x').get_badges(x), nl*5)


if __name__ == "__main__":
    tasks = Tasks()
    arg1  = getitem(sys.argv, 1, default=tasks.last)
    arg2  = getitem(sys.argv, 2, default='1')

    parser = OptionParser()
    parser.add_option("-n", "--num", dest="num", help="Number of cards to show.",
      default=0)
    options, args = parser.parse_args()
    if not args:
        print "Need one arg."; sys.exit()

    if arg1 == '-d':
        tasks.delete(arg2)
    else:
        try               : tasks.add(arg1, int(arg2))
        except ValueError : print "Invalid argument"
