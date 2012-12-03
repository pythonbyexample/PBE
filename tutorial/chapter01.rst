TicTacToe
=========

Since TicTacToe is a very simple but not a very interesting game, this chapter will be more of a
simulation than a full game; there will be no user input, just the AI playing itself.

You can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/tictactoe.py


To run tictactoe, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

The only slightly difficult bit about this game is that I need to check if a player completed a
full line, thereby winning the game. To do that, I will first generate a list of all possible
lines that can win the game: horizontal, vertical and diagonal. This will be handled by the main
`Tictactoe` class, which will have the following methods:

- generate list of win lines
- check if the game came to a draw or if one player has won
- print out winning or draw message
- run the game: for each player, make a random move, draw the board and check for end of game

The most complicated method is the one that generates the win lines:

.. sourcecode:: python

    def make_win_lines(self):
        """Create a list of winning lines -- when a player fills any one of them, he wins."""
        lines, diag1, diag2 = [], [], []

        for n in range(size):
            lines.append( [Loc(m, n) for m in range(size)] )
            lines.append( [Loc(n, m) for m in range(size)] )

            diag1.append(Loc(n, n))
            diag2.append(Loc(2-n, n))

        return lines + [diag1, diag2]

The `Loc` class is imported from `board` and is a simple board location wrapper with x and y
attributes; `size` is an integer that specifies board size which is usually `3` in TicTacToe games.

I'm creating the vertical line first, then horizontal - in each loop; a single location is also added
to each diagonal line in the same loop. It may be a bit confusing that the same loop is making
whole lines at a time and also adding single locations to diagonal lines; you can split it into
two loops for clarity.

The next two methods check if the board is filled up; check if any of the win lines completed for
that player; if the game is done, win or draw message is printed:

.. sourcecode:: python

    def check_end(self, player):
        if board.filled(): self.game_won(None)

        for line in self.win_lines:
            if board.completed(line, player):
                self.game_won(player)

    def game_won(self, player):
        print(self.winmsg % player if player else self.drawmsg)
        sys.exit()


The `winmsg` and `drawmsg` are defined at the top of `Tictactoe` as class variables.

In `run()`, I need to cycle over the players and let each one make a random move, draw the board
and check if game is done.

.. sourcecode:: python

    def run(self):
        self.win_lines = self.make_win_lines()

        for player in cycle(players):
            board[ board.random_blank() ] = player
            board.draw()
            self.check_end(player)

I'm using `cycle()` function which is a part of `itertools` module -- it will iterate over items
in a sequence continuously until interrupted from inside the loop.

The playing board will use a primitive `board.Board` class that provides some simple playing board
functionality. I will cover board.py in one of the later tutorials.

The board will need to do three simple things: 1. return a random blank location 2. check if a
winning line is completed by the same player and 3. check if the board is completely filled up:

.. sourcecode:: python

    class TictactoeBoard(Board):
        def filled(self):
            return not any( self[loc] == blank for loc in self.locations() )

        def random_blank(self):
            return rndchoice( [loc for loc in self.locations() if self[loc] == blank] )

        def completed(self, line, item):
            return all(self[loc] == item for loc in line)

The method `self.locations()` simply returns the list of all locations in the board; `blank` is a
character constant '.' used to show blank locations; `rndchoice()` is aliased from python's
`random.choice()`.

The built-ins `all()` and `any()` are extremely useful, especially when used with list
comprehensions or generators. The first of these returns true if all items in the list are True;
second returns True if at least a single item in the list is True. For an empty list, `any()`
returns False, `all()` returns True.

Here's the sample run, with some of the padding removed::

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
