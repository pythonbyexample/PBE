Battleship
==========

https://github.com/pythonbyexample/PBE/tree/master/code/battleship.py

To run battleship, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Tiles
-----

Battleship has only two types of tiles: blank and ship -- a ship will simply be represented by a
few 'ship' tiles in a row or a column. In addition, I would like to display 'hit' empty tiles and
sunk ships differently, which means I need to have an `is_hit` attribute and two extra chars to
show a hit ship/tile.

Handling of hidden/revealed status is a little tricky: I want the entire player's `Board` to be
revealed from the start, but the enemy's `Board` will be hidden except for the tiles that were hit.

I am going to have a reverse link for the revealed/hidden attribute, which is done by the
`AttrToggles` class; in effect, changing either attribute will also set the other one to be the
reverse of the first.

.. sourcecode:: python

    class Tile(BaseTile, AttrToggles):
        """Tile that may be a ship or blank space (water)."""
        ship              = blank = is_hit = revealed = False
        hidden            = True
        attribute_toggles = [("hidden", "revealed")]

        def __repr__(self):
            return blank if self.hidden else self.char

        def hit(self):
            self.is_hit   = True
            self.revealed = True
            self.char     = sunkship if self.ship else hitchar


    class Blank(Tile) : char = blank
    class Ship(Tile)  : char = shipchar


BattleshipBoard
---------------

The Board has a couple of simple methods that return a random blank tile for ship placement and a
random unhit tile for the AI move.

The `random_placement()` method picks a random spot and places the ship, ensuring that it's not
located next to any other ship by using the `next_validloc()` method. `Board.nextloc()` returns an
offset location in a given direction if valid, otherwise it returns `None`.

.. sourcecode:: python

    class BattleshipBoard(Board):
        def random_blank(self) : return rndchoice(self.tiles("blank"))
        def random_unhit(self) : return rndchoice(self.tiles_not("is_hit"))

        def next_validloc(self, start, dir, n):
            loc = self.nextloc(start, dir, n)
            if loc and not any(t.ship for t in self.cross_neighbours(loc)):
                return loc

        def random_placement(self, ship):
            """Return list of random locations for `ship` length."""
            while True:
                start = self.random_blank()
                dir   = rndchoice(self.dirlist)
                locs  = [ self.next_validloc(start, dir, n) for n in range(ship) ]
                if all(locs): break

            return locs


Player
------

The `Player` class initializes the `Board` for each player and does ship placement according to the
`num_ships` setting; it also has a simple `enemy()` method which uses the `utils.nextval()` function to
return the player's enemy.

.. sourcecode:: python

    class Player(object):
        def __init__(self, num):
            """Create player's board and randomly place `num_ships` ships on it."""
            self.num   = num
            self.ai    = bool(num in ai_players)
            self.board = BattleshipBoard(size, Blank, num_grid=True, padding=padding, pause_time=0, screen_sep=0)
            B          = self.board

            for ship in range1(num_ships):
                for loc in B.random_placement(ship):
                    B[loc] = Ship(loc)

            if not self.ai:
                for tile in B: tile.revealed = True

        def enemy(self): return nextval(players, self)


Battleship
----------

The `check_end` method should be called with current player's enemy -- it checks if all of his ships
were hit, prints out win message and ends the game.

.. sourcecode:: python

    class Battleship(object):
        winmsg = "Player %s wins!"

        def draw(self):
            p1, p2 = players
            print(nl*5)
            p1.board.draw()
            print(divider)
            p2.board.draw()
            sleep(pause_time)

        def check_end(self, player):
            if all(ship.is_hit for ship in player.board.tiles("ship")):
                self.draw()
                print(self.winmsg % player.enemy().num)
                sys.exit()


The `run()` method is very simple: draw, make the move, check if the enemy is defeated:

.. sourcecode:: python

    class BasicInterface(object):
        def run(self):
            # board is only used to check if location is within range (using board.valid())
            self.textinput = TextInput( board=first(players).board )

            for player in cycle(players):
                bship.draw()
                tile = self.ai_move(player) if player.ai else self.get_move(player)
                tile.hit()
                bship.check_end(player.enemy())

        def get_move(self, player):
            """Get user command and return the tile to attack."""
            return player.enemy().board[ self.textinput.getloc() ]

        def ai_move(self, player):
            """Very primitive 'AI', always hits a random location."""
            return player.enemy().board.random_unhit()


Constants
---------

At the top, I've defined a few constants which can be used to configure game options: `size` to
change each player's board, `num_ships` for the nubmer of ships; unicode chars used to display
ships, water, explosions.

The `ai_players` list can be set to include both players for AI vs. AI play, one player for human
vs. AI.

Human vs. Human play is not very interesting because both boards will be fully revealed.

.. sourcecode:: python

    size       = 5, 5
    num_ships  = 3
    pause_time = 0.3

    blank      = '𝀈'
    shipchar   = '▢'
    sunkship   = '☀'
    hitchar    = '♈'

    players    = [1, 2]
    ai_players = [1, 2]


Screenshots
-----------

The board on top is the AI's, the other one is mine and it shows my ships and an AI's missed attack:


    1   2   3   4   5

1   𝀈   𝀈   𝀈   𝀈   𝀈

2   𝀈   𝀈   𝀈   𝀈   𝀈

3   𝀈   𝀈   𝀈   𝀈   𝀈

4   𝀈   𝀈   𝀈   𝀈   𝀈

5   𝀈   𝀈   𝀈   𝀈   𝀈

--------------------------

    1   2   3   4   5

1   𝀈   ♈   ▢   𝀈   𝀈

2   𝀈   𝀈   ▢   𝀈   ▢

3   𝀈   𝀈   ▢   𝀈   𝀈

4   ▢   𝀈   𝀈   𝀈   𝀈

5   ▢   𝀈   𝀈   𝀈   𝀈


In the middle of the game, I've sunk one of AI's ships:

    1   2   3   4   5

1   𝀈   𝀈   𝀈   𝀈   𝀈

2   𝀈   ♈   𝀈   ♈   𝀈

3   ☀   ☀   ♈   𝀈   𝀈

4   𝀈   ♈   𝀈   ♈   𝀈

5   𝀈   𝀈   𝀈   𝀈   𝀈

--------------------------

    1   2   3   4   5

1   𝀈   ♈   ▢   𝀈   ♈

2   𝀈   𝀈   ▢   𝀈   ▢

3   𝀈   𝀈   ▢   ♈   𝀈

4   ☀   𝀈   ♈   𝀈   𝀈

5   ▢   𝀈   ♈   ♈   ♈

