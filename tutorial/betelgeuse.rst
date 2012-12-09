Betelgeuse
==========

Betelgeuse is a game of star conquest: the goal is to take over all of the enemy's star systems.

https://github.com/pythonbyexample/PBE/tree/master/code/betelgeuse.py

To run Betelgeuse, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

PlayerBase
----------

I will need to compare game instance that may belong to one or the other player: stars, fleets and
the player himself. We'll need a class that handles this logic which will be the parent for all
three classes:

.. sourcecode:: python

    class PlayerBase(object):
        """Used as base for all player's stars and fleets as well as Player class itself, to allow for
           making equality checks between all of them.
        """
        def __eq__(self, other) : return bool(self.char == other.char)
        def __ne__(self, other) : return bool(self.char != other.char)
        def __repr__(self)      : return self.char

Tiles
-----

I'll only need two types of tiles for this game: blanks and stars. The blank tile does not need to
do anything and the Star has some interesting functionality: first, it has a production setting
which determines how many new ships are built in each cycle in run() method.

When a star is displayed, it will always show its statistics when its owner is the human player,
otherwise stats may be hidden depending on the show_ships setting.

The go() method builds new ships; production volume is halved for neutral players.


.. sourcecode:: python

    class Tile(BaseTile, PlayerBase) : blank = star = False
    class Blank(Tile)                : char = blank

    class Star(Blank):
        char  = neutral_char
        ships = 0

        def __init__(self, loc, num):
            super(Star, self).__init__(loc)
            self.num        = num
            self.production = randint(*production_rng)
            board[loc]      = self

        def __repr__(self):
            data = [self.char, self.num]
            if show_ships or self == betelgeuse.show_ships_player:
                data.append("%s:%s" % (self.production, self.ships))
            return sjoin(data, space)

        def go(self):
            if betelgeuse.turn % star_turns == 0:
                self.ships += self.production if (self in players) else (self.production // 2)

Board
-----

The game board is very simple: it provides a random blank locations for star placement and prints
out status message (current turn).

.. sourcecode:: python

Fleet
-----

The star fleet is created when you send a number of ships from one star to another, whether to
conquer or reinforce the destination star. The fleet 'knows' when to arrive by using the arrival
attribute which is the game turn of arrival.

The go() method compares fleet to the destination star and determines if it needs to attack or
reinforce it; it's crucial that this check is done on arrival instead of launch time because the
star may be conquered by another fleet, yours or enemy's , while the fleet is in transit. If that
were to happen, you'd have a rather awkward situation where your fleet attacks your own forces or
reinforces enemy's garrison!

Ship combat is handled by having ships fight one at a time, using random function and the
star_defence setting to determine the loser, until one side has no ships left.

In the land() method, 'conquer' argument is not used, but you can use it to print the fleet
victory message if you like.

.. sourcecode:: python

Player
------

The Player class has a small utility method which returns all of Player's stars and all other stars, a method handling
creation of fleets and the makr_random_moves & random_move() methods used by the AI.

The logic of AI moves is as follows: we need to go over all of player's stars, based on a random
check and the number of ships, decide whether we wish to send a fleet; if sending a fleet, we
should pick the closest target and return the source star, destination and the number of ships to
send.

It is important to check if there are no targets at all because the game continues even if the
enemy has no stars left as long as he has at least one fleet.

.. sourcecode:: python

Betelgeuse
----------

The easiest way to check if only one player is left standing is to make a set of player characters
and check if its length is '1'.

.. sourcecode:: python

BasicInterface
--------------

Unlike the games in previous sections, in Betelgeuse the player can make multiple moves per turn.
A move has to specify the source star, the destination and the number of ships to send; to end the
turn, the player simply hits Enter on an empty  prompt.

The run() method handles each of player's turns, draws the Board, checks for the end of game and
lets stars and fleets handle their production/movement.

The make_moves() methods handles all moves in a turn; make_move() performs a single move.

It's important for _make_move() method to make sure that the source star actually belongs to the
player and that it has enough ships to send the fleet, otherwise the Player who only has five
ships would be able to send 500 and win the game -- wand we can't allow that.

The Player can always quit the game by entering the 'q' command.

.. sourcecode:: python

Configuration
-------------

You can play human vs. human by setting ai_players empty, AI vs AI by setting it to include all AI
players, and human vs AI by omitting one player. You can have more than two players. Read the
comments for other options:


.. sourcecode:: python


Screenshots
-----------
