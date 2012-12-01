#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import sleep

from utils import TextInput, ujoin, enumerate1, range1, first, envelope, space, nl
from board import Loc, StackableBoard, BaseTile

pause_time = 0.5
blank      = '.'
plchar     = '@'
size       = 30, 20
vsize      = 15, 10
num_rocks  = 30
rockchar   = '#'
scrolltype = 2
wrap       = True


def topitems(iterable):
    return [x[-1] for x in iterable]

class Tile(BaseTile):
    blank = rock = player = False

    def __init__(self, loc):
        super(Tile, self).__init__(loc)
        if loc: board[loc] = self

    def __repr__(self):
        return self.char


class Blank(Tile) : char = blank
class Rock(Tile)  : char = rockchar


class Player(Tile):
    char = plchar

    def move(self, dirname, wrap):
        dirs = dict(u=0, r=1, d=2, l=3)
        dir = board.dirlist[ dirs[dirname] ]
        newloc = board.nextloc(self, dir, wrap=wrap)
        if newloc:
            board.move(self, newloc)


class ScrollBoard(StackableBoard):
    def __init__(self, size, vsize, def_tile, scrolltype, viswrap=False):
        super(ScrollBoard, self).__init__(size, def_tile)
        self.vwidth, self.vheight = vsize

        self.scrolltype = scrolltype
        self.viswrap    = viswrap
        self.vtopleft   = Loc(0,0)
        self.maxv_x     = self.width - self.vwidth
        self.maxv_y     = self.height - self.vheight

    def draw(self):
        if self.viswrap: self.viswrap_draw(); return

        print(nl*5)
        for n, row in enumerate(self.board):
            x, y = self.vtopleft
            if y + self.vheight > n >= y:
                print(space, ujoin( topitems(row[ x : x+self.vwidth ]) ))
        sleep(pause_time)

    def viswrap_draw(self):
        print(nl*5)
        rows = Loop(self.board, "row", index=self.vtopleft.y)

        for _ in range(self.vheight):
            cols = Loop(rows.row, index=self.vtopleft.x)
            print(space, ujoin( topitems(cols.n_items(self.vwidth)) ))
            rows.next()

        sleep(pause_time)

    def rand_blank(self):
        return rndchoice(self.tiles("blank"))

    def center_on(self, item_loc):
        loc           = self.ploc(item_loc)
        halfwidth     = self.vwidth // 2
        halfheight    = self.vheight // 2
        x             = loc.x - halfwidth
        y             = loc.y - halfheight

        if not self.viswrap:
            x, y = max(0, x), max(0, y)
        self.vtopleft = Loc(x, y)

    def move(self, item, newloc):
        scroll = getattr(self, "scroll%d" % self.scrolltype)
        scroll(item.loc, newloc)
        super(ScrollBoard, self).move(item, newloc)

    def scroll1(self, loc, newloc):
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

    def scroll2(self, loc, newloc):
        self.center_on(newloc)


class Test(object):
    def run(self):
        moves   = 'd'*2 + 'r'*18 + 'u'*11 + 'l'*17
        moves   = 'd'*3 + 'u'*10

        for move in moves:
            board.draw()
            player.move(move, wrap)

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
    board  = ScrollBoard(size, vsize, Blank, scrolltype)
    player = Player(Loc(3, 3))
    for _ in range(num_rocks): Rock(board.rand_blank())
    Test().run()
