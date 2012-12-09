Robots
======

The goal of this game is to create a program that leads the player to the goal within the allotted
number of turns.

https://github.com/pythonbyexample/PBE/tree/master/code/robots.py

To run Robots, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Tiles
-----

This game ahas a lot more of different tiles compared to previous games; to make it a little
easier to deal with all of them, I've automated the assignment of tile characters and healths by
using the special __class__.__name__ attributes.

The mobile tile is the parent for robots, the player and missile tiles. It has the following
action-handling methods: turn clockwise and counter-clockwise, wait, execute random action, fire a
missile, move one tile ahead.

The create_program() method creates a random program (used by the AI), and go() executes the next
step in the current program.

The fire() method requires some explanation: if there is no space ahead, we do nothing; if there
is a blank space, the missile is sent on its merry way, but if there is no blank space, there is a
slight problem: we have nowhere to place the missile, so we need to create a special type of
missile which has no location and no direction (it's a really aimless missile in its own age of
adolescence); immediately after creation, the missile hits its target out of nowhere.

The robot and player tiles are similar but the player needs some additional processing when it
moves to tell if it has won the game by reaching the goal or lost by failing to do so before its
turns ran out.

Finally, the missile keeps flying along its way until it hits something; once it hits, it may
destroy the target if it has no health left.

.. sourcecode:: python

RBoard
------

The board only provides a rnadom blank location and combined status of all players.

.. sourcecode:: python

RobotsGame
----------

The main class handles game end with win/lose messages and expands the player's program which I'll
explain in the following section.

.. sourcecode:: python

BasicInterface
--------------

The player can submit the program in the following format: "Ncmd1 Ncmd2 ...", for example: "m 2t
3m T 2f" means move one tile, make 2 clockwise turns (each turn being 45 degrees), move 3 tiles,
make counter clockwise turn, fire 2 missiles. (See commands dict at the top of file for a full
list of actions).

The `singlechar_cmds` argument is needed to allow the player to group multiple commands using
spaces, without this argument each command and its count would have to be separated: '3 m 2 f'. The
trade-off is that this option does not allow you to enter counts larger than 9, so to move 15
tiles you'd need to enter "9m 6m".

.. sourcecode:: python


Configuration
-------------

You can set num_players to 0 to look at robots run random programs continuously, to 1 for a single
player and to 2 for human vs. human game; you can also adjust max_turns to make it harder or
easier to reach the goal. As always, you can change size to make a larger game board.

.. sourcecode:: python


Screenshots
-----------
