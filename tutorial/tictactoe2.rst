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

Let's take a step back and think about what we need to make this game work:

- two players
- the board for them to play on
- a way for the game to check for a winning condition

The first two requirements are easy: each player can be a single character string, 'X' and 'O',
and the board will be a list of rows containing tiles; with each tile identified by x & y
coordinates.

The third requirement is a little harder -- I don't want to limit the game to a 3x3 grid (for
which it would be easy to hard-code the locations), so the obvious approach would be to check
if a new move is placed on a diagonal and then to check the rest of the diagonal tiles, and to
do the same check for the vertical and horizontal lines.

Sometimes programming is similar to cooking - it may be best to prep the ingredients and tools
beforehand rather than scamper around trying to do everything at the same time later on. In
this case, it's easier to prepare "win lines", i.e. lines which, when filled out, result in a
win, before the game starts. Each of these lines will be a simple list of coordinates.

Once the player makes a move, all I'll have to do is go over the list of win lines and
check if any of them are filled out by the current player. In this game the list is small
enough to make it acceptable to go over on each turn; if the list was much larger, a good
optimization would be to make a dictionary of coordinates with each key corresponding to a
list of win lines containing the coordinate.

Let's think about making lists of rows and columns first -- since they are easier than
diagonals. The first row has the `x` coordinate going from 0 to width-1, and `y` coordinate is
0. The second row is the same except that y is 1, and so on. To make a list of rows, I
need to iterate over `y` values from 0 to height-1, creating a list with `x` ranging
from 0 to width-1.

I'm going to ignore the -1 adjustment in the pseudocode to make it more readable, here it is::

    for each y (from 0 to height):
        winline = [x,y for each x (from 0 to width)]

