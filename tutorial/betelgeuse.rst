Betelgeuse
==========

Betelgeuse is a game of star conquest: the goal is to take over all of the enemy's star systems.

https://github.com/pythonbyexample/PBE/tree/master/code/betelgeuse.py

To run Betelgeuse, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

PlayerBase
----------

I will need to compare game instance that may belong to one or the other player: stars, fleets and
the player himself. I'll need a class that handles this logic which will be the parent for all
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

I will only need two types of tiles for this game: Blanks and Stars. The `Blank` tile does not
need to do anything; the `Star` has a production setting which determines how many new ships are
built in each cycle in `run()` method.

When a star is displayed, it will always show its statistics when its owner is the human player,
otherwise stats may be hidden depending on the `show_ships` setting.

The `go()` method builds new ships; production volume is halved for neutral players.


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
out the status message (current turn).

.. sourcecode:: python

    class BetelgeuseBoard(Board):
        stat = "turn: %d"

        def random_blank(self) : return randchoice(self.locations("blank"))
        def status(self)       : print(self.stat % betelgeuse.turn)

Fleet
-----

The star fleet is created when you send a number of ships from one star to another, whether to
conquer or reinforce the destination star. The fleet 'knows' when to arrive by using the arrival
attribute which is the game turn of arrival.

The `go()` method compares the fleet to the destination star and determines if it needs to attack
or reinforce it; it's crucial that this check is done on arrival instead of launch time because
the star may be conquered by another fleet, yours or enemy's, while the fleet is in transit. If
that were to happen, you'd have a rather awkward situation where your fleet attacks your own
forces or reinforces enemy's garrison!

.. sourcecode:: python

    def __init__(self, char, origin, star, ships):
        self.char    = char
        self.origin  = origin
        self.star    = star     # target star
        self.ships   = ships
        self.arrival = betelgeuse.turn + round(board.dist(origin.loc, star.loc) / 2)
        origin.ships -= ships

    def __repr__(self):
        eta = self.arrival - betelgeuse.turn
        return "(%s %s %s s:%d, a:%d)" % (self.char, self.origin.num, self.star.num, self.ships, eta)

    def go(self):
        if betelgeuse.turn >= self.arrival:
            if self == self.star : self.land()
            else                 : self.attack()

Ship combat is handled by having ships fight one at a time, using random function and the
`star_defence` setting to determine the loser, until one side has no ships left.

.. sourcecode:: python

    def attack(self):
        """Note: need to do checks at the start of loop in case there are no ships in `star`."""
        while True:
            if not self.ships      : self.dismiss(); break
            if not self.star.ships : self.land(conquer=True); break
            loser = self.star if random() > star_defence else self
            loser.ships -= 1


In the `land()` method, 'conquer' argument is not used, but you can uncomment the print line to
show the fleet victory message if you like.

.. sourcecode:: python

    def land(self, conquer=False):
        # if conquer: print(self.conquer_msg % (self.char, self.star.num))
        self.star.char = self.char
        self.star.ships += self.ships
        self.dismiss()

    def dismiss(self):
        fleets.remove(self)


Player
------

The Player class has a small utility method which returns all of Player's stars and all other
stars, a method handling creation of fleets and the `make_random_moves()` and `random_move()`
methods used by the AI.

.. sourcecode:: python

    def __init__(self, char):
        self.char = char
        self.ai   = bool(char in ai_players)

    def stars(self)       : return [s for s in stars if s==self]
    def other_stars(self) : return [s for s in stars if s!=self]

    def send(self, *args):
        fleets.append( Fleet(self.char, *args) )

The logic of the AI moves is as follows: we need to go over all of player's stars, based on a
random check and the number of ships, decide whether we wish to send a fleet; if sending a fleet,
we should pick the closest target and return the source star, destination and the number of ships
to send.

It is important to check if there are no targets at all because the game continues even if the
enemy has no stars left as long as he has at least one fleet.

