Versi
=====

Versi is a clone of the Reversi game.

The goal of the game is to capture more tiles than your enemy. You can capture the enemy's tiles
by placing a new piece on the blank tile so that one or more of enemy pieces are enclosed on a
line between your placed piece and one of your existing pieces.

https://github.com/pythonbyexample/PBE/tree/master/code/versi.py

To run Versi, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

PlayerBase
----------

In order to compare Tiles and Player instances, I'll need a class that handles this logic:

.. sourcecode:: python

    class PlayerBase(object):
        def __eq__(self, other):
            return bool(self.char == getattr(other, "char", None))

        def __ne__(self, other):
            return not self==other

Tiles
-----

The two kinds of tiles I'll use are blank tiles and player pieces which will have the `flip()`
method to let the piece be captured by the enemy:

.. sourcecode:: python

    class Tile(BaseTile, PlayerBase):
        blank = piece = False

        def __repr__(self): return self.char


    class Blank(Tile): char = blank


    class Piece(Tile):
        def __init__(self, loc=None, char=None):
            super(Piece, self).__init__(loc)
            self.char = char
            if loc: board[loc] = self

        def flip(self):
            self.char = nextval(player_chars, self.char)

VersiBoard
----------

There are a few small methods in the `Board` class: `valid_move()` returns `True` if the move captures
any pieces, `get_valid_moves()` returns all possible moves, `is_corner()` checks if the location is in
a corner, `status()` prints the score of each player:

.. sourcecode:: python

    class VersiBoard(Board):
        scores_msg = "%s  score: %3s    %s  score: %3s"

        def get_valid_moves(self, player):
            return [loc for loc in self.locations() if self.valid_move(player, loc)]

        def valid_move(self, player, loc):
            return bool(self.get_captured(player, loc))

        def is_corner(self, loc):
            return loc.x in (0, self.width-1) and loc.y in (0, self.height-1)

        def status(self):
            print(self.scores_msg % (player1, player1.score(), player2, player2.score()))

        def middle(self):
            return iround(self.width/2) - 1, iround(self.height/2) - 1

The logic of the `get_captured()` method is as follows: starting from the newly placed tile, go in
each of eight directions and check if any pieces can be captured; return the list of captures
(which may be empty).

Note that `dirlist2` is a list of eight major directions while `dirlist` is a list of four
directions.

.. sourcecode:: python

    def get_captured(self, player, start_loc):
        """If `start_loc` is a valid move, returns a list of locations of captured pieces."""
        if not self[start_loc].blank:
            return []

        getdir = self.capture_direction
        return flatten( [getdir(player, start_loc, dir) for dir in self.dirlist2] )

    def capture_direction(self, player, start, dir):
        """Return the list of enemy tiles to capture in the `dir` direction from `start` location."""
        groups = groupby(self.ray(start, dir))
        group1, group2 = nextgroup(groups), nextgroup(groups)
        if group1 and group2 and (group1.key == player.enemy() and group2.key == player):
            return group1.group
        else:
            return []


Player
------

There are a couple of tiny methods in the `Player` class: `score()` calculates the player's score
by adding up all of his tiles, `enemy()` returns Player's enemy.

.. sourcecode:: python

    def __init__(self, char):
        self.char = char
        self.ai   = char in ai_players

    def __repr__(self) : return self.char

    def score(self)    : return sum(tile==self for tile in board)
    def enemy(self)    : return nextval(players, self)

    def make_move(self, loc):
        for tile in board.get_captured(self, loc):
            tile.flip()
        Piece(loc, self.char)


The `get_random_move()` method is used by the AI and is a little tricky in the way it uses sorting:
we need to sort all moves so that corner locations are preferred, because they are protected from
capture, but in the absence of corner moves, we need to get the move that captures the most
pieces.

In the default Python sorting, `True` values come first and numeric values are sorted in ascending
order, so I need to negate the number of captured pieces to have the best moves sorted near the top:

.. sourcecode:: python

    def get_random_move(self):
        """Return location of best move."""
        def by_corner_score(loc):
            return board.is_corner(loc), -len(board.get_captured(self, loc))

        moves = board.get_valid_moves(self)
        shuffle(moves)
        return first(sorted(moves, key=by_corner_score))

Versi
-----

The Versi class is quite simple: I'm initializing a few pieces that go in the middle of the board,
checking if the game is finished and printing win/lose/draw messages.

.. sourcecode:: python

    class Versi(object):
        winmsg     = "%s wins!"
        tiemsg     = "The game was a tie!"

        def __init__(self):
            x, y = board.middle()
            Piece(Loc(x,y), player1.char)
            Piece(Loc(x+1, y+1), player1.char)
            Piece(Loc(x+1, y), player2.char)
            Piece(Loc(x, y+1), player2.char)

        def game_end(self):
            board.draw()
            winner = cmp(player1.score(), player2.score())
            if not winner : print(nl, self.tiemsg)
            else          : print(nl, self.winmsg % (player1 if winner>0 else player2))
            sys.exit()

BasicInterface
--------------

Player's input is simply the location of the new piece; the logic of the main loop is complicated
a bit by the fact that a player may have no valid moves available, in which case the other player
continues to make moves until the first player can either move again or the game ends; for this
reason, the transfer of turns needs to be handled explicitly.

The Player can always quit the game by entering the 'q' command.

.. sourcecode:: python

    def run(self):
        moves          = board.get_valid_moves
        player         = rndchoice(players)
        player         = first(players)
        self.textinput = TextInput(board=board)

        while True:
            board.draw()
            move = player.get_random_move() if player.ai else self.get_move(player)
            player.make_move(move)

            # give next turn to enemy OR end game if no turns left, FALLTHRU: current player keeps the turn
            if moves(player.enemy()) : player = player.enemy()
            elif not moves(player)   : versi.game_end()

    def get_move(self, player):
        while True:
            loc = self.textinput.getloc()
            if board.valid_move(player, loc) : return loc
            else                             : print(self.textinput.invalid_move)

Configuration
-------------

You can play human vs. human by setting `ai_players` empty, AI vs AI by setting it to include all AI
players, and human vs AI by omitting one player.

.. sourcecode:: python

    size         = 5, 5
    player_chars = '⎔▣'
    ai_players   = '⎔▣'

Screenshots
-----------


I'm playing square pieces, here is the initial layout::


          1     2     3     4     5     6


    1     .     .     .     .     .     .


    2     .     .     .     .     .     .


    3     .     .     ▣     ⎔     .     .


    4     .     .     ⎔     ▣     .     .


    5     .     .     .     .     .     .


    6     .     .     .     .     .     .


    ▣  score:   2    ⎔  score:   2
    >


This screenshot shows the board after two moves: my move to 5,3 and the AI move to 5,2; as you can
see, our scores changed accordingly::


          1     2     3     4     5     6


    1     .     .     .     .     .     .


    2     .     .     .     .     ⎔     .


    3     .     .     ▣     ⎔     ▣     .


    4     .     .     ⎔     ▣     .     .


    5     .     .     .     .     .     .


    6     .     .     .     .     .     .


    ▣  score:   3    ⎔  score:   3
    >


