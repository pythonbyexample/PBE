#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division

import sys
import re
from copy import copy
from random import randint

sentinel = object()
space    = ' '
nl       = '\n'


class InvalidCode(Exception):
    def __init__(self, val) : self.val = val
    def __str__(self)       : return repr(self.val)


class Loop(object):
    """ Loop over a list of items in forward / backward direction, keeping track of current item,
        which is available as `item` attribute by default, or under a custom `name` provided to init.
    """
    def __init__(self, items, name="item", index=0):
        self.items   = items
        self.name    = name
        self.length  = len(self.items)
        self.lastind = len(self.items) - 1
        self.index   = 0
        self.next(index)

    def next(self, n=1):
        # len=3, last=2, cur=0, next(7) ; 1201201 7%3: cur+n%len
        if n < 0:
            self.prev(abs(n))
        self.index = (self.index + n) % self.length
        self.update_attr()

    def prev(self, n=1):
        # len=3, last=2, cur=1, prev(5) ; 02102 -4%3: cur+n%len  3 + -1
        print("n", n)
        print("self.length", self.length)
        print( abs((self.index - n) % self.length) )
        self.index = self.length - abs((self.index - n) % self.length)
        print("self.index", self.index)
        # self.index = self.index-1 if self.index > 0 else self.lastind
        self.update_attr()

    def n_items(self, n):
        """Return next `n` items, starting with current item."""
        for _ in range(n):
            yield self.item
            self.next()

    def update_attr(self):
        self.item = self.items[self.index]
        setattr(self, self.name, self.items[self.index])

    def __eq__(self, value):
        return bool(self.item == value)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return repr(self.item)

    def __bool__(self):
        return bool(self.item)

    def __add__(self, other):
        return self.item + other

    def __sub__(self, other):
        return self.item - other

    def __radd__(self, other):
        return self.item + other

    def __rsub__(self, other):
        return other - self.item


class AttrToggles(object):
    """Inverse-toggle two boolean attributes when one of a pair is toggled; `attribute_toggles` is a list of tuples."""
    attribute_toggles = []

    def __setattr__(self, attr, val):
        object.__setattr__(self, attr, val)
        toggles = self.attribute_toggles

        if attr in flatten(toggles):
            for attrs in toggles:
                if attr in attrs:
                    attrs = set(attrs) - set([attr])
                    for attr in attrs:
                        object.__setattr__(self, attr, not val)


class Dice(object):
    """Roll multiple dice."""
    def __init__(self, num=2, sides=6):
        self.num   = num
        self.sides = sides

    def roll(self):
        return [randint(1, self.sides) for _ in range(self.num)]

    def rollsum(self):
        return sum(self.roll())


