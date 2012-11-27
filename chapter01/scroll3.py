#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import sleep

from utils import TextInput, ujoin, enumerate1, range1, first, envelope, space, nl
from board import Loc, Board, StackableBoard

pause_time = 0.5
blank      = '.'
size       = 15, 15
vsize      = 5, 5
rockchar   = '#'


class ScrollBoard(StackableBoard):
    def __init__(self, size, vsize, def_tile):
        super(ScrollBoard, self).__init__(size, def_tile)
        self.vwidth, self.vheight = vsize
        self.vtopleft = Loc(0,0)

    def draw(self):
        print(nl*5)
        for n, row in enumerate(self.board):
            x, y = self.vtopleft
            if y + self.vheight > n >= y:
                print( ujoin( [t[-1] for t in row[ x : x+self.vwidth ]] ) )
        print(player.loc)
        sleep(pause_time)

    def rand_blank(self):
        return rndchoice([ l for l in self.locations() if self[l]==blank ])

    def move(self, item, newloc):
        super(ScrollBoard, self).move(item, newloc)
        x, y = self.vtopleft

        if newloc.x < x:
            x = max(x - self.vwidth, 0)

        elif newloc.x >= x + self.vwidth:
            x = min(x + self.vwidth, self.width - self.vwidth)

        if newloc.y < y:
            y = max(y - self.vheight, 0)

        elif newloc.y >= y + self.vheight:
            y = min(y + self.vheight, self.height - self.vheight)

        self.vtopleft = Loc(x, y)


class Player(object):
    char = '@'

    def __init__(self, loc):
        self.loc = loc
        board[loc] = self

    def __repr__(self):
        return self.char

    def move(self, dirname):
        dirs = dict(u=0, r=1, d=2, l=3)
        dir = board.dirlist[ dirs[dirname] ]
        newloc = board.nextloc(self.loc, dir)
        if newloc:
            board.move(self, newloc)


class Test(object):
    def run(self):
        moves   = 'd'*7 + 'r'*7
        moves   = 'd'*8 + 'r'*8 + 'u'*7 + 'l'*6

        for move in moves:
            board.draw()
            player.move(move)

        return

        ####
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
    board  = ScrollBoard(size, vsize, blank)
    player = Player(Loc(0, 0))
    for _ in range(30):
        board[board.rand_blank()] = rockchar
    Test().run()
