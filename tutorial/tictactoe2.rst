TicTacToe (expanded version)
============================

This section is the expanded version of the first TicTacToe tutorial. If you've understood
everything in the first chapter and had no trouble following the code, you don't need to
read this page -- go right ahead and skip to the next section.

You can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/tictactoe.py


To run tictactoe, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Tictactoe class
---------------

Let's take a step back and think about what we need to make this game work: first, we need
two players; second -- the board for them to play on; third, a way for the game to check
for a winning condition.

The first two requirements are easy: each player can be a single character string, 'X' and
'O', and the board will be a list of lines with each tile identified by x & y coordinates.

The third requirement is a little harder -- I don't want to limit the game to a 3x3 grid
(which would be easy to hard-code the locations for), so the obvious approach would be to
check if a new move is placed on a diagonal and then to check the rest of the diagonal
tiles, and to do the same check for the vertical and horizontal lines.

Sometimes programming is similar to cooking - it's best to prep the ingredients and tools
before hand rather than scamper around trying to do everything at the same time later on.
In this case, it's easier to prepare "win lines", i.e. lines which, when filled out,
result in a win, before the game starts. Each of these lines will be a simple list of
coordinates.

Once the player makes a move, all I'll have to do is go over the list of win lines and
check if any of them are filled out by the current player. In this game the list is small
enough to make it acceptable to go over on each turn; if the list was much larger, a good
optimization would be to make a dictionary of coordinates with each key corresponding to a
list of win lines containing the coordinate.

Let's think about making lists of rows and columns first -- since they are easier than
diagonals. The first row has the x coordinate going from 0 to width-1, and y coordinate is
0. The second row is the same except that y is 1, and so on. To make a list of rows, I
need to iterate over `y` values from 0 to height-1, creating a list with `x` ranging
from 0 to width-1; the pseudocode is::


    for y from 0 to height:
        winline = [x,y for x (from 0 to width)]

(NOTE: this is NOT real Python code, although it's fairly close).

The list of columns is very similar::

    for x from 0 to width:
        winline = [x,y for y (from 0 to height)]

As you may know, TicTacToe is always played on a square board, so that height and width
are the same, and may be referred to as 'size', which means we can combine both loops by
iterating over `n` and `m` and swapping their locations::

    for n from 0 to size:
        winline = [m,n for m (from 0 to size)]
        winline = [n,m for m (from 0 to size)]

This might seem a little confusing, if it makes it clearer, you can make a slightly more
verbose version that explicitly refers to x and y coordinates::

    for x from 0 to size:
        winline = [x,y for y (from 0 to size)]
        y = x
        winline = [x,y for x (from 0 to size)]

Naturally, you'll also need to add the winlines to a list (more on this below). Let's
tackle the diagonals: the first one starts at the top left corner; if you picture the
coordinates as it goes down towards the right corner, the x and y are both incremented by
one: 0,0 1,1 2,2 and so on. Going back to using `n` for coordinates, we get::

    diag = []
    for n from 0 to size:
        diag.add(n, n)

The second diagonal's y coordinate changes in the same way as before, but x coordinate starts at `size`
and then decrements by one as it goes down, so I have the `n` variable that goes from 0 to
`size` but I need to get another variable out of it that goes in the opposite direction,
i.e. 1->size, 2->size-2, 3->size-3... I hope you can see the pattern! As the indexing
starts at 0, we also need to adjust the calculation by further subtracting 1 from size::

    diag = []
    for x from 0 to size:
        y = size - x - 1
        diag.add(x, y)

Finally, here is the real Python code:

.. sourcecode:: python

    def make_win_lines(self):
        """Create a list of winning lines -- when a player fills any one of them, he wins."""
        lines, diag1, diag2 = [], [], []

        for n in range(size):
            lines.append( [Loc(m, n) for m in range(size)] )
            lines.append( [Loc(n, m) for m in range(size)] )

            diag1.append(Loc(n, n))
            diag2.append(Loc(size-n-1, n))

        return lines + [diag1, diag2]

As you can see, a few things here are different from the pseudocode -- let's go over each
of them in turn.

Python's `range()` built-in returns a list of values from 0 to the max value passed as
an argument; the append() method adds the argument at the end of the list.

I'm using the Loc object (Loc means Location), imported from the utils module, to wrap
each coordinate pair, giving it convenient x and y attributes.

I end up with a list `lines` which contains rows and columns and two additional `diag1`
and `diag2` lines. As a last step, I need to add them together so that a master list of
all win lines is returned. As you may remember from the Python tutorial, lists can be
added together using `+` operator:

.. sourcecode:: python

    >>> l = [3, 4]
    >>> a, b = 1, 2
    >>> l + [a, b]
    [3, 4, 1, 2]





The next method will check if the player has won the game by completing a line and then check if
the game came to a draw (board is filled up and no more moves are possible).

The `game_won()` method prints out the win / draw message and quits the game.

The `winmsg` and `drawmsg` are defined at the top of `Tictactoe` as class variables.

.. sourcecode:: python

    def check_end(self, player):
        for line in self.win_lines:
            if board.completed(line, player):
                self.game_won(player)

        if board.filled(): self.game_won(None)

    def game_won(self, player):
        print(self.winmsg % player if player else self.drawmsg)
        sys.exit()


In `run()`, I'll need to cycle over the players and let each one make a random move, draw the board
and check if game is done.

.. sourcecode:: python

    def run(self):
        self.win_lines = self.make_win_lines()

        for player in cycle(players):
            board[ board.random_blank() ] = player
            board.draw()
            self.check_end(player)

(The `cycle()` function is a part of `itertools` module -- it will iterate over items in a sequence
continuously until interrupted from inside the loop.)

TictactoeBoard
--------------

The playing board will inherit from the `board.Board` class which provides some primitive playing
board functionality. I'll cover board.py in one of the later tutorials.

The board will need to do three simple things:

1. return a random blank location
2. check if a winning line is completed by the player
3. check if the board is completely filled up

.. sourcecode:: python

    class TictactoeBoard(Board):
        def filled(self):
            return not any( self[loc] == blank for loc in self.locations() )

        def random_blank(self):
            return rndchoice( [loc for loc in self.locations() if self[loc] == blank] )

        def completed(self, line, item):
            return all(self[loc] == item for loc in line)

The method `self.locations()` returns the list of all locations in the board; `blank` is a
character constant '.' used to show blank locations; `rndchoice()` is aliased from python's
`random.choice()`.

The built-ins `all()` and `any()` are both extremely useful, especially when used with list
comprehensions or generators. The first of these returns True if all items in the list are True;
the second returns True if at least a single item in the list is True. For an empty list, `any()`
returns False, `all()` returns True.

Here's the 'screenshot' of a sample run, with some of the padding removed::

    . . .
    . X .
    . . .

    . . .
    . X O
    . . .

    . . X
    . X O
    . . .

    . . X
    O X O
    . . .

    X . X
    O X O
    . . .

    X . X
    O X O
    O . .

    X X X
    O X O
    O . .

    X is the winner!
