#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
import re
from copy import copy
from random import randint, shuffle
from itertools import zip_longest, takewhile

sentinel = object()
space    = ' '
nl       = '\n'


class InvalidCode(Exception):
    def __init__(self, val) : self.val = val
    def __str__(self)       : return repr(self.val)


class Loop(object):
    """ Loop over a sequence of items in forward / backward direction, keeping track of current item,
        which is available as `item` attribute by default, and under a custom `name` provided to init.
    """
    def __init__(self, items, name="item", index=0):
        self.items   = list(items)
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
        return self.item

    def prev(self, n=1):
        # len=3, last=2, cur=1, prev(5) ; 02102 -4%3: cur+n%len  3 + -1
        # print("n", n)
        # print("self.length", self.length)
        # print( abs((self.index - n) % self.length) )
        self.index = abs((self.index - n) % self.length)
        # self.index = self.length - abs((self.index - n) % self.length)
        # print("self.index", self.index)
        # self.index = self.index-1 if self.index > 0 else self.lastind
        self.update_attr()
        return self.item

    def n_items(self, n):
        """Return next `n` items, starting with current item."""
        for _ in range(n):
            yield self.item
            self.next()

    def update_attr(self):
        self.item = self.items[self.index]
        setattr(self, self.name, self.items[self.index])

    def __str__(self):
        return str(self.item)

    def __getitem__(self, i):
        return self.items[i]

    def __setitem__(self, i, val):
        self.items[i] = val

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
    """ Inverse-toggle two boolean attributes when one of a pair is toggled; `attribute_toggles`
        is a list of tuples.
    """
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
    invalid_inp    = "Invalid input"
    invalid_move   = "Invalid move"
    formats        = ("loc",)
    choice_tpl     = "%2d) %s"
    explicit_split = True       # input contained spaces & it was possible to explicitly split values

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

    def __init__(self, formats=None, board=None, prompt="> ", quit_key='q', accept_blank=False,
                 invalid_inp=None, singlechar_cmds=False):
        try              : is_str = isinstance(formats, basestring)
        except NameError : is_str = isinstance(formats, str)

        if is_str: formats = [formats]

        self.board           = board
        self.formats         = formats
        self.prompt          = prompt
        self.quit_key        = quit_key
        self.accept_blank    = accept_blank
        self.singlechar_cmds = singlechar_cmds
        self.invalid_inp     = invalid_inp or self.invalid_inp

    def getloc(self):
        return first( self.getinput(formats=["loc"]) )

    def yesno(self, default=None):
        self.accept_blank = bool(default)

        assert default in ('y', 'n', None)
        if   default == 'y' : p = "[Y/n] "
        elif default == 'n' : p = "[y/N] "
        else                : p = "[y/n] "

        inp = self.getinput( formats=["(y|Y|n|N)"] )
        inp = first(inp) if inp else default

        return bool(inp.lower() == 'y')

    def getval(self):
        return first(self.getinput())

    def getinput(self, formats=None):
        formats = formats or self.formats

        while True:
            # return self.parse_input(formats)
            try: return self.parse_input(formats)
            except (IndexError, ValueError, TypeError, KeyError) as e: print(self.invalid_inp)

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
        isdigit  = lambda x: x.isdigit()

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
                    # print("inp", inp)
                    x, y = inp.pop(0), inp.pop(0)
                    loc = Loc( int(x)-1, int(y)-1 )
                    if self.board and not self.board.valid(loc):
                        raise IndexError
                    commands.append(loc)

            # int and 'human format' (1-indexed) int
            elif code in ("%d", "%hd"):
                if nomatch(first(inp)):
                    continue
                else:
                    if self.explicit_split:
                        n = inp.pop(0)
                    else:
                        n = list(takewhile(isdigit, iter(inp)))
                        n = sjoin(n, '')
                        inp = inp[len(n):]
                    n = int(n) if code=="%d" else int(n)-1
                    commands.append(n)

            else:
                if nomatch(first(inp)) :
                    continue
                else:
                    if self.explicit_split:
                        val = inp.pop(0)
                    else:
                        val = []

                        def match(x):
                            pat = sjoin(val, sep='') + x
                            if re.match(regex, pat):
                                val.append(x)
                                return True

                        val = list(takewhile(match, iter(inp)))
                        val = sjoin(val, '')
                        inp = inp[len(val):]

                    commands.append( handlers.get(code, str)(val) )

        if inp: raise ValueError
        return commands

    def parse_input(self, formats):
        inp = input(self.prompt).strip()
        if inp == self.quit_key: sys.exit()
        if self.accept_blank and not inp:
            return None

        formats = [fmt for fmt in formats if self.matchfmt(fmt, inp)]
        if not formats:
            raise ValueError

        fmt = first(formats)
        if self.singlechar_cmds:
            inp = inp.replace(space, '')

        if space in inp:
            inp = inp.split()
        else:
            inp = list(inp)
            self.explicit_split = False

        commands = self.parse_fmt(inp, fmt)
        return commands

    def menu(self, choices):
        for n, (title, _) in enumerate1(choices):
            print(self.choice_tpl % (n, title))

        fmt          = "(%s)" % sjoin( range1(len(choices)), '|' )
        self.formats = [fmt]
        i            = int(self.getval()) - 1
        return choices[i][1]


