#!/usr/bin/env python

# Imports {{{
from __future__ import print_function, unicode_literals, division

import os, sys
from random import choice, randint
from string import join, uppercase, letters
from os.path import expanduser, exists

from term import Term

maxx, maxy   = 2, 2
initial_hide = 0.7
start_points = 30
wordsfn      = "words"
datafn       = expanduser("~/.words_data")
# }}}


class Word(object):
    def __init__(self, word):
        self.hidden = []
        self.word   = word.rstrip()
        self.gen_hidden(initial_hide)

    def __len__(self):
        return len(self.word)

    def guess(self, i, l):
        """Reveal all instances of `l` if word[i] == `l` & reveal random letter in one other word."""
        if self.word[i] == l:
            self.reveal_letter(l)
            lst = [w for w in board if len(w.hidden)>1 and w != self]
            if lst:
                choice(lst).revealrnd()
            return True

    def reveal(self, letter):
        """Reveal all letters equal to `letter`."""
        for n, ltr in enumerate(self.word):
            if ltr == letter:
                self.hidden.remove(n)

    def revealrnd(self):
        """Reveal a random letter."""
        self.reveal( self.word[choice(self.hidden)] )

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
        self.hidden = range(length)
        while len(self.hidden) < num_to_hide:
            self.hide( choice(range(length)) )

    def __str__(self):
        return ''join( (hiddenltr if n in self.hidden else l) for n, l in enumerate(self.word) )


class Command(object):
    term = Term()

    movekeys = {
        '[D' : "left",
        '[C' : "right",
        '[B' : "down",
        '[A' : "up",

        'h'  : "left",
        'l'  : "right",
        'j'  : "down",
        'k'  : "up",
    }

    cmds = dict(
        q = "quit",
        r = "random",
        b = "back",
        h = "help",
    )

    def help(self):
        print "move: left/right/down/up   Enter: open word / guess letter\n" \
              "r: reveal random letter   b: back to wordlist   q: quit"

    def quit(self):
        if self.term.getch("quit? [y/n] ") == 'y':
            sys.exit()

    def guess(self):
        """Let player guess current letter."""
        if char.listmode: return
        l = self.term.getch("letter? ")
        if board.current().reveal(char.i, l):
            char.points += 1
        else:
            char.points -= 1

    def random(self):
        if char.points >= 3:
            board.current().revealrnd()
            char.points -= 3

    def open(self):
        """Open current word or guess current letter."""
        if char.listmode:
            char.listmode = False
            char.i = 0
        else:
            self.guess()

    def back(self):
        char.listmode = True

    def blank(self):
        pass

    def uinput(self):
        cmd = self.term.getch('> ')
        if cmd in self.movekeys:
            return char.move(self.movekeys[cmd])
        elif cmd == '\n':
            self.open()
        else:
            getattr(self, self.cmds.get(cmd, "blank"))()


def main():
    while 1:
        board.display() if char.listmode else board.show_word()

        if   board.all_done(): won()
        elif char.points < 0: lost()
        cmd.uinput()

def save_top_score(self):
    data = shelve.open(datafn)
    score = data.get("score", 0)
    if self.points > score:
        print("You have the top score!!\n")
        data["score"] = self.points
    data.close()


if __name__ == "__main__":
    words = open(wordsfn).readlines()
    char  = Char()
    board = Board()
    main()
