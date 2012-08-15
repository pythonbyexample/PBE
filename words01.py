#!/usr/bin/env python

# Imports {{{
import os, sys
from random import choice, randint
from string import join

from term import Term

initial_hide   = 0.7
initial_points = 7
wordsfn        = "words"
# }}}


class Word(object):
    def __init__(self):
        self.i      = 0
        self.points = initial_points
        self.hidden = ''
        self.word   = choice(words).rstrip()
        self.length = len(self.word)
        self.gen_hidden(initial_hide)

    def reveal(self, i, l):
        if self.word[i] == l:
            self.reveal_letter(l)
            return True

    def reveal_letter(self, letter):
        for n, ltr in enumerate(self.word):
            if ltr == letter:
                self.hidden[n] = ltr

    def revealrnd(self):
        """Reveal a random letter."""
        l = [self.word[i] for i,l in enumerate(self.hidden) if l=='_']
        self.reveal_letter(choice(l))

    def gen_hidden(self, hidden):
        """Hide letters according to `hidden` setting, e.g. if 0.7, hide 70%."""
        num = int(round(self.length * hidden))
        self.hidden = list('_'*self.length)

        if num != self.length:
            while 1:
                n = randint(0, self.length-1)
                if self.hidden[n] == '_':
                    self.reveal_letter(self.word[n])
                if self.hidden.count('_') <= num:
                    break

    def done(self):
        return not self.num_hidden()

    def num_hidden(self):
        return self.hidden.count('_')

    def show_hidden(self):
        return "%s\n%s*" % (join(self.hidden), ' '*self.i*2)


class Command(object):
    term = Term()

    movekeys = {
        '[D' : "left",
        '[C' : "right",
    }

    cmds = dict(
        q = "quit",
        r = "random",
    )

    def quit(self):
        if self.term.getch("quit? [y/n] ") == 'y':
            sys.exit()

    def guess(self):
        """Let player guess current letter."""
        l = self.term.getch("letter? ")
        if word.reveal(word.i, l):
            word.points += 1
        else:
            word.points -= 1

    def random(self):
        if word.points >= 3:
            word.revealrnd()
            word.points -= 3

    def blank(self):
        pass

    def move(self, dir):
        i   = word.i
        x   = word.length
        i += 1 if dir=="right" else -1
        if   i < 0: i = x-1
        elif i == x: i = 0
        word.i = i

    def uinput(self):
        cmd = self.term.getch('> ')
        if cmd in self.movekeys:
            self.move(self.movekeys[cmd])
        elif cmd == '\n':
            self.guess()
        else:
            getattr(self, self.cmds.get(cmd, "blank"))()


def won():
    print "You won! score: %s" % word.points
    sys.exit()

def lost():
    print "You lose!"
    sys.exit()

def main():
    cmd = Command()
    while 1:
        os.system("clear")
        print
        print word.show_hidden()

        if   word.done(): won()
        elif word.points < 0: lost()
        cmd.uinput()


if __name__ == "__main__":
    words  = open(wordsfn).readlines()
    word   = Word()
    main()
