Blocky Blocks is a clone of the game "Jumpy Blocks", its rules are a bit convoluted: each tile has
a number (starting at one), which can be incremented by the player up to the tile's number of
neighbours, at which point it wraps back to zero. A player can only increment his own or neutral
tiles directly. The goal is to capture all tiles by wrapping around your own tiles located next to
enemy's.

First I'll create a tile class which should be able to increment itself as well as neighbour tiles
when it wraps around. I'll explain the first line below; `_increment()` increments and returns
True on wrap-around; `increment()` uses the floodfill algorithm to increment all neighbours
('cross' means neighbours in four major directions rather than all eight neighbours).

Next I will create the `BlockyBoard` class which is going to calculate the max (wrap-around)
number and create the number loop for each tile. The number loop has the `next()` method which
increments the number and wraps around at the end; `range1()` is a 1-indexed version of the Python
built-in `range()`.

The `ai_move()` will need to create a list of valid moves, sort them by how close they are to
wrapping around and either use the closest or random move -- in order to make it less predictable
(admittedly this is a very weak, basic AI).

The main class will only have one method which checks if the game is finished. I've added the
counter Loop to avoid infinite recursion in the flood fill algorithm which happens at the end of
game when tiles start incrementing each other in circles. The check above triggers when the
counter wraps around to zero.

I've created the `Test` class to separate front-end logic that handles user input from the rest of
the game to make it easier to use a different interface in the future.

`TextInput` class accepts and parses the tile location from user input (in `get_move()`); the run()
loop draws the board, goes over each player and makes their moves.
