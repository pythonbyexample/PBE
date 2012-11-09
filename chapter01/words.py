#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import os
from random import choice as rndchoice
from string import letters

from utils import ujoin

num_words    = 6
initial_hide = 0.7
start_points = 30
hiddenltr    = '_'
nl           = '\n'
space        = ' '

wordsfn      = "words"
testwords    = "sunny clouds snowflake".split()


class Word(object):
    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def __len__(self):
        return len(self.word)

    def guess(self, i, letter):
        """Reveal all instances of `l` if word[i] == `l` & reveal random letter in one other word."""
        if i in self.hidden and self.word[i] == letter:
            self.reveal(letter)
            lst = [w for w in words if len(w.hidden) > 1 and w != self]
            if lst:
                rndchoice(lst).revealrnd()
            return True

    def reveal(self, letter):
        """Reveal all letters equal to `letter`."""
        for n, ltr in enumerate(self.word):
            if ltr == letter:
                self.hidden.remove(n)

    def revealrnd(self):
        """Reveal a random letter."""
        self.reveal(self.word[ rndchoice(self.hidden) ])

    def hide(self, num):
        """Hide all letters matching letter at index `n`."""
        if num not in self.hidden:
            for n, ltr in enumerate(self.word):
                if ltr == self.word[num]:
                    self.hidden.append(n)

    def gen_hidden(self, hidden):
        """Hide letters according to `hidden`, e.g. if 0.7, hide 70%."""
        length      = len(self)
        num_to_hide = round(length * hidden)
        while len(self.hidden) < num_to_hide:
            self.hide(rndchoice( range(length) ))

    def __str__(self):
        word = ( (hiddenltr if n in self.hidden else l) for n, l in enumerate(self.word) )
        return space.join(word)


def display():
    print(ujoin(words, nl), nl)

def main():
    display()
    words[0].revealrnd()
    display()

    word = words[2]
    word.guess(0, 's')
    display()
    word.guess(1, 'n')
    display()


if __name__ == "__main__":
    wordlist = open(wordsfn).readlines()
    words    = [Word(word) for word in testwords]
    main()
