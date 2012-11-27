#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice

from utils import TextInput, ujoin, enumerate1, range1, first, space, nl

num_words      = 2
initial_hide   = 0.7
hidden_char    = '_'
randcmd        = 'r'      # must be one char

wordsfn        = "words"
limit_9        = True
random_reveals = num_words // 2
guesses_divby  = 3


class Word(object):
    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def __str__(self):
        word = ( (hidden_char if n in self.hidden else l) for n, l in enumerate(self.word) )
        return ujoin(word, space * self.spacing())

    def spacing(self):
        return 3 if len(self) > 9 else 2

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
    winmsg  = "Congratulations! You've revealed all words! (score: %d)"
    losemsg = "You've ran out of guesses.."
    stattpl = "random reveals: %d | attempts: %d"

    def __init__(self, wordlist):
        self.random_reveals = random_reveals
        self.words = set()

        while len(self.words) < num_words:
            word = rndchoice(wordlist).rstrip()
            if limit_9 and len(word)>9: continue
            self.words.add(Word(word))

        self.words   = list(self.words)
        self.guesses = sum(len(w) for w in self.words) // guesses_divby

    def __getitem__(self, i) : return self.words[i]
    def __iter__(self)       : return iter(self.words)

    def display(self):
        tpl = "%2s"
        print(nl*5)

        for n, word in enumerate1(self.words):
            print(tpl % n, space, word, nl)
            lnumbers = ujoin(range1(len(word)), space * (word.spacing()-1), tpl)
            print(space*3, lnumbers, nl*2)

        print(self.stattpl % (self.random_reveals, self.guesses), nl)

    def randreveal(self):
        if self.random_reveals:
            rndchoice([w for w in self if w.hidden]).randreveal()
            self.random_reveals -= 1

    def check_end(self):
        if not any(word.hidden for word in self):
            self.display()
            print(self.winmsg % (self.random_reveals*3 + self.guesses))
            sys.exit()
        elif not (self.guesses or self.random_reveals):
            self.display()
            print(self.losemsg)
            sys.exit()

    def guess(self, word, lind, letter):
        if self.guesses:
            if words[word].guess(lind, letter):
                pass
            else:
                self.guesses -= 1


class Test(object):
    def run(self):
        self.textinput = TextInput(("%hd %hd %s", randcmd))

        while True:
            words.display()
            cmd = self.textinput.getinput()

            if first(cmd) == randcmd : words.randreveal()
            else                     : self.reveal_letter( *cmd )
            words.check_end()

    def reveal_letter(self, *cmd):
        try               : words.guess(*cmd)
        except IndexError : print(self.textinput.invalid_move)


if __name__ == "__main__":
    words = Words( open(wordsfn).readlines() )
    Test().run()