(NOTE: this is NOT real Python code, although it's fairly close).

The list of columns is very similar::

    for each x (from 0 to width):
        winline = [x,y for each y (from 0 to height)]

As you may know, TicTacToe is always played on a square board, so that height and width
are the same, and may be referred to as `size`, which means we can combine both loops by
iterating over `n` and `m` and swapping their locations::

    for each n (from 0 to size):
        winline = [m,n for each m (from 0 to size)]
        winline = [n,m for each m (from 0 to size)]

This might seem a little confusing, if it makes it clearer, you can make a slightly more
verbose version that explicitly refers to `x` and `y` coordinates::

    for each x (from 0 to size):
        winline = [x,y for each y (from 0 to size)]
        y = x
        winline = [x,y for each x (from 0 to size)]

Naturally, you'll also need to add the winlines to a list, otherwise they'll be lost to you
forever. Let's tackle the diagonals: the first one starts at the top left corner; if you
picture the coordinates as the line goes down towards the right corner, the `x` and `y` are both
incremented by one: 00 11 22 and so on. Going back to using `n` for coordinates, we get::

    diag = []
    for each n from 0 to size:
        diag.add(n, n)

The second diagonal's y coordinate changes in the same way as before, but `x` coordinate starts
at `size` and then decrements by one as it goes down, so I have the `n` variable that goes from
0 to `size` but I need to get another variable out of it that goes in the opposite direction,
i.e. 1->size, 2->size-2, 3->size-3... I hope you can see the pattern! As the indexing starts at
0, we also need to adjust the calculation by further subtracting 1 from size::

    diag = []
    for each x (from 0 to size):
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
an argument; the `append()` method adds the argument at the end of the list.

I'm using the `Loc` object (Loc means Location), imported from the `utils` module, to wrap each
coordinate pair, giving it convenient x and y attributes.

I hope you still remember that horizontals and verticals are added one 'winline' per loop,
while diagonals are added one coordinate pair per loop, that's why they look different.

I end up with a list `lines` which contains rows and columns and two additional `diag1` and
`diag2` lines. As a last step, I need to add them together so that a master list of all win
lines is returned. As you may remember from the Python tutorial, lists can be added together
using `+` operator:

.. sourcecode:: python

    >>> lst = [3, 4]
    >>> a, b = 1, 2
    >>> lst + [a, b]
    [3, 4, 1, 2]


In the next method I'll need to use the list I've created to check if a player had won the
game yet. As an aside: in this simple game I'm using a single character string to
represent both the player and his 'mark' or tile he places on the board (in later games
we'll use a more complex object for players and their tiles).

The details of checking if a line is completed will be handled by the `Board`, as it depends
on current contents of the `Board,` so it makes sense to ask the `Board:` "is this line
completed by this player?"

Behold, our pseudocode::

    FOR line in win-lines:
        IF Board: line completed by player:
            game is won by player!

    IF Board is completely filled:
        game is a draw!

And the "game is won" will be handled by `game_won()` method, which, incidentally, also
needs to be able to handle a draw condition (remember, you don't always have a winner in
TicTacToe??!) To indicate a draw, I'll pass a `None` value as the player::

    game_won method (argument: player):
        print win message IF player OTHERWISE draw message
        exit game

Here is the real code for both of these methods (the `winmsg` and `drawmsg` are defined at
the top of `Tictactoe` as class variables):

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

When the game actually runs, it will need to cycle over players continuously until the end: 1st
player, 2nd player, 1st player, ... Inside the main loop, we'll need to place a player's tile
on a random blank `Board` location. As with winline / player checking above, this is the type
of thing `Board` should handle by itself (both giving back a blank location and placing a
specified tile on it). The board should also be able to draw itself and we'll need to check for
game end after each player's move -- since we can't let the next player make a move if the
other player has already won the game, that would make no sense at all! This pseudocode should
give you no trouble::

    create win lines

    CYCLE over players continuously:
        put player on Board at a random blank location
        draw the board
        CALL check_end method for the current player

The real code is shown below:

.. sourcecode:: python

    def run(self):
        self.win_lines = self.make_win_lines()

        for player in cycle(players):
            board[ board.random_blank() ] = player
            board.draw()
            self.check_end(player)

Note that I have to save `win_lines` as an instance attribute by using `self` prefix, which
refers to the current instance (in our case, the only existing instance of the `TicTacToe`
class).

The `Board` allows you to insert a tile at a location by using square brackets, just like
assigning an item to a list::

.. sourcecode:: python

    board[location] = item

The location we need to use here is returned by the `random_blank()` method. I hope you still
remember that the player and a player tile are interchangeable as they're both represented by a
single character which allows me to insert the tile by assigning the player variable.

(The `cycle()` function is a part of `itertools` module -- it needs to be imported before
it can be used.)

TictactoeBoard
--------------

The playing board will inherit from the `board.Board` class which provides some primitive playing
board functionality. I'll cover board.py in one of the later tutorials.

The `Board` will need to do three simple things:

1. return a random blank location
2. check if a winning line is completed by the player
3. check if the board is completely filled up

These methods will use the built-in `Board.locations()` method which returns a list of all
locations, and I will also need to use Python's `random.choice()` method (aliased as `randchoice`).

This is an excellent opportunity to introduce a pair of very useful filter functions that
work on lists and are especially handy when used with list comprehensions: `any()` and
`all();` here is a little demonstration:

.. sourcecode:: python

    >>> l = list(range(15))
    >>> l
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    >>> any(x>20 for x in l)
    False
    >>> any(x>10 for x in l)
    True
    >>> all(x>10 for x in l)
    False
    >>> all(x<30 for x in l)
    True

And here is our pseudocode::

    filled method:
        TEST none of the locations on Board are blank

    random_blank method:
        randomly choose one out of all blank locations on Board

    completed method (arguments: line, item):
        TEST all tiles in the 'line' are equal to 'item'


Easy-peasy? Yes, easy-peasy:

.. sourcecode:: python

    blank = '.'

    class TictactoeBoard(Board):
        def filled(self):
            return not any( self[loc] == blank for loc in self.locations() )

        def random_blank(self):
            return randchoice( [loc for loc in self.locations() if self[loc] == blank] )

        def completed(self, line, item):
            return all(self[loc] == item for loc in line)


Configuration
-------------

At the top of file, you can set the size of the `Board,` blank character (it's best not to set it
to space to let you see the size of the `Board`), and two single-character players::

    size    = 3
    blank   = '.'
    players = 'XO'


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