.. sourcecode:: python

    def make_random_moves(self):
        moves = [self.random_move(star) for star in self.stars()]
        for move in moves:
            if move: self.send(*move)

    def random_move(self, star):
        def dist(star2): return board.dist(star, star2)

        if random() < send_chance and star.ships >= send_cutoff:
            targets = sorted(self.other_stars(), key=dist)
            if not targets: return None

            ships = randint(star.ships // 2, star.ships)
            return star, first(targets), ships

Betelgeuse
----------

The easiest way to check if only one player is left standing is to make a set of player characters
and check if its length is '1'.

.. sourcecode:: python

    class Betelgeuse(object):
        winmsg            = "Player %s wins!"
        turn              = 1
        show_ships_player = None

        def check_end(self):
            pchars = set(sf.char for sf in stars+fleets if sf.char != neutral_char)

            if len(pchars) == 1:
                board.draw()
                print(nl, self.winmsg % first(pchars))
                sys.exit()

BasicInterface
--------------

Unlike the games in previous sections, in Betelgeuse the player can make multiple moves per turn.
A move has to specify the source star, the destination and the number of ships to send; to end the
turn, the player simply hits Enter on an empty prompt.

At first, the player needs to wait for his star to produce spaceships by waiting a few turns.

If the player controls star #2 and wishes to attack star #5 with 10 ships, the command would
be: `2 5 10`.

The `run()` method handles each of player's turns, draws the Board, checks for the end of game and
lets stars and fleets handle their production/movement.

.. sourcecode:: python

    def run(self):
        self.textinput = TextInput("%hd %hd %d", board, accept_blank=True)

        while True:
            for player in players:
                betelgeuse.show_ships_player = None if player.ai else player
                board.draw()
                player.make_random_moves() if player.ai else self.make_moves(player)
                betelgeuse.check_end()

            for sf in stars + fleets: sf.go()
            betelgeuse.turn += 1

The `make_moves()` methods handles all moves in a turn; `get_move()` returns a single move.

It's important for `_make_move()` method to make sure that the source star actually belongs to the
player and that it has enough ships to send the fleet, otherwise the Player who only has five
ships would be able to send 500 and win the game -- and we can't allow that!

.. sourcecode:: python

    def make_moves(self, player):
        while True:
            cmd = self.get_move(player)
            if not cmd: break
            player.send(*cmd)
            board.draw()

    def get_move(self, player):
        while True:
            try:
                return self._get_move(player)
            except (IndexError, AssertionError):
                print(self.textinput.invalid_move)

    def _get_move(self, player):
        cmd = self.textinput.getinput()
        if not cmd: return

        src, goal, ships = cmd
        src, goal = stars[src], stars[goal]
        assert src == player and src.ships >= ships
        return src, goal, ships

The Player can always quit the game by entering the 'q' command.

Configuration
-------------
By default the playing board is large and you need to maximize your terminal window to play;
you can change the `size`, of course.

You can play human vs. human by setting `ai_players` empty, AI vs AI by setting it to include all AI
players, and human vs AI by omitting one player. You can have more than two players; read the
comments for other options:

.. sourcecode:: python

    size           = 8, 6
    player_chars   = '⎔▣'
    # ai_players     = '⎔'
    ai_players     = '⎔▣'

    neutral_char   = '⊛'
    blank          = '.'
    padding        = 13, 4

    pause_time     = 0.3
    num_stars      = 6
    show_ships     = True   # show production and # of ships for all stars

    star_turns     = 5      # star production cycle
    star_defence   = 0.6    # star defense rating: degree of advantage for defenders, must be less than 1.0
    production_rng = 8, 12  # range of star production, ships per cycle
    send_chance    = 0.4    # chance of sending a fleet, used by AI
    send_cutoff    = 25     # only send a fleet if have >=N, used by AI

Screenshots
-----------

(The alignment is slightly off in HTML shown here but works fine in the terminal.)

The star system I'm playing is on the bottom, to the right, the enemy AI is to the left of
me, my system is #1 and has 10 production and 10 ships. All the other star systems are neutral::

    .              .              .              .              .              .              .       ⊛ 5 11:5




    .              .        ⊛ 3 8:4              .              .              .              .              .




    .              .        ⊛ 6 8:4              .              .              .              .              .




    .              .              .              .              .              .              .              .




    .              .              .              .              .              .              .              .




    ⊛ 4 12:6              .              .              .        ▣ 2 8:8      ⎔ 1 10:10              .              .




    turn: 6
    >

