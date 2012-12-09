Mines
=====

Mines is a clone of the Minesweeper game, the goal is to clear out all mines by marking their
location. Numbered tiles tell you how many mines are in the surrounding area.

https://github.com/pythonbyexample/PBE/tree/master/code/mines.py

To run Mines, you will also need to download 'mines_lib.py', 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/


Tile
----

In this game I will use the same tile class to represent both mines and number tiles.

I am going to have a reverse link for the revealed/hidden attribute, which is done by the
`AttrToggles` class; in effect, changing either attribute will also set the other one to be the
reverse of the first.

.. sourcecode:: python

    class Tile(BaseTile, AttrToggles):
        revealed = mine = marked = False
        hidden   = True
        number   = None

        attribute_toggles = [("hidden", "revealed")]

        def __repr__(self):
            if   self.hidden : return hiddenchar
            elif self.marked : return flag
            elif self.mine   : return minechar
            else             : return self.num()

        def num(self):
            return numbers[self.number-1] if self.number else blank

        def toggle_mark(self):
            self.marked = not self.marked
            self.hidden = not self.hidden


MinesBoard
----------

The `MinesBoard` class initializes mines according to num_mines setting and calculates all numbered
tiles based on how many neighbours are mines. The cleared method checks if all tiles on the board
were marked.

.. sourcecode:: python

    def __init__(self, *args, **kwargs):
        num_mines = kwargs.pop("num_mines")

        super(MinesBoard, self).__init__(*args, **kwargs)
        self.divider = '-' * (self.width * 4 + 4)

        for _ in range(num_mines):
            self.random_empty().mine = True

        for tile in self:
            tile.number = sum( nbtile.mine for nbtile in self.neighbours(tile) )

    def cleared(self):
        return all( self.marked_or_revealed(tile) for tile in self )

    def marked_or_revealed(self, tile) : return bool(tile.revealed or tile.mine and tile.marked)
    def random_hidden(self)            : return rndchoice(self.locations("hidden"))
    def random_empty(self)             : return rndchoice(self.tiles_not("mine"))

It's important that a marked tile passes the test only if it really has a mine on it, otherwise
the player could just mark all the tiles and win the game -- we can't have that!

The reveal method simply sets the tile status as revealed; the possible explosion is handled in
the `Mines` class.

.. sourcecode:: python

    def reveal(self, tile):
        """ Reveal all empty (number=0) tiles adjacent to starting tile `loc` and subsequent unhidden tiles.
            Uses floodfill algorithm.
        """
        if tile.number   : tile.revealed = True
        if tile.revealed : return

        tile.revealed = True
        for nbtile in self.neighbours(tile): self.reveal(nbtile)

Revealing of blank tiles (the ones without numbers) is a little trickier: it should only be done
when the player picks a blank tile and it should spread outwards from that tile and reveal all
numbered tiles right next to blank tiles, but no tiles beyond those. The general idea is that
everything around a blank tile is safe to reveal by definition, so it makes no sense to force the
player to reveal them manually.


Mines
-----

In the main class, I only need the methods to check for end of game and win/lose handling; I need
to check for exploded mines first because it would pass the test `board.cleared()` if it was the last
tile left.

.. sourcecode:: python

    def check_end(self, tile):
        """Check if game is lost (stepped on a mine), or won (all mines found)."""
        if tile.mine and not tile.marked:
            self.game_lost()
        elif self.board.cleared():
            self.game_won()

In `game_lost()` I want to show the mine locations when the player loses, as a consolation, and I
want to show how long the game took when the player wins:

.. sourcecode:: python

    def game_lost(self):
        B = self.board
        for tile in B: B.reveal(tile)
        B.draw()
        print(self.lose_msg)
        sys.exit()

    def game_won(self):
        self.board.draw()
        print( self.win_msg % timefmt(time() - self.start) )
        sys.exit()


BasicInterface
--------------

There are two types of player commands we need to handle: the first is a location or a list of
locations, for example: '34' to reveal the tile at 3,4 coordicates, '34 36' to reveal two tiles,
et cetera. The second type of commands is exactly the same, but with an 'm' key added at the
beginning to mark mine locations, for example 'm 34 36' to mark these tiles.

The `singlechar_cmds` argument is needed to allow the player to group multiple commands using
spaces, without this argument each coordinate would have to be separated: 'm 3 4 3 6'. The
trade-off is that this option does not allow you to play on a board larger than 9x9, because it
interprets a '11 5' coordinate as 1,1 ; but I think a 9x9 board should be enough for most people.

The question mark denotes an optional part of the pattern.

.. sourcecode:: python

    class BasicInterface(object):
        def run(self):
            # allow entering of multiple (up to 10) locations
            pattern        = "%s? loc%s" % (mark_key, " loc?"*9)
            self.textinput = TextInput(pattern, board, singlechar_cmds=True)
            while True:
                board.draw()
                self.make_move()

        def make_move(self):
            cmd  = self.textinput.getinput()
            mark = bool(first(cmd) == mark_key)
            if mark: cmd.pop(0)

            for loc in cmd:
                tile = board[loc]
                tile.toggle_mark() if mark else board.reveal(tile)
                mines.check_end(tile)

Configuration
-------------

It's important to have a random number of mines so that the player won't know if all the mines are
marked.

.. sourcecode:: python

    size       = 6, 6
    num_mines  = randint(4, 8)
    mark_key   = 'm'
    padding    = 2, 1


Screenshots
-----------

::

        1   2   3   4   5   6

    1   .   .   .   .   ⚑   ⚑

    2   .   .   .   ⚑   ③   ②

    3   .   ①   ①   ①   ①

    4   .   ①

    5   .   ②   ①   ①

    6   .   .   ⚑   ①

    >
