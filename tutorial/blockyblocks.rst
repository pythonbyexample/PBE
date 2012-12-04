Blocky Blocks
=============

Blocky Blocks is a clone of the game "Jumpy Blocks"; you can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/bblocks.py

To run bblocks, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Blocky Blocks' rules are a bit convoluted: each tile has a number (starting at
one), which can be incremented by the player up to the tile's number of
neighbours, at which point it wraps back to zero. A player can only increment
his own or neutral tiles directly. The goal is to capture all tiles by wrapping
around your own tiles located next to enemy's.

When you run this game, it's best to set the font size in your terminal to
about 14 or 18 to be able to see the unicode number symbols.

Tile
----

First I'll create a tile class which should be able to increment itself as well
as neighbour tiles when it wraps around. `_increment()` increments and returns
True on wrap-around; `increment()` uses the floodfill algorithm to increment
all neighbours ('cross' means neighbours in four major directions rather than
all eight neighbours); I'll cover the first line later in the tutorial:

.. sourcecode:: python

    class Tile(BaseTile):
        num = maxnum = player = None

        def __repr__(self):
            if self.player : return players[self.player][self.num-1]
            else           : return str(self.num)

        def increment(self, player):
            """ Increment tile number; if number wraps, increment neighbour tiles.
                `bblocks.counter` is used to avoid infinite recursion loops.
            """
            if not bblocks.counter.next(): bblocks.check_end(player)

            if self._increment(player):
                for tile in board.cross_neighbours(self):
                    tile.increment(player)
                board.draw()

        def _increment(self, player):
            self.player = player
            self.num.next()
            return bool(self.num == 1)

BlocksBoard
-----------

Next I will create the `BlockyBoard` class which is going to calculate the max
(wrap-around) number and create the number loop for each tile. The number loop
has the `next()` method which increments the number and wraps around at the
end; `range1()` is a 1-indexed version of the Python built-in `range()`.

The `ai_move()` will need to create a list of valid moves, sort them by how
close they are to wrapping around and either use the closest or random move --
in order to make it less predictable (admittedly this is a very weak, basic
AI).

.. sourcecode:: python

    class BlocksBoard(Board):
        def __init__(self, *args, **kwargs):
            super(BlocksBoard, self).__init__(*args, **kwargs)
            neighbours = self.neighbour_cross_locs

            for tile in self:
                tile.maxnum = len( [self.valid(nbloc) for nbloc in neighbours(tile)] )
                tile.num    = Loop(range1(tile.maxnum))

        def ai_move(self, player):
            """Randomly choose between returning the move closest to completing a tile or a random move."""
            tiles = [t for t in self if self.valid_move(player, t)]

            def to_max(t): return t.maxnum - t.num
            tiles.sort(key=to_max)
            return rndchoice( [first(tiles), rndchoice(tiles)] )

        def valid_move(self, player, tile):
            return bool(tile.player is None or tile.player==player)

BlockyBlocks
------------

The main class will only have one method which checks if the game is finished.
I've added the counter Loop to avoid infinite recursion in the flood fill
algorithm which happens at the end of game when tiles start incrementing each
other in circles. The check above triggers when the counter wraps around to
zero.

.. sourcecode:: python

    class BlockyBlocks(object):
        winmsg  = "player %s has won!"
        counter = Loop(range(check_moves))

        def check_end(self, player):
            if all(tile.player==player for tile in board):
                board.draw()
                print(nl, self.winmsg % player)
                sys.exit()

I've created the `Test` class to separate front-end logic that handles user
input from the rest of the game to make it easier to use a different interface
in the future.

`TextInput` class accepts and parses the tile location from user input (in
`get_move()`); the run() loop draws the board, goes over each player and makes
their moves.

.. sourcecode:: python

    class Test(object):
        def run(self):
            self.textinput = TextInput(board=board)

            for p in cycle(players.keys()):
                board.draw()
                tile = board.ai_move(p) if p in ai_players else self.get_move(p)
                tile.increment(p)
                bblocks.check_end(p)

        def get_move(self, player):
            while True:
                loc = self.textinput.getloc()
                if board.valid_move(player, board[loc]) : return board[loc]
                else                             : print(self.textinput.invalid_move)

Setup
-----

At the top, you can change a few settings:

.. sourcecode:: python

    size        = 4
    pause_time  = 0.4
    players     = {1: "➀➁➂➃", 2: "➊➋➌➍"}
    ai_players  = [1, 2]
    check_moves = 15
    padding     = 2, 1

Note that the game is implemented in a fairly flexible way which makes it
possible to change things like the size and each player easily: you can set
`ai_players` to be an empty list to let two human players play against each
other, you can set both players to be AI, or you can set one player to be AI to
play against it.

When you let two AIs battle it out, you can modify the `pause_time` to make the
game go faster or slower.
