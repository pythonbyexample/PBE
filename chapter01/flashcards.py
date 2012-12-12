#!/usr/bin/env python3

"""flashcards

Notes: flashcard file entries need to be separated by dashes, or, if dashes are present in a key,
       by double dashes.

Usage: ./flashcards.py [-n show_num] <cards_file>

Written by AK <ak@lightbird.net>
"""

import os
import sys
from optparse import OptionParser
from os.path import join as pjoin
from string import join, center
from avkutil import Term
from random import shuffle


__version__ = "0.1"


dash      = '-'
dash2     = '--'
nl        = '\n'
space     = ' '
hashchar  = '#'
tpl       = hashchar + '%s' + hashchar
width     = 78
screensep = 45

class Flashcards(object):
    question = "Did you get it right (Y/n)? "
    donemsg  = "Done, %s right out of %s (%d%%)"

    def main(self, options, args):
        num        = int(options.num)
        self.cards = dict()

        with open(args[0]) as fp:
            for line in fp:
                if line:
                    k, v = line.split(dash2, 1)
                    self.cards[k.strip()] = v.strip()

        rkeys = d.keys()
        shuffle(rkeys)

        t      = Term()
        right  = 0
        length = num or len(rkeys)

        for n, key in enumerate(rkeys):
            right += int(self.draw_card(n, key))
            if n + 1 == length:
                break

        print nl*2 + dash*width
        print(self.donemsg % (right, length, right/length*100.0))

    def draw_card(self, n, key):
        print(nl*screensep)
        print("%s / %s" % (n+1, length))
        box(self.cards[key])
        c = t.getch()
        print(nl*2)
        self.box(key)
        print(self.question)
        sys.stdout.flush()
        c = t.getch()

        if c in 'y\n':
            return 1

    def box(self, txt):
        """Box and center in screen."""
        line     = hashchar*width
        in_width = width - 2

        print(line, nl, line)
        print(tpl % space*in_width)
        print(tpl % center(txt, in_width))
        print(tpl % space*in_width)
        print(line, nl, line)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--num", dest="num", help="Number of cards to show.",
      default=0)
    options, args = parser.parse_args()
    if not args:
        print "Need one arg."; sys.exit()

    try:
        Flashcards().main(options, args)
    except KeyboardInterrupt:
        sys.exit()
