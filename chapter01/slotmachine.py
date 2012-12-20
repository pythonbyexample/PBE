#!/usr/bin/env python3

""" slot machine game
"""

from random import randint
from time import sleep
from utils import Loop, first, sjoin, nl

num_wheels = 3
pause_time = 0
pause_time = 0.05
winmsg     = "You've won!! Collect your prize : %d"

tiles = {
    '𝅪': 100,
    '𝅫': 200,
    '𝅬': 500,
    # '❖': 1000,
    # '✬': 2000,
    # 'ਠ': 5000,
    # 'હ': 10000,
    # 'ತ': 25000,
 }


class SlotMachine(object):
    def run(self):
        rotations    = [randint(1,5) for _ in range(num_wheels)]    # wheel rotations per cycle
        total_cycles = [randint(x,x+20) for x in range(50, 50 + 20*num_wheels + 1, 20)]
        wheels       = [Loop(tiles.keys(), name="tile") for _ in range(num_wheels)]
        cycle        = 0

        while True:
            L       = zip(wheels, rotations, total_cycles)
            current = [self.rotate(wheel, n, cycle, max_cycle) for wheel, n, max_cycle in L]

            print(nl*5, sjoin(current))
            sleep(pause_time)
            cycle += 1
            if cycle >= total_cycles[-1]: break

        if len(set(w.tile for w in wheels)) == 1:
            tile = first(wheels).tile
            print(winmsg % tiles[tile])
            return True

    def rotate(self, wheel, n, cycle, max_cycle):
        return wheel.next(n) if (cycle <= max_cycle) else wheel.item


if __name__ == "__main__":
    SlotMachine().run()
