#!/usr/bin/env python3

""" achief - simple and quick way to gamify tasks and activities.
"""

import os.path
import shelve
from argparse import ArgumentParser
from collections import defaultdict

from utils import iround, getitem, nl, space

savefn          = "~/.achief.dat"
ranks           = "Page Squire Knight-Errant Knight Minister Chancellor Imperator".split()

div             = '-' * 60
badges          = '𝅪𝅫𝅬❖'
fullbadge       = badges[-1]
adv_badges      = ('✬', 'ਠ', 'હ', 'ತ')
badge_modifier  = 1                      # set higher to get badges quicker
levels_per_rank = 200


class Task(object):
    points = 0
    tpl    = "[%d] level %d | %s\n"

    def add(self, n=1):
        self.points = max(0, self.points + n)
        self.level  = 1 + self.points // 10
        self.rank   = getitem(ranks, self.level // levels_per_rank, default=ranks[-1])

    def display(self):
        print(self.tpl % (self.points, self.level, self.rank))
        print(self.get_badges(self.level), nl)

    def get_badges(self, level):
        level = iround(level*badge_modifier)
        lines = self.advanced_badges(level) + [ self.basic_badges(level) ]
        lines = [space.join(line) for line in lines]

        return nl.join(l.center(16) for l in lines if l)

    def basic_badges(self, level):
        blvl = level % 12

        # number of full basic badges, level of last basic badge (may be 1,2,3 notches)
        num_full, last_badge = blvl//4, blvl%4

        last_badge = badges[last_badge-1] if last_badge else ''
        return fullbadge * num_full + last_badge

    def advanced_badges(self, level):
        """Complete pyramid is filled out at level=1339."""
        num_levels = len(adv_badges)
        blevels    = [0] * num_levels   # number of adv. badges at each level
        blevels[0] = level // 12

        for n, levels in enumerate(blevels[:-1]):
            max_badges = num_levels - n + 1
            blevels[n+1], blevels[n] = blevels[n] // max_badges, blevels[n] % max_badges

        numbered = reversed(list(enumerate(blevels)))
        return [adv_badges[n] * count for n, count in numbered]


class Tasks(object):
    tpl = " %-15s %7s %7s %20s"

    def __init__(self):
        data  = shelve.open(os.path.expanduser(savefn), writeback=True)
        if "tasks" not in data:
            data["tasks"] = defaultdict(Task)

        self.tasks = data.get("tasks")
        self.data  = data

    def delete(self, name):
        if name in self.tasks:
            del self.tasks[name]
            print("'%s' deleted" % name)

    def show(self, name):
        if name in self.tasks:
            self.tasks[name].display()

    def add(self, name, n=1):
        """Add `n` points to `name` task."""
        self.tasks[name].add(n)
        self.show(name)

    def list(self):
        print(self.tpl % ("task", "points", "level", "rank"), nl + div)
        for name, task in sorted(self.tasks.items()):
            print(self.tpl % (name, task.points, task.level, task.rank))

    def close(self):
        self.data.close()


def test():
    for x in range(0, 1500, 10):
        print(x, Task('x').get_badges(x), nl*5)


if __name__ == "__main__":
    tasks  = Tasks()
    parser = ArgumentParser()

    parser.add_argument("task", default=None, nargs='?')
    parser.add_argument("points", type=int, default=1, nargs='?')

    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-s", "--show", metavar="TASK", default=False)
    parser.add_argument('-d', "--delete", metavar="TASK", default=False)
    args = parser.parse_args()

    if   args.delete   : tasks.delete(args.delete)
    elif args.show     : tasks.show(args.show)
    elif args.list     : tasks.list()
    elif args.task     : tasks.add(args.task, args.points)
    tasks.close()
