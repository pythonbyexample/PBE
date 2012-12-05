Sudoku
======

Sudoku rules are simple: a move is valid as long as it does not create duplicate number in any
column, row or a 3x3 region; you can view the source here:

https://github.com/pythonbyexample/PBE/tree/master/code/sudoku.py

To run sudoku, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Tiles
-----

A tile can have the preset, or initial numbers which cannot be changed by the player; all other
tiles will be blank at first. Once the player sets the number, it can be changed at any time as
long as the value is valid.

I'll be using three types of tiles: `Initial` (can't change), `Blank` and `Number` (set by user).

Tiles won't have any methods except for `__eq__` to compare the number to other tiles present in
the region / line:

.. sourcecode:: python

    class Tile(BaseTile):
        initial = blank = False
        num     = None

        def __repr__(self)      : return str(self.num) if self.num else blank
        def __eq__(self, other) : return bool(self.num == other)


    class Number(Tile):
        def __init__(self, num):
            super(Number, self).__init__()
            self.num = int(num)

    class Blank(Tile)     : pass
    class Initial(Number) : pass


SudokuBoard
-----------

In the `__init__` method, all we need to do is load the puzzle from its string and generate regions
and lines. The lines are in fact vvery similar to the TicTacToe tutorial, but the effect is
reversed: instead of winning lines, we have lines that are not allowed to have repeated numbers.

Eeach of the nine regions is created in the same way, the only difference is that each region to
the right starts at the location offset by 3 horizontally; region below is offset vertically, and
so on.

The draw method is a bit tricky -- if it's unclear, try adding a few print() lines for intermediate
values; note how I'm using `ljoin()` to simplify the display logic.


.. sourcecode:: python

    class SudokuBoard(Board):
        def __init__(self, size, def_tile, puzzle):
            super(SudokuBoard, self).__init__(size, def_tile)

            for tile, val in zip(self, puzzle):
                if val != blank:
                    self[tile] = Initial(val)

            self.regions = [self.make_region(xo, yo) for xo in offsets for yo in offsets]

            lines = []
            for n in rng9:
                lines.extend(( [Loc(x, n) for x in rng9], [Loc(n, y) for y in rng9] ))
            self.lines = lines

        def make_region(self, xo, yo):
            """Make one region at x offset `xo` and y offset `yo`."""
            return [ Loc(xo + x, yo + y) for x in rng3 for y in rng3 ]

        def draw(self):
            print(nl*5)
            def ljoin(L): return sjoin(L, space, tiletpl)

            print( space*4, ljoin((1,2,3)), space, ljoin((4,5,6)), space, ljoin((7,8,9)), nl )

            for n, row in enumerate1(self.board):
                print(tiletpl % n, space,
                      ljoin(row[:3]), space, ljoin(row[3:6]), space, ljoin(row[6:9]),
                      nl)
                if n in (3,6): print()
            print(divider)


Sudoku
------

The main class is extremely simple: `check_end()` checks if there are no blank tiles left and ends
the game; valid_move disallows changing initial tiles and also checks that the value is not
already present in the line/region.

In the `BasicInterface` class, I get valid input from the user in `get_move()`; in `run()` the main loop
draws the board, gets user's move, sets the tile and finally checks if the game is finished.

`TextInput` accepts two arguments: the first is the board location in xy format, %d is an integer:
346 sets the tile at location 3,4 to value '6'; if spaces are present in the input, it's assumed
that they are used to separate commands, so '3 4 6' is valid, but '34 6' is not valid because it
parses 'x' as 34, which is out of range for this game:

.. sourcecode:: python

    class BasicInterface(object):
        def run(self):
            self.textinput = TextInput("loc %d", board)

            while True:
                board.draw()
                loc, val   = self.get_move()
                board[loc] = Number(val)
                sudoku.check_end()

        def get_move(self):
            while True:
                cmd = self.textinput.getinput()
                if sudoku.valid_move(*cmd) : return cmd
                else                       : print(self.textinput.invalid_move)


Configuration
-------------

At the top, I've defined a few constants I use to generate regions and lines:

.. sourcecode:: python

    rng3    = range(3)
    rng9    = range(9)
    offsets = (0, 3, 6)


Screenshots
-----------

The only one included puzzle looks like this::

         1  2  3    4  5  6    7  8  9

    1    .  1  3    .  .  .    .  .  2

    2    2  .  .    .  .  .    4  8  .

    3    .  .  .    7  .  .    .  1  9


    4    .  .  .    9  .  .    8  .  .

    5    7  .  .    .  .  .    .  2  .

    6    .  .  .    3  .  .    .  .  .


    7    .  .  2    6  3  .    9  .  .

    8    4  .  9    .  7  .    6  .  .

    9    .  .  1    4  9  .    .  .  8
