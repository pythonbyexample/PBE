Robots
======

The aim of this game is to write a program for your robot that leads him to the goal within the
allotted number of turns.

https://github.com/pythonbyexample/PBE/tree/master/code/robots.py

To run Robots, you will also need to download 'board.py' and 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Tiles
-----

This game has a lot more different tiles compared to previous games; to make it a little
easier to deal with all of them, I've automated the assignment of tile characters and healths by
using the special `__class__.__name__` attributes.

.. sourcecode:: python

    chars         = dict(Player='☺', Missile='*', Rock='☗', Goal='⚑', Blank='.', Robot='♉')
    health_dict   = dict(Player=5, Robot=5, Missile=1, Rock=10, Goal=99)

    class Tile(BaseTile):
        player = robot = blank = missile = rock = goal = False
        health = None

        def __init__(self, loc):
            super(Tile, self).__init__(loc)
            self.char   = chars.get(self.__class__.__name__)
            self.health = health_dict.get(self.__class__.__name__)
            if loc: board[loc] = self

        def __repr__(self):
            return self.char

        def destroy(self):
            """Note: we need to check for `loc` for a special case of a missile with loc=None."""
            if self.loc: del board[self.loc]


    class Blank(Tile) : pass
    class Rock(Tile)  : pass
    class Goal(Tile)  : pass

The `Mobile` tile is the parent for robots, the player and missile tiles. It has the following
action-handling methods: turn clockwise and counter-clockwise, wait, execute random action, fire a
missile, move one tile ahead.

.. sourcecode:: python

    class Mobile(Tile):
        turn = 1

        def __init__(self, loc=None, direction=None):
            super(Mobile, self).__init__(loc)
            self.direction = direction or Loop(board.dirlist2, name="dir")
            self.program   = []

        def go(self):
            self.program = self.program or self.create_program()
            cmd = getattr(self, self.program.pop(0))
            cmd()
            self.turn += 1

        def turn_cw(self)  : self.direction.next()
        def turn_ccw(self) : self.direction.prev()
        def wait(self)     : pass

        def random(self):
            method = getattr(self, rndchoice(fullcmds))
            method()

        def fire(self):
            start = board.next_tile(self, self.direction.dir)

            if not start     : return
            elif start.blank : Missile(start.loc, self.direction).go()
            else             : Missile().hit(start)

        def move(self):
            tile = board.next_tile(self, self.direction.dir)

            if tile and tile.blank : board.move(self, tile.loc)
            else                   : self.program = []

        def create_program(self):
            return [rndchoice(fullcmds)] * randint(1, 6)


The `create_program()` method creates a random program (used by the AI), and `go()` executes the next
step in the current program.

The `fire()` method requires some explanation: if there is no space ahead, we do nothing; if there
is a blank space, the missile is sent on its merry way, but if there is no blank space, there is a
slight problem: we have nowhere to place the missile, so we need to create a special type of
missile which has no location and no direction (it's a really aimless missile in its own age of
adolescence); immediately after creation, the missile hits its target straight out of nowhere.

The robot and player tiles are similar but the player needs some additional processing when it
moves -- to tell if it has won the game by reaching the goal or lost by failing to do so before its
turns ran out.

.. sourcecode:: python

    class Robot(Mobile):
        # def __repr__(self): return str(self.health)

        def destroy(self):
            del board[self]
            robots.remove(self)


    class Player(Mobile):
        status_msg = "%shp | %s"

        def move(self):
            tile = board.next_tile(self, self.direction.dir)
            if tile and tile.goal:
                board.move(self, tile.loc)
                rgame.game_end(True)

            super(Player, self).move()
            if self.turn >= max_turns:
                rgame.game_end(False)

        def status(self):
            return self.status_msg % (self.health, board.dirnames[self.direction.dir])

        def destroy(self):
            del board[self]
            players.remove(self)


Finally, the missile keeps flying along its way until it hits something; once it hits, it may
destroy the target if it has no health left (otherwise it just decrements the health).

.. sourcecode:: python

    class Missile(Mobile):
        def go(self):
            while True:
                tile = board.next_tile(self, self.direction.dir)

                if not tile:
                    self.destroy()
                    break
                elif tile.blank:
                    board.move(self, tile.loc)
                    board.draw(missile_pause)
                else:
                    self.hit(tile)
                    break

        def hit(self, target):
            target.health -= 1
            if not target.health:
                target.destroy()
            self.destroy()