class TextInput(object):
    """ Get text input from user in a specified format `fmt`.
        Given format "loc %d", both inputs are valid: "332", "3 3 2"; when input is ambiguous, values
        need to be separated by spaces.

        Supported format codes:
            loc - location in X Y format; will be checked using board.valid() method.
            %d  - integer
            %f  - float
            %s  - string

        getloc() - convenience method to get a single location irrespective of `self.fmt`.

        Note: location is accepted in "human format", i.e. it's adjusted from 1-indexed to 0-indexed.
    """
    invalid_inp  = "Invalid input"
    invalid_move = "Invalid move"
    formats      = ("loc",)

    # needs to be in precise order for matchfmt() method
    regexes     = (
                   ("loc?" , "(\d+ \d+)?"),
                   ("%s?"  , "\w*"),
                   ("%d?"  , "\d*"),
                   ("%hd?" , "\d*"),
                   ("%f?"  , "\d*\.?\d*"),  # TODO: this one needs more work..

                   ("loc"  , "\d+ \d+"),
                   ("%s"   , "\w+"),
                   ("%d"   , "\d+"),
                   ("%hd"  , "\d+"),
                   ("%f"   , "\d\.?\d?"),
                   (" "    , " *"),
                    )

    def __init__(self, formats=None, board=None, options=(), prompt="> ", quit_key='q', accept_blank=False, invalid_inp=None,
                 singlechar_cmds=False):
        if isinstance(formats, basestring): formats = [formats]
        self.board           = board
        self.formats         = formats
        self.options         = options
        self.prompt          = prompt
        self.quit_key        = quit_key
        self.accept_blank    = accept_blank
        self.singlechar_cmds = singlechar_cmds
        self.invalid_inp     = invalid_inp or self.invalid_inp

    def getloc(self):
        return first( self.getinput(formats=["loc"]) )

    def getval(self):
        return first(self.getinput())

    def getinput(self, formats=None):
        formats = formats or self.formats

        while True:
            # return self.parse_input(formats)
            try:
                return self.parse_input(formats)
            except (IndexError, ValueError, TypeError, KeyError), e:
                print(self.invalid_inp)

    def matchfmt(self, fmt, inp):
        for init, repl in self.regexes:
            fmt = fmt.replace(init, repl)
        return re.match("^%s$" % fmt, inp)

    def parse_fmt(self, inp, fmt):
        """Attempt to parse `inp` using `fmt` format; return False if there is mismatch."""
        from board import Loc

        fmt      = fmt.split()
        inp      = copy(inp)
        commands = []
        handlers = {"%d": int, "%f": float, "%s": str}
        regexes  = dict(self.regexes)

        def nomatch(val): return bool( optional and not re.match(regex, val) )

        for n, code in enumerate(fmt):
            optional = code.endswith('?')
            if optional: code = code[:-1]
            regex    = "^%s$" % regexes.get(code, code)

            if not inp:
                if optional: continue
                else: raise ValueError

            if code == "loc":

                if nomatch( ujoin(inp[:2]) ):
                    continue
                else:
                    x, y = inp.pop(0), inp.pop(0)
                    loc = Loc( int(x)-1, int(y)-1 )
                    if self.board and not self.board.valid(loc):
                        raise IndexError
                    commands.append(loc)

            elif code == "%hd":     # 'human' format, 1-indexed, integer
                if nomatch(first(inp)) : continue
                else                   : commands.append( int(inp.pop(0)) - 1 )

            else:
                if nomatch(first(inp)) : continue
                else                   : commands.append( handlers.get(code, str)(inp.pop(0)) )

        if inp: raise ValueError
        return commands

    def parse_input(self, formats):
        inp = raw_input(self.prompt).strip()
        if inp == self.quit_key: sys.exit()
        if self.accept_blank and not inp:
            return None

        formats = [fmt for fmt in formats if self.matchfmt(fmt, inp)]
        if not formats:
            raise ValueError

        fmt = first(formats)
        if self.singlechar_cmds:
            inp = inp.replace(space, '')

        inp      = inp.split() if space in inp else list(inp)
        commands = self.parse_fmt(inp, fmt)
        return commands
        # return commands if len(commands)>1 else first(commands)



# ==== Functions =======================================================

def ujoin(iterable, sep=' ', tpl='%s'):
    return sep.join( [tpl % unicode(x) for x in iterable] )

def itersplit(it, check):
    """Split iterator `it` in two lists: first that passes `check` and second that does not."""
    return [x for x in it if check(x)], \
           [x for x in it if not check(x)]

def enumerate1(it):
    """Enumerate iterator `it` using 1-based indexing."""
    return ((n+1, x) for n, x in enumerate(it))

def range1(x):
    return range(1, x+1)

def envelope(value, minval, maxval):
    """Adjust `value` to be within min/max bounds."""
    return min(max(value, minval), maxval)

def flatten(iterable):
    return [item for sublist in iterable for item in sublist]

def human_readable(val):
    return val + 1

def py_readable(val):
    return val - 1

def timefmt(sec):
    return "%d:%02d" % (sec/60, sec%60)

def parse_hnuminput(iterable):
    """Convert a list of 'human input' 1-indexed string values to 0-indexed integers."""
    return [int(val)-1 for val in iterable]

def lastind(iterable):
    return len(iterable) - 1

def nextval(iterable, value):
    """Next value of `iterable` after `value`, wrapping around at the end."""
    i = iterable.index(value)
    i = 0 if i >= lastind(iterable) else i+1
    return iterable[i]

def first(iterable):
    return next(iter(iterable))

def getitem(iterable, index, default=None):
    try               : return iterable[index]
    except IndexError : return default
