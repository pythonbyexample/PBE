#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice

from utils import TextInput, ujoin, enumerate1, range1, first, space, nl


num_words      = 5
hidden_char    = '_'
lettertpl      = "%2s"
initial_hide   = 0.7                # how much of the word to hide, 0.7 = 70%
randcmd        = 'r'                # reveal random letter; must be one char
limit9         = True               # only use 9-or-less letter words
random_reveals = num_words // 2     # allow player to reveal x random letters

wordsfn        = "words"


guesses_divby  = 3      # calc allowed wrong guesses by dividing total # of letters by this number


class Word(object):
    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def __str__(self):
        word = ( (hidden_char if n in self.hidden else l) for n, l in enumerate(self.word) )
        return ujoin(word, space * self.spacing(), lettertpl)

    def __len__(self)    : return len(self.word)
    def spacing(self)    : return 2 if len(self) > 9 else 1
    def randreveal(self) : self.reveal( self.word[rndchoice(self.hidden)] )

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
    losemsg = "You've run out of guesses.."
    stattpl = "random reveals: %d | attempts: %d"

    def __init__(self, wordlist):
        self.random_reveals = random_reveals
        self.words          = set()

        while len(self.words) < num_words:
            word = Word( rndchoice(wordlist).rstrip() )
            if limit9 and len(word)>9:
                continue
            self.words.add(word)

        self.words   = list(self.words)
        self.guesses = sum(len(w) for w in self.words) // guesses_divby

    def __getitem__(self, i) : return self.words[i]
    def __iter__(self)       : return iter(self.words)

    def display(self):
        print(nl*5)

        for n, word in enumerate1(self.words):
            print(lettertpl % n, space, word, nl)
            lnumbers = ujoin(range1(len(word)), space * word.spacing(), lettertpl)
            print(space*4, lnumbers, nl*2)

        print(self.stattpl % (self.random_reveals, self.guesses), nl)

    def randreveal(self):
        if self.random_reveals:
            rndchoice( [w for w in self if w.hidden] ).randreveal()
            self.random_reveals -= 1

    def guess(self, word, lind, letter):
        if self.guesses and not self[word].guess(lind, letter):
            self.guesses -= 1

    def check_end(self):
        if not any(word.hidden for word in self):
            self.game_end(True)
        elif not (self.guesses or self.random_reveals):
            self.game_end(False)

    def game_end(self, won):
        self.display()
        msg = self.winmsg % (self.random_reveals*3 + self.guesses) if won else self.losemsg
        print(msg)
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

    def reveal_letter(self, *cmd):
        try               : words.guess(*cmd)
        except IndexError : print(self.textinput.invalid_inp)


if __name__ == "__main__":
    words = Words( open(wordsfn).readlines() )
    Test().run()
