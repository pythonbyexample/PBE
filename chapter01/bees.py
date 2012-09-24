#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
from random import random, choice, randint
from time import sleep

init_bees   = 100
init_wasps  = 5
num_flowers = 500
turns       = 500


class Hive(object):
    honey = 5

    def __init__(self):
        self.bees = [Bee() for _ in range(init_bees)]

    def new_bee(self):
        if random() >= 0.8:
            self.bees.append(Bee())

class Bee(object):
    nectar      = 0
    max_nectar  = 80
    max_flowers = 100

    def go(self):
        visited = 0
        while visited < self.max_flowers and self.nectar < self.max_nectar:
            flower = choice(flowers)
            self.nectar += flower.get_nectar()
            visited += 1

        hive.honey += int(self.nectar/10)
        self.nectar = 0

class Flower(object):
    nectar = 5

    def go(self):
        self.nectar += randint(1,3)

    def get_nectar(self):
        nectar = 1 if self.nectar else 0
        self.nectar -= nectar
        return nectar

class Wasp(object):
    def go(self):
        if hive.bees:
            bee = choice(hive.bees)
            if random() >= 0.8:
                if random() >= 0.2 : hive.bees.remove(bee)
                else               : wasps.remove(self)

def main():
    for turn in range(turns):
        for x in hive.bees + wasps + flowers:
            x.go()

        hive.new_bee()
        if random() >= 0.95: wasps.append(Wasp())

        status = "[%3s]   %6s honey   %3s bees   %d wasps"
        print(status % (turn, hive.honey, len(hive.bees), len(wasps)))
        sleep(0.1)


if __name__ == "__main__":
    hive    = Hive()
    flowers = [Flower() for _ in range(num_flowers)]
    wasps   = [Wasp() for _ in range(init_wasps)]
    main()
