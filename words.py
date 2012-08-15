#!/usr/bin/env python

# Imports {{{
import os, sys
from random import choice, randint
from string import join, uppercase, letters
from os.path import expanduser, exists

from term import Term

maxx, maxy   = 2, 2
initial_hide = 0.7
start_points = 30
wordsfn      = "words"
topfn        = expanduser("~/.words_topscore")
# }}}


class Board(object):
    def __init__(self):
        self.board = [ [Word() for _ in range(maxx)] for _ in range(maxy) ]

    def display(self):
        for n, row in enumerate(self.board):
            for m, w in enumerate(row):
                print ' '*5 + '@' if (m, n) == char.loc else w,
            print '\n'

    def show_word(self):
        p = "%5s" % ("[%d]" % char.points)
        print "%s  %s" % (p, self.current().show_hidden())

    def current(self):
        x, y = char.loc
        return self.board[y][x]

    def all_done(self):
        return all(w.done() for w in self)

    def __iter__(self):
        for y in range(maxy):
            for x in range(maxx):
                yield self.board[y][x]


class Char(object):
    i        = 0    # word letter index
    loc      = 0,0
    points   = start_points
    listmode = True

    def move(self, dir):
        if self.listmode:
            x, y = self.loc
            if   dir == "right" : x += 1
            elif dir == "down"  : y += 1
            elif dir == "left"  : x -= 1
            elif dir == "up"    : y -= 1
            if 0 <= x < maxx and 0 <= y < maxy:
                self.loc = x, y

        else:
            i = self.i
            x = board.current().length
            i += 1 if dir=="right" else -1
            if   i < 0: i = x-1
            elif i == x: i = 0
            self.i = i

    def save_top_score(self):
        s = 0
        if exists(topfn):
            with open(topfn) as fp:
                try: s = int(fp.read().strip())
                except: pass
        if self.points > s:
            print "You have the top score!!\n"
            with open(topfn, 'w') as fp:
                fp.write(str(self.points))


class Word(object):
    def __init__(self):
        self.i      = 0
        self.hidden = ''
        self.word   = choice(words).rstrip()
        self.length = len(self.word)
        self.gen_hidden(initial_hide)

    def reveal(self, i, l):
        """Reveal all instances of `l` if word[i] == `l` & reveal random letter in one other word."""
        if self.word[i] == l:
            self.reveal_letter(l)

            lst = [w for w in board if w.num_hidden()>1 and w != board.current()]
            if lst:
                choice(lst).revealrnd()
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
        """Hide letters according to `hidden`, e.g. if 0.7, hide 70%."""
        num = int(round(self.length * hidden))
        self.hidden = list('_'*self.length)

        if num != self.length:
            while 1:
                n = randint(0, self.length-1)
                if self.hidden[n] == '_':
                    self.reveal_letter(self.word[n])
                if self.hidden.count('_') <= num:
                    break

    def __str__(self):
        s = "%d/%d" % (self.hidden.count('_'), self.length)
        return "%6s" % s

    def done(self):
        return not self.num_hidden()

    def num_hidden(self):
        return self.hidden.count('_')

    def show_hidden(self):
        return "%s\n%s%s*" % (join(self.hidden), ' '*7, ' '*char.i*2)


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


def won():
    print "You won! score: %s" % char.points
    char.save_top_score()
    print "Words:"
    for w in board: print '\t' + w.word
    sys.exit()

def lost():
    print "You lose!"
    sys.exit()

def main():
    cmd = Command()
    while 1:
        os.system("clear")
        cmd.help()
        print
        board.display() if char.listmode else board.show_word()

        if   board.all_done(): won()
        elif char.points < 0: lost()
        cmd.uinput()

def ascii(word):
    for l in word.lower():
        if l not in letters: return False
    return True

def filter_words(words):
    words = [w for w in words if ascii(w)]
    with open('words2', 'w') as fp:
        for w in words: fp.write(w+'\n')


if __name__ == "__main__":
    words = open(wordsfn).readlines()
    char  = Char()
    board = Board()
    main()