RBoard
------

The board only provides a random blank location and combined status of all players.

.. sourcecode:: python

    class RBoard(Board):
        stat_sep = " | "

        def random_blank(self):
            return rndchoice(self.locations("blank"))

        def status(self):
            print( nl, self.stat_sep.join(p.status() for p in players) )

RobotsGame
----------

The main class handles game end with win/lose messages and expands the player's program (I'll
explain this in more detail in the following section).

.. sourcecode:: python

    class RobotsGame(object):
        winmsg  = "Victory! You've reached the goal!"
        losemsg = "You failed to reach the goal in %d turns.."

        def game_end(self, win):
            board.draw()
            print( nl, self.winmsg if win else (self.losemsg % max_turns) )
            sys.exit()

        def expand_program(self, cmds):
            L = []
            while True:
                if not cmds: break
                count = 1
                cmd   = cmds.pop(0)

                if isinstance(cmd, int):
                    count, cmd = cmd, cmds.pop(0)

                L.extend( [commands[cmd]] * count )
            return L


BasicInterface
--------------

The player can submit the program in the following format: "Ncmd1 Ncmd2 ...", for example:

    m 2t 3m T 2f

 -- this means move one tile, make 2 clockwise turns (each turn being 45 degrees), move 3
tiles, make counter clockwise turn, fire 2 missiles.

(See commands dict at the top of file for a full list of actions).

The `singlechar_cmds` argument is needed to allow the player to group multiple commands using
spaces. Without this argument each command and its count would have to be separated, e.g.: "3 m
2 f". The trade-off is that this option does not allow you to enter counts larger than 9, so to
move 15 tiles you'd need to enter "9m 6m", but this shouldn't be a problem for this game as
large counts are rarely needed.

.. sourcecode:: python

    class BasicInterface(object):
        def run(self):
            cmdpat  = "%d?"
            cmdpat  = cmdpat + " (%s)" % sjoin(commands.keys(), '|')
            pattern = cmdpat + (" %s?" % cmdpat) * (max_cmds - 1)

            self.textinput = TextInput(pattern, board, accept_blank=True, singlechar_cmds=True)

            while True:
                board.draw()
                for unit in players + robots:
                    cprog        = self.create_program if unit.player else unit.create_program
                    unit.program = unit.program or cprog()
                    unit.go()

        def create_program(self):
            while True:
                try:
                    program = self.textinput.getinput() or ['r']
                    return rgame.expand_program(program)
                except (KeyError, IndexError):
                    print(self.textinput.invalid_inp)

Configuration
-------------

You can set `num_players` to 0 to look at robots run random programs continuously, to 1 for a
single player and to 2 for human vs. human game; you can also adjust `max_turns` to make it
harder or easier to reach the goal. As with other games, you can change `size` to make a larger
game board.

.. sourcecode:: python

    size          = 15, 10
    num_players   = 1
    num_robots    = 6
    num_rocks     = 5

    pause_time    = 0.2
    missile_pause = 0.03
    max_turns     = 25
    max_cmds      = 15

Screenshots
-----------

In the screenshots below, the smiley is the player robot, guys with antennas are the other
robots, black shapes are rocks and the flag is the goal. In the first screen I'm one turn from
reaching the goal, and in the next screen I win the game! ::

    . ♉ . . . . . . . . . . . . .
    . . . ♉ ☗ . . . . . . . . . .
    ⚑ . . . ☗ . . . . . . . . . .
    ☺ . . . . . . . . . . . . . .
    . . . . . . ☗ . . . . ♉ . . .
    . . . ♉ . . . . . . . . . . .
    . . . . . . . . . . . . . . .
    . . ♉ . . . . . . . . . . . ♉
    . . . . . . . . . . . . . . .
    . . . . . . . . ☗ . ☗ . . . .

    4hp | up






    . ♉ . . . . . . . . . . . . .
    . . . ♉ ☗ . . . . . . . . . .
    ☺ . . . ☗ . . . . . . . . . .
    . . . . . . . . . . . . . . .
    . . . . . . ☗ . . . . ♉ . . .
    . . . ♉ . . . . . . . . . . .
    . . . . . . . . . . . . . . .
    . . ♉ . . . . . . . . . . . ♉
    . . . . . . . . . . . . . . .
    . . . . . . . . ☗ . ☗ . . . .

    4hp | up

    Victory! You've reached the goal!

