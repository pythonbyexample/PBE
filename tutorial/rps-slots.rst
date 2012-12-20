RockPaperScissors
=================

Rock Paper Scissors is a tiny game where you can beat the opponent by countering his rock with
paper, his scissors with rock, and his paper with scissors.

You can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/rockpaper.py


To run RockPaperScissors, you will also need to download 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/utils.py


Code
----

The main logic of the game happens in the `run()` method: I need to create the `textinput`
instance with a pattern that accepts 'r', 'p', and 's' inputs and the `scores` list.

In the main loop, I'm getting the choices (inputs) of each player; if they are the same, I don't
need to do anything because it's a draw. If they're not the same, I check if combined choices are
in `wins` tuple -- if they are, the 2nd player wins, otherwise the 1st player wins --
corresponding to the 1st and 0th indexes in the `scores` list, which I then increment.

Finally, I print out the status message with updated scores and moves and then pause for a short
time (the only reason I do that is to slow things down when AI plays vs. AI).

.. sourcecode:: python

    wins = ("rp", "sr", "ps")   # choice on the right side wins

    class RockPaperScissors(object):
        def run(self):
            self.textinput = TextInput("(r|p|s)")
            scores         = [0, 0]

            while True:
                choice1, choice2 = (self.get_move(p) for p in players)

                if choice1 != choice2:
                    winplayer = 1 if (choice1+choice2 in wins) else 0
                    scores[winplayer] += 1

                print(status % (players[0], scores[0], players[1], scores[1], choice1, choice2))
                sleep(pause_time)

In the `get_move()` function, I only need to check if the player is AI and return a random move or
the player's move from `textinput`.

You can quit the game by using the 'q' key.

.. sourcecode:: python

        def get_move(self, player):
            if player in ai_players : return randchoice(moves)
            else                    : return self.textinput.getval()

Configuration
-------------

You can run the game in AI vs. AI mode, play against the AI, or play against human by setting the 
`ai_players` accordingly.

.. sourcecode:: python

    players    = "XY"
    ai_players = "Y"


Screenshots
-----------

A sample run, I'm playing 'X'::

    > r
    X   0     Y   0     moves: r r
    > r
    X   1     Y   0     moves: r s
    > r
    X   1     Y   0     moves: r r
    > r
    X   1     Y   1     moves: r p
    > r
    X   1     Y   2     moves: r p
    > r
    X   1     Y   2     moves: r r
    > r
    X   2     Y   2     moves: r s
    > p
    X   3     Y   2     moves: p r
    > p
    X   3     Y   3     moves: p s
    > s
    X   4     Y   3     moves: s p
    > s
    X   4     Y   4     moves: s r


Slot Machine
============

This small game is a simulation of a slot machine.

You can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/slotmachine.py


Reel
----

The Reel class represents a single reel, or 'drum', inside the machine, which
rotates independently from other reels when the machine is running. It would be easy to make a
random display of symbols while the reels are spinning and make a final random selection when
it stops, but I think it's more interesting to make a more realistic simulation and have the
reels that are actually rotating in the same sequence. To make sure changing symbols of
different reels are not synchronized, I'll have them rotating at randomized, different speeds.

As in a real slot machine, I'll stop the reels in a delayed order from left to right, using
randomly generated max_cycle variable to let them know when to stop.

I'll use the utils.Loop class to store the list of symbols and cycle through them using
Loop.next() method. The symbol() method will rotate the reel if it did not reach max_cycle yet
and return current symbol:

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

The run() method sets up the machine and runs it until all reels come to a stop.

I'll need to create a rotation and max_cycle values for each of the reels and then create the
reel objects themselves.



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
