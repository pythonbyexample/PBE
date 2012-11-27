#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import os
from random import choice as rndchoice
from string import letters

from utils import ujoin, space, nl

num_words    = 6
initial_hide = 0.7
start_points = 30
hidden_char  = '_'

wordsfn      = "words"
testwords    = "sunny clouds snowflake".split()


class Word(object):
    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def __str__(self):
        word = ( (hidden_char if n in self.hidden else l) for n, l in enumerate(self.word) )
        return space.join(word)

    def guess(self, i, letter):
        """Reveal all instances of `l` if word[i] == `l` & reveal random letter in one other word."""
        if i in self.hidden and self.word[i] == letter:
            self.reveal(letter)

            L = [w for w in words if len(w.hidden) > 1 and w != self]
            if L: rndchoice(L).randreveal()
            return True

    def reveal(self, letter):
        """Reveal all letters equal to `letter`."""
        for n, nletter in enumerate(self.word):
            if nletter == letter:
                self.hidden.remove(n)

    def randreveal(self):
        """Reveal a random letter."""
        self.reveal( self.word[rndchoice(self.hidden)] )

    def hide(self, index):
        """Hide all letters matching letter at `index`."""
        if index not in self.hidden:
            for n, nletter in enumerate(self.word):
                if nletter == self.word[index]:
                    self.hidden.append(n)

    def gen_hidden(self, hidden):
        """Hide letters according to `hidden`, e.g. if 0.7, hide 70%."""
        length      = len(self.word)
        num_to_hide = round(length * hidden)

        while len(self.hidden) < num_to_hide:
            self.hide( rndchoice(range(length)) )


class Words(object):
    pass

def display():
    print(ujoin(words, nl), nl)

def main():
    display()
    words[0].randreveal()
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
