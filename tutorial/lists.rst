Python Lists
============

A list is one of the most important data structures in Python. In this small tutorial I will go
over the methods, tricks, and examples of using lists in your programs.

https://github.com/pythonbyexample/PBE/tree/master/code/slotmachine.py

To run SlotMachine, you will also need to download 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/utils.py

Reel
----

The `Reel` class represents a single reel, or 'drum', inside the machine, which
rotates independently from other reels when the machine is running. It would be easy to make a
random display of symbols while the reels are spinning and make a final random selection when
it stops, but I think it's more interesting to make a more realistic simulation and have the
reels that are actually rotating in the same sequence. To make sure changing symbols of
different reels are not synchronized, I'll have them rotating at randomized, different speeds.

As in a real slot machine, I'll stop the reels in a delayed order from left to right, using
randomly generated `max_cycle` variable to let them know when to stop.

I'll use the `utils.Loop` class to store the list of symbols and cycle through them using
`Loop.next()` method. The `symbol()` method will rotate the reel if it did not reach `max_cycle` yet
and return the current symbol:

.. sourcecode:: python

    class Reel(object):
        def __init__(self, rotations, max_cycle):
            self.reel      = Loop(symbols.keys(), name="symbol")
            self.rotations = rotations
            self.max_cycle = max_cycle

        def symbol(self, cycle=0):
            if cycle and cycle <= self.max_cycle:
                self.rotate()
            return self.reel.symbol

        def rotate(self): self.reel.next(self.rotations)

SlotMachine
-----------

The `run()` method sets up the machine and runs it until all reels come to a stop.

I'll need to create a `rotation` and `max_cycle` values for each of the reels and then create the
reel objects themselves.

In the main loop itself I need to join all symbols into a line, display it and pause.

.. sourcecode:: python

    num_reels  = 3
    pause_time = 0.05
    first_stop = 30     # stop first reel
    reel_delay = 25     # range of delay to stop each reel

    class SlotMachine(object):
        def run(self, pause_time, display=True):
            """Run the machine, return tuple of (symbol line, win_amount)."""

            rotations    = [randint(1,4) for _ in range(num_reels)]    # reel rotations per cycle
            rd           = reel_delay
            total_cycles = [randint(x, x+rd) for x in range(first_stop, first_stop + rd*num_reels, rd)]

            reels        = [Reel(rotations, max_cycle) for rotations, max_cycle in zip(rotations, total_cycles)]

            for cycle in range1(max(total_cycles)):
                line = sjoin( [reel.symbol(cycle) for reel in reels] )
                if display: print(nl*5, line)
                sleep(pause_time)

            return self.done(reels, display, line)


In the `done()` method, I have to check if all of the reels aligned with the same symbol by
turning the line into a set (therefore eliminating duplicates) and checking if its length is 1:

.. sourcecode:: python

    def done(self, reels, display, line):
        S      = [r.symbol() for r in reels]
        won    = bool(len(set(S)) == 1)
        amount = symbols[first(S)] if won else 0

        if won and display:
            print(winmsg % symbols[first(S)])
        return line, amount

test()
------

In the test mode, the machine will run 300 times without printing out the lines or pausing, at
the end some statistics are added up and displayed. This is a good illustration of making a
small program that may be reused by a different program (which may not want to print out all
lines for each run).

.. sourcecode:: python

    def test():
        slots   = SlotMachine()
        runs    = [slots.run(0, False) for _ in range(300)]
        wins    = len([r for r in runs if r[1]])
        total   = sum(r[1] for r in runs)
        showall = True

        for run in runs:
            if showall or run[1]:
                print("%8s %6s" % run, nl)
        print(" wins", wins)
        print(" total", total)


Settings
--------

You can change the symbols and related winnings, as well as a few other settings as described
in the comments below:

.. sourcecode:: python

    num_reels  = 3
    pause_time = 0.05
    first_stop = 30     # stop first reel
    reel_delay = 25     # range of delay to stop each reel
    winmsg     = "You've won!! Collect your prize : %d"

    symbols = {
        '❄': 100,
        '⌘': 200,
        '✿': 500,
        '❖': 1000,
        '✬': 2500,
     }

Screenshots
-----------

The winning rate is about 3%; here is the tail end of `test()` run::

    ❄ ❄ ❄    100

    ❖ ⌘ ❖      0

    ⌘ ⌘ ✿      0

    ✿ ❄ ⌘      0

    ❖ ⌘ ✿      0

    ❖ ❖ ✿      0

    ❄ ❄ ✿      0

    ❄ ✿ ⌘      0

    wins 10
    total 8300

Here is the test run with `showall=False`::

    ✿ ✿ ✿    500

    ❖ ❖ ❖   1000

    ⌘ ⌘ ⌘    200

    ⌘ ⌘ ⌘    200

    ❖ ❖ ❖   1000

    ❖ ❖ ❖   1000

    wins 6
    total 3900