class Container:
    def __init__(self, **kwargs)   : self.__dict__.update(kwargs)
    def __setitem__(self, k, v)    : self.__dict__[k] = v
    def __delitem__(self, k)       : del self.__dict__[k]
    def __getitem__(self, k)       : return self.__dict__[k]
    def __iter__(self)             : return iter(self.__dict__)
    def __nonzero__(self)          : return bool(self.__dict__)
    def __bool__(self)             : return bool(self.__dict__)
    def pop(self, *args, **kwargs) : return self.__dict__.pop(*args, **kwargs)
    def get(self, *args, **kwargs) : return self.__dict__.get(*args, **kwargs)
    def update(self, arg)          : return self.__dict__.update(arg)
    def items(self)                : return self.__dict__.items()
    def keys(self)                 : return self.__dict__.keys()
    def values(self)               : return self.__dict__.values()


class BufferedIterator(object):
    """Iterator with 'buffered' takewhile and takeuntil."""

    def __init__(self, seq):
        self.seq        = iter(seq)
        self.end_marker = object()
        self.buffer     = []
        self.last       = None

    def __bool__(self):
        return self.last is not self.end_marker

    def __next__(self):
        self.last = self.buffer.pop() if self.buffer else next(self.seq, self.end_marker)
        return self.last

    def consume(self, n):
        for _ in range(n): next(self)

    def takewhile(self, test):
        lst = []
        while True:
            val = next(self)

            if val is self.end_marker:
                return lst
            elif test(val):
                lst.append(val)
            else:
                self.buffer.append(val)
                return lst

    def takeuntil(self, test):
        """Return items BEFORE the item for which `test` passes."""
        return self.takewhile(lambda x: not test(x))

    def joined_takewhile(self, test):
        return ''.join(self.takewhile(test))

    def joined_takeuntil(self, test):
        return ''.join(self.takeuntil(test))


# ==== Functions =======================================================

def ujoin(iterable, sep=' ', tpl='%s'):
    """Deprecated."""
    return sep.join( [tpl % str(x) for x in iterable] )

def sjoin(iterable, sep=' ', tpl='%s'):
    """Cast each item to a string using `tpl` template, then join into a single string."""
    return sep.join( [tpl % str(x) for x in iterable] )

def itersplit(it, check):
    """Split iterator `it` in two lists: first that passes `check` and second that does not."""
    return [x for x in it if check(x)], \
           [x for x in it if not check(x)]

def enumerate1(it):
    """Enumerate iterator `it` using 1-based indexing."""
    return ((n+1, x) for n, x in enumerate(it))

def range1(x):
    """1-index based range."""
    return range(1, x+1)

def envelope(value, minval, maxval):
    """Adjust `value` to be within min/max bounds."""
    return min(max(value, minval), maxval)

def flatten(iterable):
    """One-level flattening."""
    return [item for sublist in iterable for item in sublist]

def timefmt(sec):
    """Format time to min:sec format."""
    return "%d:%02d" % (sec/60, sec%60)

def lastind(iterable):
    """Last (highest) valid index of `iterable`; also accepts length as an int."""
    if isinstance(iterable, int):
        return iterable - 1
    return len(iterable) - 1

def nextval(iterable, value):
    """Next value of `iterable` after `value`, wrapping around at the end; useful to toggle values."""
    i = iterable.index(value)
    i = 0 if i >= lastind(iterable) else i+1
    return iterable[i]

def first(iterable, default=None):
    try:
        return next(iter(iterable))
    except StopIteration:
        return default

def last(seq, default=None):
    try:
        return seq[-1]
    except IndexError:
        return default

def getitem(iterable, index, default=None):
    """Get item from an `iterable` at `index`, return default if index out of range."""
    try               : return iterable[index]
    except IndexError : return default

def nextgroup(groupy_iterator, default=None):
    group = nextitem(groupy_iterator)
    if group:
        return Container(key=group[0], group=list(group[1]))
    else:
        return default


def nextitem(iterable, default=None):
    try:
        return next(iterable)
    except StopIteration:
        return default

def topitems(iterable):
    """ Last (top) items from a list of lists, useful to get 'top' items from a list of stacks e.g.
        from a list of locations on a stackable game board.
    """
    return [x[-1] for x in iterable]

def iround(value):
    return int(round(value))

def cmp(val1, val2):
    if val1 == val2 : return 0
    else            : return 1 if val1 > val2 else -1

def grouper(n, iterable, fillvalue=None):
    """From itertools recipes: collect data into fixed-length chunks or blocks."""
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

def shuffled(lst):
    shuffle(lst)
    return lst

def progress_bar(value, total, size=78, char='∘', border='||'):
    inside = size - 2
    tpl    = "%s%%-%ds%s" % (border[0], inside, border[1])
    return tpl % (char * iround(inside * value/total))

def multi_replace(text, tuples):
    for s1, s2 in tuples:
        text = text.replace(s1, s2)
    return text

def getter(fn, is_at_end=lambda v: not v):
  while True:
    val = fn()
    if is_at_end(val): break
    yield val
