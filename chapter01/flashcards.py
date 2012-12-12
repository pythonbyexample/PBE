#!/usr/bin/env python3

""" flashcards
    Note: flashcard file entries need to be separated by double dashes.
"""

import os
import sys
from os.path import exists
from random import shuffle
from utils import TextInput, getitem, nl, space


sep       = '--'
hashchar  = '#'
tpl       = hashchar + '%s' + hashchar
width     = 78
screensep = 45
cards_fn  = "cards.txt"


class Flashcards(object):
    question = "Did you get it right (Y/n)? "
    status   = "%s right out of %s (%d%%)"

    def __init__(self, fname):
        self.cards     = dict()
        self.textinput = TextInput(accept_blank=True)

        with open(fname) as fp:
            for line in fp:
                if line:
                    k, v = line.split(sep, 1)
                    self.cards[k.strip()] = v.strip()

    def run(self):
        right = keys = total = 0

        while True:
            keys = keys or self.get_keys()
            right += int( self.draw_card(keys.pop()) )
            total += 1
            print(self.status % (right, total, right/total*100.0))

    def get_keys(self):
        keys = list(self.cards.keys())
        shuffle(keys)
        return keys

    def draw_card(self, key):
        print(nl*screensep)
        self.box(key)
        self.textinput.getinput()
        self.box(self.cards[key])

        return self.textinput.yesno(default='y', prompt=self.question)

    def box(self, txt):
        """Box and center in screen."""
        line     = hashchar*width
        in_width = width - 2

        print(line)
        print(tpl % (space*in_width))
        print(tpl % txt.center(in_width))
        print(tpl % (space*in_width))
        print(line)


if __name__ == "__main__":
    fname = getitem(sys.argv, 1, default=cards_fn)
    if not exists(fname):
        print("Error: %s could not be found" % fname)
        sys.exit()

    try                      : Flashcards(fname).run()
    except KeyboardInterrupt : sys.exit()
