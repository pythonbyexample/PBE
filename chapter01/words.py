#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice

from utils import TextInput, ujoin, enumerate1, range1, first, space, nl

num_words    = 6
initial_hide = 0.7
start_points = 30
hidden_char  = '_'
randcmd      = 'r'      # must be one char
wordsfn      = "words"


class Word(object):
    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def __str__(self):
        word = ( (hidden_char if n in self.hidden else l) for n, l in enumerate(self.word) )
        return ujoin(word, space*3)

    def __len__(self):
        return len(self.word)

    def guess(self, i, letter):
        """Reveal all instances of `l` if word[i] == `l` & reveal random letter in one other word."""
        if i in self.hidden and self.word[i] == letter:
            self.reveal(letter)

            L = [w for w in words if w.hidden and w != self]
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
    winmsg = "Congratulations! You've revealed all words!"

    def __init__(self, wordlist):
        self.words = set()
        while len(self.words) < num_words:
            self.words.add( Word(rndchoice(wordlist)) )
        self.words = list(self.words)

    def __getitem__(self, i) : return self.words[i]
    def __iter__(self)       : return iter(self.words)

    def display(self):
        tpl = "%2s"
        print(nl*5)

        for n, word in enumerate1(self.words):
            print(tpl % n, space, word, nl)
            lnumbers = ujoin(range1(len(word)), space*2, tpl)
            print(space*3, lnumbers, nl*2)

    def randreveal(self):
        rndchoice([w for w in self if w.hidden]).randreveal()

    def check_end(self):
        if not any(word.hidden for word in self):
            self.display()
            print(self.winmsg)
            sys.exit()


class Test(object):
    def run(self):
        self.textinput = TextInput(("%hd %hd %s", randcmd))

        while True:
            words.display()
            cmd = self.textinput.getinput()

            if first(cmd) == randcmd : words.randreveal()
            else                     : self.reveal_letter( *cmd )
            words.check_end()

    def reveal_letter(self, word, lind, letter):
        try:
            words[word].guess(lind, letter)
        except IndexError:
            print(self.textinput.invalid_move)


if __name__ == "__main__":
    words = Words( open(wordsfn).readlines() )
    Test().run()
