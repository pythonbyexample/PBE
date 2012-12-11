Simple Race
===========

The goal of this game is to get your pieces to the end of the racing track before your opponent.

https://github.com/pythonbyexample/PBE/tree/master/code/simplerace.py

To run Simple Race, you will also need to download 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/utils.py

Piece
-----

The logic of the `move()` method is as follows: I need to set the current tile to blank, if I moved
past the end of track, I set the done attribute, if I moved on top of the opposing piece, I need
to bump it to the beginning of the track and finally I have to move myself to the new location.

.. sourcecode:: python


SimpleRace
----------

The `valid()` method is used to create the list of valid moves: the idea is that moving past the end
of track is always valid while the move inside the track is valid if you land on a blank tile or
on the opposing piece.

Make sure to read the docstring -- it explains a few interesting details about this method:

.. sourcecode:: python

BasicInterface
--------------

The logic of the `run()` method is as follows: I need to tell the player which type of pieces he's
playing.

In the main loop, I need to get the move distance, get the list of valid moves, determine if I
need to present a menu of moves to the player by using the `offer_choice()` method, make the chosen
move and finally check if the game is finished.

In the `get_move()` method, I need to show the menu of available moves, displayed under the racing
track so that each move number is aligned to the target location.

The easiest way to do that is to create a string of spaces which is six tiles longer than the
track (to accomodate past-the-track moves), and then to iterate over valid moves and insert each
move number at its target index.

Finally, we need to try to make the player's chosen move and to print an error if it's out of
valid range.

.. sourcecode:: python

Configuration
-------------

.. sourcecode:: python


Screenshots
-----------
