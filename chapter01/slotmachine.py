#!/usr/bin/env python3

""" slot machine game
"""

from random import randint
from time import sleep
from utils import Loop, first, sjoin, nl

num_reels  = 3
pause_time = 0
pause_time = 0.05
winmsg     = "You've won!! Collect your prize : %d"

symbols = {
    '𝅪': 100,
    '𝅫': 200,
    '𝅬': 500,
    '❖': 1000,
    '✬': 2000,
    # 'ਠ': 5000,
    # 'હ': 10000,
    # 'ತ': 25000,
 }


class SlotMachine(object):
    def run(self):
        rotations    = [randint(1,5) for _ in range(num_reels)]    # reel rotations per cycle
        total_cycles = [randint(x,x+20) for x in range(50, 50 + 20*num_reels + 1, 20)]
        reels        = [Loop(symbols.keys(), name="symbol") for _ in range(num_reels)]
        cycle        = 0

        while True:
            L            = zip(reels, rotations, total_cycles)
            line = [self.rotate(reel, n, cycle, max_cycle) for reel, n, max_cycle in L]

            print(nl*5, sjoin(line))
            cycle += 1
            if cycle >= total_cycles[-1]: break
            sleep(pause_time)

        if len(set(w.symbol for w in reels)) == 1:
            symbol = first(reels).symbol
            print(winmsg % symbols[symbol])
            return True

    def rotate(self, reel, n, cycle, max_cycle):
        return reel.next(n) if (cycle <= max_cycle) else reel.symbol


if __name__ == "__main__":
    SlotMachine().run()
