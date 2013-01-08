Flashcards
==========

The goal of this script is to help you memorize some of the python functions and custom classes
and functions used in the upcoming sections of this guide.

You can also create your own flashcard text files to memorize any kinds of material.

You can view or download the code here:

https://github.com/pythonbyexample/PBE/tree/master/code/flashcards.py


To run flashcards, you will also need to download 'utils.py':

https://github.com/pythonbyexample/PBE/tree/master/code/

Card
----

I will need a `Card` class which is going to store the front and back sides of a card and will be
responsible for displaying the card and getting the response to the "did you get it right" question.

The `__init__()` method parses the card's front and back text:

.. sourcecode:: python

    def __init__(self, card):
        front, back = card.split(sep, 1)
        self.front  = front.strip()
        self.back   = back.strip()

In the `draw()` method, we need to print the card front and status, pause for the user, print the
back and status again, and finally return `True` if the user got the card right.

The last part is handled by the special `yesno()` method of the `TextInput` object which returns `True`
if the user's answer is 'y'.

.. sourcecode:: python

    def draw(self, status_msg):
        print(nl*screensep)
        self.box(self.front)
        print(status_msg)
        textinput.pause.getinput()

        self.box(self.back)
        print(status_msg)
        return textinput.question.yesno(default='y')

In the `box()` method I'll use the unicode box border characters stored in the border container to
enclose the text, which is centered using the `str.center()` method.

We also need to use the `textwrap.wrap()` method to fit long strings inside the box.

.. sourcecode:: python

    def box(self, txt):
        """Center text and display border around it."""
        in_width = width - 2    # inside width
        tpl      = border.vertical + '%s' + border.vertical

        topline  = border.tl + border.horiz * in_width + border.tr
        btmline  = border.bl + border.horiz * in_width + border.br
        padline  = tpl % (space * in_width)

        wrapped  = [line for line in wrap(txt, width - 10)]
        wrapped  = [tpl % l.center(in_width) for l in wrapped]
        lines    = [topline, padline] + wrapped + [padline, btmline]

        print( nl.join(space+l for l in lines) )

Flashcards
----------

The `Flashcards` class is responsible for loading the cards and running the main loop. The `__init__()`
method goes over each line and passes it to `Card` to create the flashcard.

.. sourcecode:: python

    def __init__(self, fname):
        self.cards = list()
        with open(fname) as fp:
            for line in fp:
                if line.strip():
                    self.cards.append(Card(line))

The `run()` method does some simple stats reporting and generates a new randomized list of
cards every time it runs out of them (using `copy.copy()` and `utils.shuffled()` functions), so
that you have to go over the entire set of cards without repeating them before you have to
start over.

.. sourcecode:: python

    def run(self):
        right = cards = total = 0

        while True:
            cards   = cards or shuffled(copy(self.cards))
            percent = (right/total*100.0) if total else 0
            stat    = status % (right, total, percent)

            right += int( cards.pop().draw(stat) )
            total += 1

This code is not very efficient since it creates two copies of the `cards` list; it should be fine
for this script as you'll usually have a small number of cards, but you should not that this
approach would be too wasteful in the general case.

You can quit at any prompt by using the 'q' command.

You can also provide an alternate cards filename at the command line: `flashcards.py mycards.txt`;
otherwise the default cards.txt is used. Filename argument processing is handled using the
`utils.getitem()` function and the `sys.argv` argument list:

.. sourcecode:: python

    fname = getitem(sys.argv, 1, default=cards_fn)
    if not exists(fname):
        print("Error: %s could not be found" % fname)
        sys.exit()


Screenshots
-----------

First the script shows you the front of flashcard::

    ╭────────────────────────────────────────────────────────────────────────────╮
    │                                                                            │
    │                                 time.sleep                                 │
    │                                                                            │
    ╰────────────────────────────────────────────────────────────────────────────╯

    5 right out of 6 (83%)

    >

At this point the script waits for the user to try to remember this card and hit `Enter`, and then
to show the back of the card::

    ╭────────────────────────────────────────────────────────────────────────────╮
    │                                                                            │
    │      pause the program for a period of time e.g. 0.5 - half a second       │
    │                                                                            │
    ╰────────────────────────────────────────────────────────────────────────────╯

    5 right out of 6 (83%)

    Did you get it right (Y/n)?
