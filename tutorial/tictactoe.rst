TicTacToe
=========

Since TicTacToe is a very simple but not a very interesting game, this chapter will be more of a
simulation than a full game; there will be no user input, just the AI playing itself.

This chapter is meant for readers with some degree of experience in Python and other languages;
if you are just starting out, please navigate to the next chapter which covers the same
material in much greater detail.

You can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/tictactoe.py


To run tictactoe, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Tictactoe class
---------------

The only slightly difficult bit about this game is that I need to check if a player completed a
full line, thereby winning the game. To accomplish that, I will first generate a list of all
possible lines that can win the game: horizontal, vertical and diagonal. This will be handled by
the main `Tictactoe` class, which will have the methods that will take care of:

- generating the list of win lines
- checking if the game came to a draw or if one player has won
- printing out the winning or draw message
- running the game: for each player, make a random move, draw the board and check for end of game

The largest method is the one that generates the win lines:

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

The `Loc` class is imported from `board` and is a simple board location wrapper with x and y
attributes; `size` is an integer that specifies board size which is usually `3` in TicTacToe games.

In each loop, I'm creating the vertical line first, then horizontal; a single location is also
added to each of the two diagonal lines in the same loop. It may be a bit confusing that the same
loop is making whole lines at a time and also adding single locations to diagonal lines; you can
split it into two loops for clarity if that helps.

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
            return randchoice( [loc for loc in self.locations() if self[loc] == blank] )

        def completed(self, line, item):
            return all(self[loc] == item for loc in line)

The method `self.locations()` returns the list of all locations in the board; `blank` is a
character constant '.' used to show blank locations; `randchoice()` is aliased from python's
`random.choice()`.

The built-ins `all()` and `any()` are both extremely useful, especially when used with list
comprehensions or generators. The first of these returns True if all items in the list are True;
the second returns True if at least a single item in the list is True. For an empty list, `any()`
returns False, `all()` returns True.


Configuration
-------------

At the top of file, you can set the size of the Board, blank character (it's
best not to set it to space to let you see the size of the Board), and two single-character
players::

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
