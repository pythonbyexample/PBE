#!/usr/bin/env python3

""" flashcards
    Note: flashcard file entries need to be separated by double dashes.
"""

import os
import sys
from os.path import exists
from random import shuffle
from textwrap import wrap
from time import sleep

from utils import TextInput, Container, getitem, nl, space


sep       = '--'
hashchar  = '#'
chars     = Container(tl='╭', tr='╮', bl='╰', br='╯', horiz='─', vert='│')
tpl       = chars.vert + '%s' + chars.vert
width     = 78
screensep = 45
cards_fn  = "cards.txt"



class Flashcards(object):
    question = " Did you get it right (Y/n)? "
    status   = "\n %s right out of %s (%d%%)\n"
    prompt   = "> "

    def __init__(self, fname):
        self.cards     = dict()
        self.textinput = TextInput(accept_blank=True, prompt=self.question)
        self.pauseinp  = TextInput(accept_blank=True)

        with open(fname) as fp:
            for line in fp:
                if line:
                    k, v = line.split(sep, 1)
                    self.cards[k.strip()] = v.strip()

    def run(self):
        right = keys = total = 0

        while True:
            keys = keys or self.get_keys()
            stat = self.status % (right, total, (right/total*100.0) if total else 0)
            right += int( self.draw_card(keys.pop(), stat) )
            total += 1

    def get_keys(self):
        keys = list(self.cards.keys())
        shuffle(keys)
        return keys

    def draw_card(self, key, status_msg):
        print(nl*screensep)
        self.box(key)
        self.pauseinp.getinput()        # instead of input() to handle quit key
        self.box(self.cards[key])
        print(status_msg)
        return self.textinput.yesno(default='y')

    def box(self, txt):
        """Box and center in screen."""
        in_width = width - 2
        topline  = space + chars.tl + chars.horiz*in_width + chars.tr
        btmline  = space + chars.bl + chars.horiz*in_width + chars.br
        padline  = space + tpl % (space * in_width)
        wrapped  = [space + tpl % wline.center(in_width) for wline in wrap(txt, width - 10)]
        lines    = [topline, padline] + wrapped + [padline, btmline]

        print(nl.join(lines))


if __name__ == "__main__":
    fname = getitem(sys.argv, 1, default=cards_fn)
    if not exists(fname):
        print("Error: %s could not be found" % fname)
        sys.exit()

    try                      : Flashcards(fname).run()
    except KeyboardInterrupt : sys.exit()
