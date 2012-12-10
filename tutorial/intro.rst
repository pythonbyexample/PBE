Introduction
============

This chapter will introduce you to some of the basics of programming in Python.

Requirements
------------

To use this guide, the minimal requirement is the `Python Interpreter
<http://www.python.org/download/>`_ version 3.2+, but I'd also recommend getting a good programming
editor that support auto-indenting and syntax highlighting for Python.

If you're completely new to Python and programming, it might be best to
quickly look through the `Official Python Tutorial <http://docs.python.org/tutorial>`_.

My guide will mostly use short, simple games to teach Python and Programming in general.

NOTE
----
I will not be showing full code in the code listings to keep things short and simple (I will omit
import lines and other minor things); you should download (or view) the source files at the url given
below to view the entire code.

Windows Note
------------

On windows it's probably best to run scripts from inside IDLE which is installed with python by
using the F5 shortcut.

Where is the code?
------------------

You can download all of the code here:

https://github.com/pythonbyexample/PBE/tree/master/code

To run the two intro programs, you will need to download one additional file: utils.py

Intro Part I
------------
https://github.com/pythonbyexample/PBE/tree/master/code/intro1.py

This little program will show how to use class inheritance. Four trees are created, two of them
are Bamboo trees (bamboo is really a type of grass, but..), and the other two are Birches. Both
types of trees grow fast, but Bamboo is by far the fastest; individual trees may have different
rate of growth based on environment factors.

I'll start by defining the parent Tree class and two classes for the types of our trees:

.. sourcecode:: python

    class Tree(object):
        height = 0

        def __repr__(self):
            return "<%s tree, %.1f ft>" % (self.name, self.height)

        def grow(self):
            self.height += self.growth_rate + self.growth_rate * random() / 3

    class Bamboo(Tree):
        growth_rate = 10
        name        = "Bamboo"

    class Birch(Tree):
        growth_rate = 1.2
        name        = "Birch"

A few things to note:

- `Bamboo` and `Birch` inherit from `Tree`
- all start with `height` of 0, inherited from `Tree`
- `Bamboo` and `Birch` have different growth rates
- `__repr__` is a special method that displays the tree's information when tree instance is
  printed to screen
- all trees have `grow()` method that grows the tree based on its rate and adds a small random
  variation

In the `main()` function I will create four trees, grow each of them once, then grow each of them
five times, displaying the trees after each change:

.. sourcecode:: python

    def main():
        trees = Bamboo(), Bamboo(), Birch(), Birch()
        print(trees, nl)

        for tree in trees: tree.grow()
        print(trees, nl)

        for _ in range(5):
            for tree in trees: tree.grow()
        print(trees, nl)

    main()


Note that `nl` is a newline character I've imported from the utils module, it adds a blank line
when given to `print()` function.

The output should be something like::

    (<Bamboo tree, 0.0 ft>, <Bamboo tree, 0.0 ft>, <Birch tree, 0.0 ft>, <Birch tree, 0.0 ft>)

    (<Bamboo tree, 10.0 ft>, <Bamboo tree, 10.4 ft>, <Birch tree, 1.4 ft>, <Birch tree, 1.4 ft>)

    (<Bamboo tree, 67.1 ft>, <Bamboo tree, 73.8 ft>, <Birch tree, 8.5 ft>, <Birch tree, 8.3 ft>)

Both Bamboo trees are much taller than Birches, but there are some minor height differences inside
the same type as well.


Intro Part II
-------------
https://github.com/pythonbyexample/PBE/tree/master/code/intro2.py

One of the simplest games you can make (and also one of the oldest games known) is a race game
where each player races along the track (or a playing board) and tries to reach the end before the
other player. I will not make the complete game in this chapter; I'll simply make two racing
tracks and demonstrate how playing pieces can be added and moved around.

The general idea is that the racing track is a python list, the player is a represented by a the
'@' character, and blank spaces are shown as dots. I'll need to have a function that prints out
the `track` and one that moves the player to another spot:

.. sourcecode:: python

    blank   = '.'
    char    = '@'
    loc     = 0
    length  = 79
    forward = 1
    back    = -1
    track   = [blank] * length


    def move(dir, n):
        """Move `n` times in `dir` direction."""
        global loc
        track[loc] = blank

        loc = loc + dir*n
        loc = envelope(loc, 0, lastind(track))
        track[loc] = char

    def display():
        print(''.join(track), nl)

In `move()` function I need to set the current location to blank, calculate the new location and place
my character there.

The `envelope()` function (imported from the `utils` module) forces location to be within valid
range and accepts three arguments: the value itself, lower bound, and higher bound.

I'm using one more function from the `utils` module: `lastind()` returns last valid index for an
iterable (e.g. 9 if iterable length is 10, 19 if 20, etc).

.. sourcecode:: python

    def demo1():
        print("demo1")
        display()
        track[loc] = char
        display()

        move(forward, 10)
        display()
        move(back, 2)
        display()

Hopefully this is clear enough. We're moving forward by ten steps and then back by two::

    demo1
    ...............................................................................

    @..............................................................................

    ..........@....................................................................

    ........@......................................................................

What if I want to put some sort of "things" on the path and let players move on top of them
without erasing them? Simple! I'll just use a list of lists for my track and change the `move()`
accordingly:

.. sourcecode:: python

    loc2   = 0
    track2 = [[blank] for _ in range(length)]

    def move2(dir, n):
        global loc2
        track2[loc2].remove(char)

        loc2 = loc2 + dir*n
        loc2 = envelope(loc2, 0, lastind(track2))
        track2[loc2].append(char)

    def display2():
        print( ''.join( x[-1] for x in track2 ), nl )

Instead of printing all items in `track`, I'm only displaying the last, i.e. 'top' item using
index `-1`.

In `move()`, I am now removing and appending the item to the list at location `loc`, ensuring that
other items at these locations are not affected.


.. sourcecode:: python

    def demo2():
        print("demo2")

        display2()
        track2[loc2].append(char)
        move2(back, 10)
        display2()
        move2(forward, 10)
        move2(back, 2)
        display2()

        dice = Dice()
        print(dice.roll())

        x = dice.rollsum()
        print("x =", x)
        move2(forward, x)
        display2()

To add some randomness, I'm using the `Dice` object from `utils`: by default it creates two dice
with 6 sides each, but it's possible to specify any number of dice and sides. `Dice` has two
methods: `roll()` will return the list of rolls for each dice; sometimes you won't care about the
individual dice -- `rollsum()` will provide the total of all rolls in these cases.

    demo2
    ...............................................................................

    @..............................................................................

    ........@......................................................................

    [2, 2]
    x = 9
    .................@.............................................................
