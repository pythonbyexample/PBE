#!/usr/bin/env python3

""" achief - simple and quick gamification
"""

import sys
from utils import Container, getitem, lastind, nl, space


savefn     = ".achief.dat"
ranks      = "Page Squire Knight-Errant Knight Minister Chancellor".split()

badges     = '𝅪𝅫𝅬❖'
adv_badges = ('✬', 'ਠ', 'ತ', 'હ')


class Task(object):
    points = 0
    tpl = "%d points | level %d | rank %s |"

    def __init__(self, name):
        self.name = name

    def add(self, n=1):
        self.points += n

    def remove(self, n=1):
        self.points = max(0, self.points - n)

    def display(self):
        level               = self.points // 10
        rank                = getitem(ranks, level // 10, default=ranks[-1])

    def get_badges(self, level):
        adv_blvl           = [0] * len(adv_badges)
        adv_blvl[0], blvl  = level//12, level%12
        blvlmax, blvl_last = blvl//4, blvl%4

        for n in range(len(adv_blvl)):
            if n == lastind(adv_blvl):
                break
            m = len(adv_blvl) - n
            adv_blvl[n+1], adv_blvl[n] = adv_blvl[n] // m, adv_blvl[n] % m

        lines = [adv_badges[n] * num for n, num in reversed(list(enumerate(adv_blvl)))]
        last = badges[blvl_last-1] if blvl_last else ''

        line = badges[-1] * blvlmax + last
        lines.append(space.join(line))

        return nl.join(l.center(8) for l in lines if l)



def test():
    for x in range(0, 500, 1):
        print(x)
        print(Task('x').get_badges(x), nl*5)



if __name__ == "__main__":
    try                      : test()
    except KeyboardInterrupt : sys.exit()
