#!/usr/bin/env python3

""" achief - simple and quick way to gamify tasks and activities
"""

import os.path
import shelve
from argparse import ArgumentParser

from utils import first, getitem, nl, space

savefn         = "~/.achief.dat"
ranks          = "Page Squire Knight-Errant Knight Minister Chancellor Imperator".split()

badges         = '𝅪𝅫𝅬❖'
fullbadge      = badges[-1]
adv_badges     = ('✬', 'ਠ', 'હ', 'ತ')
badge_modifier = 1                      # set higher to get badges quicker
lev_per_rank   = 200


class Task(object):
    points = level = 0
    tpl    = "[%d] level %d | %s\n"

    def __init__(self, name):
        self.name = name

    def add(self, n=1):
        self.points = max(0, self.points + n)
        self.level  = self.points // 10

    def display(self):
        rank  = getitem(ranks, self.level // lev_per_rank, default=ranks[-1])
        print(self.tpl % (self.points, self.level, rank))
        print(self.get_badges(self.level))

    def get_badges(self, level):
        level *= badge_modifier
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
    tpl = "%-15s %5s %5s"

    def __init__(self):
        self.data  = shelve.open(os.path.expanduser(savefn))
        self.tasks = self.data.get("tasks", dict())
        self.last  = self.data.get("last", None)

    def close(self):
        self.data["tasks"] = self.tasks
        self.data["last"] = self.last
        self.data.close()

    def new(self, name):
        self.tasks[name] = Task(name)

    def delete(self, name):
        if name in self.tasks:
            del self.tasks[name]
            print("'%s' deleted" % name)
            self.close()

    def show(self, name):
        if name in self.tasks:
            self.tasks[name].display()

    def add(self, name, n=1):
        """Add `n` points to `name` task."""
        if name not in self.tasks:
            self.new(name)
        self.tasks[name].add(n)
        self.last = name
        self.show(name)
        self.close()

    def list(self):
        print(self.tpl % ("task", "points", "level"))
        for task in self.tasks.values():
            print(self.tpl % (task.name, task.points, task.level))

def test():
    print(Task('x').get_badges(1439), nl*5)

    for x in range(0, 5000, 10):
        print(x)
        print(Task('x').get_badges(x), nl*5)


if __name__ == "__main__":
    tasks  = Tasks()

    parser = ArgumentParser()
    parser.add_argument("task", metavar="TASK", default=None, nargs='?')
    parser.add_argument("points", metavar="N", type=int, default=1, nargs='?')
    parser.add_argument('-d', "--delete", metavar="TASK", dest="del_task", help="Delete task #", default=None)
    parser.add_argument("-s", "--show", metavar="TASK", dest="show", help="Show task rank and badges", default=False)
    parser.add_argument("-l", "--list", dest="list", help="List tasks", action="store_const", const=True, default=False)
    args = parser.parse_args()

    if   args.del_task : tasks.delete(args.del_task)
    elif args.show     : tasks.show(args.show)
    elif args.list     : tasks.list()
    # else: print(sys.argv)
    elif args.task     : tasks.add(args.task, args.points)
