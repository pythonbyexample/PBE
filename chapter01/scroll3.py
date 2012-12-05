#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
from random import choice as rndchoice
from time import sleep

from utils import TextInput, Loop, ujoin, enumerate1, range1, first, envelope, space, nl
from utils import iround, sjoin
from board import Loc, StackableBoard, BaseTile

pause_time = 0.3
blank      = '.'
plchar     = '@'
size       = 30, 20
vsize      = 12, 10
num_rocks  = 30
rockchar   = '#'
scrolltype = 1

wrap       = True
viswrap    = True
out        = open("out", 'w')
bufsize    = 3
startloc   = 3, 3


def topitems(iterable):
    return [x[-1] for x in iterable]

def writeln(*args):
    out.write(sjoin(args) + nl)


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
    def __init__(self, size, vsize, def_tile, scrolltype, viswrap=False, bufsize=0):
        super(ScrollBoard, self).__init__(size, def_tile)
        self.vwidth, self.vheight = vsize

        self.scrolltype = scrolltype
        self.viswrap    = viswrap
        self.bufsize    = bufsize
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
        # print("self.vtopleft.y", self.vtopleft.y)
        rows = Loop(self.board, "row", index=self.vtopleft.y)

        for _ in range(self.vheight):
            cols = Loop(rows.row, index=self.vtopleft.x)
            print(space, ujoin( topitems(cols.n_items(self.vwidth)) ))
            rows.next()

        sleep(pause_time)

    def rand_blank(self):
        return rndchoice(self.tiles("blank"))

    def center_on(self, item_loc):
        loc        = self.ploc(item_loc)
        halfwidth  = iround(self.vwidth / 2)
        halfheight = iround(self.vheight / 2)

        if self.viswrap:
            x = Loop(range(self.width), index=loc.x)
            y = Loop(range(self.height), index=loc.y)
            x = x.prev(halfwidth)
            y = y.prev(halfheight)
        else:
            x, y = loc.x - self.halfwidth, loc.y - self.halfheight
            x, y = max(0, x), max(0, y)

        writeln(self.vtopleft, loc)
        self.vtopleft = Loc(x, y)
        writeln(self.vtopleft); writeln()

    def move(self, item, newloc):
        scroll = getattr(self, "scroll%d" % self.scrolltype)
        scroll(item.loc, newloc)
        super(ScrollBoard, self).move(item, newloc)

    def scroll1(self, loc, newloc):
        x, y    = self.vtopleft
        bufsize = self.bufsize

        maxx = x + self.vwidth - bufsize

        if newloc.x < x + bufsize:
            x = max(newloc.x - self.vwidth + bufsize, 0)

        # 30 35, vsize=10
        elif newloc.x >= maxx:
            x = min(newloc.x - bufsize, self.width - self.vwidth)

        if newloc.y < y + bufsize:
            y = max(y - self.vheight + bufsize, 0)

        elif newloc.y >= y + self.vheight:
            y = min(y + self.vheight - bufsize, self.height - self.vheight)

        self.vtopleft = Loc(x, y)
        writeln(maxx, self.vtopleft); writeln()

    def scroll2(self, loc, newloc):
        self.center_on(newloc)


class Test(object):
    def run(self):
        moves   = 'd'*2 + 'r'*18 + 'u'*11 + 'l'*17
        moves   = 'r'*9 + 'l'*8
        moves   = 'r'*30 + 'l'*30

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
    board  = ScrollBoard(size, vsize, Blank, scrolltype, viswrap=viswrap, bufsize=bufsize)
    player = Player(Loc(*startloc))
    # board.center_on(player)
    for _ in range(num_rocks): Rock(board.rand_blank())
    for x in range(size[0]): Rock(Loc(x, 0))
    for y in range(size[1]): Rock(Loc(0, y))

    Test().run()
