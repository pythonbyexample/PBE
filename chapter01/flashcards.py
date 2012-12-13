#!/usr/bin/env python3

""" flashcards - helps to memorize a set of data loaded from a text file by showing front, then
    back of the flash card.

    Note: flashcard file entries need to be separated by double dashes (see `sep` setting)
"""

import sys
from os.path import exists
from random import shuffle
from textwrap import wrap
from time import sleep
from copy import copy

from utils import TextInput, Container, getitem, nl, space


width     = 78
screensep = 30
border    = Container(tl='╭', tr='╮', bl='╰', br='╯', horiz='─', vertical='│')
cards_fn  = "cards.txt"
question  = " Did you get it right (Y/n)? "
status    = "\n %d right out of %d (%d%%)\n"
sep       = "--"

textinput = Container(question = TextInput(accept_blank=True, prompt=question),
                      pause = TextInput(accept_blank=True))


class Card(object):
    def __init__(self, cards, card):
        front, back = card.split(sep, 1)
        self.front  = front.strip()
        self.back   = back.strip()
        cards.append(self)

    def draw(self, status_msg):
        print(nl*screensep)
        self.box(self.front)
        print(status_msg)
        textinput.pause.getinput()

        self.box(self.back)
        print(status_msg)
        return textinput.question.yesno(default='y')

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


class Flashcards(object):
    def __init__(self, fname):
        self.cards = list()
        with open(fname) as fp:
            for line in fp:
                if line.strip():
                    Card(self.cards, line)

    def run(self):
        right = cards = total = 0

        while True:
            cards   = cards or self.get_cards()
            percent = (right/total*100.0) if total else 0
            stat    = status % (right, total, percent)

            right += int( cards.pop().draw(stat) )
            total += 1

    def get_cards(self):
        cards = copy(self.cards)
        shuffle(cards)
        return cards


if __name__ == "__main__":
    fname = getitem(sys.argv, 1, default=cards_fn)
    if not exists(fname):
        print("Error: %s could not be found" % fname)
        sys.exit()

    try                      : Flashcards(fname).run()
    except KeyboardInterrupt : sys.exit()
