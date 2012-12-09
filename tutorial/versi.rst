Versi
=====

Versi is a clone of the Reversi game.

The goal of the game is to capture more tiles than your enemy. You can capture the enemy's tiles
by placing a new piece on the blank tile so that one or more of enemy pieces are enclosed on a
line between your placed piece and one of your existing pieces.

https://github.com/pythonbyexample/PBE/tree/master/code/versi.py

To run Versi, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Tiles
-----

The two kinds of tiles I'll use are blank tiles and player pieces which will have the flip()
method to let the piece be captured by the enemy.

.. sourcecode:: python

VersiBoard
----------

There are a few small methods in the Board class: valid_move() returns True if the move captures
any pieces, get_valid_moves() returns all possible moves, is_corner() checks if the location is in
a corner, status() prints the score of each player.

The logic of the get_valid_movescaptured() method is as follows: starting from the newly placed
tile, go in each of eight directions and check if any pieces can be captured; return the list of
captures (which may be empty). Make sure to read the comments, they should help you with this
algorithm.

.. sourcecode:: python

Player
------

There are a couple of tiny methods in Player class: score() calculates the player's score by
adding up all of his tiles; enemy() returns Player's enemy.

The get_random_move() method is used by the AI and is a little tricky in the way it uses sorting:
we need to sort all moves so that corner locations are preferred, because they are protected from
capture, but in the absence of corner moves, we need to get the move that captures the most
pieces. When Python sorting is done, True values come first and numeric values are sorted in
ascending order, so I need to negate the number of captured pieces, to have best moves sorted near
the top.

.. sourcecode:: python


Versi
-----

The Versi class is quite simple: I'm initializing a few pieces that go in the center of the board,
check if the game is finished and print win/lose/draw messages.

.. sourcecode:: python


BasicInterface
--------------

Player's input is simply the location of the new piece; the logic of the main loop is complicated
a bit by the fact that a player may have no valid moves available in which case the other player
continues to make moves until the first player can move again or the game ends, so the transfer of
turns needs to be handled explicitly.

The Player can always quit the game by entering the 'q' command.

.. sourcecode:: python


Configuration
-------------

You can play human vs. human by setting ai_players empty, AI vs AI by setting it to include all AI
players, and human vs AI by omitting one player.

[test if size needs to be square]

.. sourcecode:: python


Screenshots
-----------
