
import re, sys
from vim import *
from os.path import expanduser

sys.path.append(expanduser("~/.vim/python/"))
import util
from util import *
reload(util) # if there is an error in a module, it's not auto-reloaded after the error is fixed

def vim_comments():
    """Align vim comments after mappings: |" foo => |"    foo."""
    rng = exist_eval("a:2")
    l1, l2 = ieval("a:line1")-1, ieval("a:line2")-1
    buf = current.buffer
    lines = [re.split(r'\|', l) for l in buf[l1:l2+1]]
    lines = [(join(l[:-1], ''), l[-1]) for l in lines]
    maxl = max([len(l[0]) for l in lines])
    for n, l in enumerate(lines):
        lstr = l[1].strip()
        if not lstr or lstr.startswith('"'):
            # blank or comment line
            buf[l1+n] = l[1]
        else:
            buf[l1+n] = l[0] + '|' + ' '*(maxl-len(l[0])+4) + '" ' + l[1].strip().lstrip('" ')

def fixindent(up=False):
    """ Fix indent of lines below current; if `up` is true, above current until indent changes.

        The logic works in the following way:
            - go in given direction, looking for the first line with different indent
            - once line is found, remember its indent as 'indent to change'
            - when we get to line with indent that does not match either, stop
            - blank lines are skipped, but 2 blanks in a row mean stop

        NOTE: does not work with tabs because I don't use them.
    """
    buf        = current.buffer
    ln         = blnum()
    ind        = int(indent(ln+1))
    step       = -1 if up else 1
    change_ind = None      # indent of lines we'll be changing
    empty      = 0         # number of empty lines seen in a row

    while 1:
        ln += step
        if ln < 0 or ln+1 >= len(buf) or empty >= 2:
            break

        l = buf[ln]
        if not l.strip():
            empty += 1
            continue
        empty = 0

        ind2 = int(indent(ln+1))
        if ind2 != ind:
            if change_ind == None:
                change_ind = ind2
            elif ind2 != change_ind:
                break
            buf[ln] = ' '*ind + buf[ln].lstrip()

        if ind2 == ind and change_ind != None:
            break


def aligncode():
    """ Align equal signs or comments in code.

        Search for lines ahead and back from current line, processing all contiguous lines that
        have align character. If `char` is not given, try to guess based on current line,
        preferring '#'.
    """
    # set up variables
    char = exist_eval("a:1")
    ln = orignum = lnum()
    b, l = current.buffer, current.line
    chars = [' # ', ': ', ' = ']
    ind = indent()

    # figure out align char
    if char:
        alchar = ' %s ' % char
    else:
        for c in chars:
            if c in l:
                alchar = c
                break
        else:
            return
    maxskip = 10 if alchar==' # ' else 2
    lnums = []
    maxl = 0

    # search ahead and back for lines to process
    for step in (1, -1):
        skipped = 0
        while 1:
            # don't jump over more than 2 lines
            if skipped >= maxskip:
                break
            try: l = b[ln]
            except: break
            lstrp = l.strip()

            if lstrp and indent(ln+1) != ind:
                break
            elif lstrp.startswith("if ") and alchar != ": ":
                break
            elif lstrp.startswith("for "):
                break

            comment = l.strip().startswith('#')
            if not comment and alchar in l:
                lnums.append(ln)
                tmp = len( l.split(alchar, 1)[0].rstrip() )
                if tmp > maxl: maxl = tmp
                skipped = 0
            elif comment or not l:
                skipped += 1
            else:
                break
            ln += step
        ln = orignum - 1

    # give more padding to comments and 1-char padding to ':'
    if alchar == ' # ':
        maxl += 4
    elif alchar == ': ':
        maxl += 1

    for ln in lnums:
        l = b[ln].split(alchar, 1)
        tpl = "%%-%ds%%s%%s" % maxl
        b[ln] = tpl % (l[0].rstrip(), alchar, l[1].lstrip())


if __name__ == "__main__":
    globals()[eval("a:function")]()
#!/usr/bin/env python
"""Miscellaneous small utility functions.

    vol(vol=None) - Get or set volume using aumix.

    progress(ratio, length=40, col=1, cols=("yellow", None, "cyan"),
            nocol="=.")
        Text mode progress bar.

    yes(question, [default answer])
        i.e. if yes("erase file?", 'n'): erase_file()

    color(text, fg, [bg])
        Colorize text using terminal color codes.

    beep(times) - Beep terminal bell number of times.

    ftime(seconds) - returns h:m:s or m:s if there's no hours.

    Term() - terminal stuff
        term.size() => height, width
        term.clear() => clear terminal
        term.getch() => get one char at a time

Andrei Kulakov <ak@silmarill.org>
"""

import os
import commands
import time
from string import join
try:
    from termios import *
except ImportError:
    from TERMIOS import *
from types import *
from sys import stdin, stdout

dbg = 1
enable_color = 0
hotkeycol = "red"

colors = dict([c.split() for c in (     # make dict {"red": "31", ...}
  "black 30, red 31, green 32, brown 33, blue 34, purple 35, cyan 36, lgray 37, gray 1;30, "
  "lred 1;31, lgreen 1;32, yellow 1;33, lblue 1;34, pink 1;35, lcyan 1;36, white 1;37"
).split(', ')])


class AvkError(Exception):
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)

def debug(*msgs):
    if dbg:
        for m in msgs: print '###  ', m

def replace(val, lst):
    """ Replace patterns within `val`."""
    for pat, repl in lst:
        val = val.replace(pat, repl)
    return val

def split(fname):
    """ Split filename into (name, extension) tuple."""
    lst = fname.split('.')
    if len(lst) == 1: return fname, None
    else: return join(lst[:-1], '.'), lst[-1]

def vol(vol=None):
    """ Set or show audio volume.

        Uses external mixer called aumix. One optional argument, vol, may
        be an int or a string. If a string, it can be of the form "+10".
    """
    if vol: os.system("aumix -v%s" % vol)
    else: return commands.getoutput("aumix -vq").split()[1][:-1]

def progress(ratio, length=40, col=1, cols=("yellow", None, "cyan"), nocol="=."):
    """ Text mode progress bar.

        ratio   - current position / total (e.g. 0.6 is 60%)
        length  - bar size
        col     - color bar
        cols    - tuple: (elapsed, left, percentage num)
        nocol   - string, if default="=.", bar is [=======.....]
    """
    if ratio > 1: ratio = 1
    elchar, leftchar = nocol
    elapsed = int(round(ratio*length))
    left = length - elapsed
    bar = (elchar*elapsed + leftchar*left)[:length]

    if col: return color(' '*elapsed, "gray", cols[0]) + color(' '*left, "gray", cols[1])
    else: return elchar*elapsed + leftchar*left

def yes(question, default=None):
    """ Get an answer for the question.

        Return 1 on 'yes' and 0 on 'no'; default may be set to 'y' or 'n';
        asks "Question? [Y/n]" (default is capitalized). Yy and Nn are
        acceptable. Question is asked until a valid answer is given.
    """
    y, n = "yn"
    if default:
        if default in "Yy": y = 'Y'
        elif default in "Nn": n = 'N'
        else:
            raise AvkError("Error: default must be 'y' or 'n'.")

    while 1:
        answer = raw_input("%s [%s/%s] " % (question, y, n))
        if default and not answer:
            return (1 if default in "Yy" else 0)
        else:
            if not answer: continue
            elif answer in "Yy": return 1
            elif answer in "Nn": return 0

def no(question, default=None):
    return not yes(question, default)

def color(text, fg, bg=None, raw=0):
    """ Return colored text.

        Uses terminal color codes; set avk_util.enable_color to 0 to return plain un-colored text.
        If fg is a tuple, it's assumed to be (fg, bg). Both colors may be 'None'.

        Raw means return string in raw form - for writing to a file instead of printing to screen.
        Leave default if not sure.
    """
    # init vars
    xterm, bgcode = 0, ''
    if not enable_color or not fg:
        return text
    if type(fg) in (TupleType, ListType):
        fg, bg = fg
    opencol, closecol = "\033[", "m"
    if raw:
        opencol, closecol = r"\[\033[", r"m\]"
    clear = opencol + '0' + closecol
    if os.environ["TERM"] == "xterm":
        xterm = 1

    # create color codes
    if xterm and fg == "yellow":    # In xterm, brown comes out as yellow..
        fg = "brown"
    fgcode = opencol + colors[fg] + closecol
    if bg:
        if bg == "yellow" and xterm: bg = "brown"

        try: bgcode = opencol + colors[bg].replace('3', '4', 1) + closecol
        except KeyError: pass
    return "%s%s%s%s" % (bgcode, fgcode, text, clear)

def beep(times, interval=1):
    """Beep terminal bell specified times with `interval` seconds (float or int)."""
    for t in range(times):
        print '\a'
        time.sleep(interval)

def ftime(seconds, suffixes=['y','w','d','','',''], separator=':', nosec=False):
    """ Takes an amount of seconds and turns it into a human-readable amount of time.
        ftime(953995) => 1w:04d:00:59:55
        if `nosec` is True, seconds will be omitted from output.
        adapted from code by: http://snipplr.com/users/wbowers/
    """
    t = []
    parts = [ (suffixes[0], 60 * 60 * 24 * 7 * 52),
              (suffixes[1], 60 * 60 * 24 * 7),
              (suffixes[2], 60 * 60 * 24),
              (suffixes[3], 60 * 60),
              (suffixes[4], 60),
              (suffixes[5], 1)]

    # for each time piece, grab the value and remaining seconds, and add it to the time string
    if nosec:
        del parts[-1]
    for n, (suffix, length) in enumerate(parts):
        value = int(seconds) / length
        if value > 0 or t:                      # skip parts until we get first non-zero
            seconds = seconds % length
            fmt = "%02d%s"
            if not t and n+1 < len(parts):
                fmt = "%d%s"              # don't pad the first part with zeroes
            t.append(fmt % (value, suffix))
    if not t: t = ['0s']
    elif len(t) == 1 and not nosec: t[0] += 's'
    return join(t, separator)

# print ftime(105, nosec=True)

class Term:
    """ Linux terminal management.

        clear   - calls os.system("clear")
        getch   - get one char at a time
        size    - return height, width of the terminal
    """
    def __init__(self):
        self.fd = stdin.fileno()
        self.new_term, self.old_term = tcgetattr(self.fd), tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~ICANON & ~ECHO)

    def normal(self):
        """Set 'normal' terminal settings."""
        tcsetattr(self.fd, TCSAFLUSH, self.old_term)

    def clear(self):
        """Clear screen."""
        os.system("clear")

    def cline(self):
        """Clear line."""
        stdout.write('\r' + ' '*self.size()[1])
        stdout.flush()

    def curses(self):
        """Set 'curses' terminal settings. (noecho, something else?)"""
        tcsetattr(self.fd, TCSAFLUSH, self.new_term)

    def getch(self, prompt=None):
        """ Get one character at a time.

            NOTE: if the user suspends (^Z) running program, then brings it back to foreground,
            you have to instantiate Term class again.  Otherwise getch() won't work. Even after
            that, the user has to hit 'enter' once before he can enter commands.
        """
        if prompt:
            stdout.write(prompt)
            stdout.flush()
        self.curses()
        c = os.read(self.fd, 1)
        self.normal()
        return c

    def size(self):
        """Return terminal size as tuple (height, width)."""
        import struct, fcntl
        h, w = struct.unpack("hhhh", fcntl.ioctl(0, TIOCGWINSZ, "\000"*8))[0:2]
        if not h:
            h, w = 24, 80
        return h, w

import os
import sqlite3
import shutil
import re
from time import *
from os.path import expanduser, exists
from string import join
from copy import deepcopy
from vim import *

leftmargin = 1


class Sort:
    """ Sort todo item list. By default, sorting is by priority, to sort by a different header,
        cursor should be positioned on the header and sort command activated.
    """
    def cmp1(self, a, b):
        """Compare two items, used by sort, can compare numbers, alphanumeric or dates."""
        a, b = a[self.index], b[self.index]
        if self.index == 1:
            try:
                a = strptime(a, "%b %d %Y")
                b = strptime(b, "%b %d %Y")
            except:
                pass
        elif self.index == 3:
            if a.startswith("www."): a = a[4:]
            if b.startswith("www."): b = b[4:]
        elif self.sort_tag:
            a, b = a.split(), b.split()
            t = self.sort_tag

            if (t in a and t in b) or (t not in a and t not in b): return 0
            elif t in a and not t in b: return -1
            else: return 1

        # return cmp(len(a), len(b))    # sort by size - useful for trimming titles
        return cmp(a, b)

    def sort(self):
        b = current.buffer
        self.sort_tag = None
        tags = []
        last_tagline_num = 0
        for n, l in enumerate(b):
            if l.startswith("------"):
                break
            elif l.strip():
                last_tagline_num = n
                if l.startswith("Tags: "): tags.extend(l.split()[1:])
                else: tags.extend(l.split())

        tags = [t.strip("[]") for t in tags]

        # find out what to sort by
        headers = tuple(eval("s:headers").split())
        self.index = 1                        # header to sort by
        cword = eval("expand('<cword>')")     # word under cursor
        pos = current.window.cursor
        if cword in headers:
            self.index = headers.index(cword)
        elif cword in tags:
            self.sort_tag = cword
            self.index = 2

        # parse the bookmark list
        bmarks = []
        maxl1 = 4; maxl2 = 7

        div_count = 0
        body_ind = 0
        newtags = []
        for n, l in enumerate(b):
            l = l.strip()
            if l:
                if l.startswith("------"):
                    if div_count == 0: body_ind = n
                    div_count += 1
                elif div_count >= 2:
                    flds = [fld.strip() for fld in re.split("\s\s+", l)]

                    if len(flds) == 3: flds.insert(2, '')

                    curtags = flds[2].split()
                    for t in curtags:
                        if t not in tags + newtags:
                            newtags.append(t)

                    if len(flds) != 4:
                        print "Error: wrong number of fields in line: %s" % l
                        return

                    if len(flds[0]) > maxl1: maxl1 = len(flds[0])
                    if len(flds[2]) > maxl2: maxl2 = len(flds[2])
                    bmarks.append(flds)

        if newtags:
            newtags = ["[%s]" % t for t in newtags]
            l = b[last_tagline_num]
            b[last_tagline_num] = l + ' ' + join(newtags)
            current.window.cursor = (last_tagline_num+1, 0)
            blen = len(b)
            command("normal gqq")
            body_ind += len(b) - blen   # to avoid overwriting new tag lines later

        maxl1 += 3; maxl2 += 2

        # sort in asc order; if was sorted, sort in desc order
        was_sorted = True
        original = deepcopy(bmarks)
        bmarks.sort(cmp=self.cmp1)
        if bmarks == original: bmarks.sort(cmp=self.cmp1, reverse=True)

        # make line template, insert headers, tasks, OnHold and Done
        divlen = maxl1 + maxl2 + 40 + leftmargin     # divider line
        del b[body_ind:]
        fldtpl = ' '* leftmargin + "%%-%ds%%-14s%%-%ds" % (maxl1, maxl2) + "%s"
        div = '-'*divlen
        b[body_ind:0] = [div, '', fldtpl % headers, div] + [fldtpl % tuple(bm) for bm in bmarks]

        # save line template to use when adding new tasks (to keep alignment)
        let("fldtpl", fldtpl)
        let("tag_col", maxl1 + 14)
        current.window.cursor = pos     # restore cursor

def update():
    """Update bookmarks from firefox places DB."""
    b = current.buffer
    dbfn = expanduser(eval("s:firefox_places"))
    tmpfn = expanduser("~/.vim/python/places.sqlite")
    shutil.copy(dbfn, tmpfn)    # because firefox locks the file ?!!
    conn = sqlite3.connect(tmpfn)
    c = conn.cursor()
    c.execute("SELECT mb.dateAdded, mp.url, mp.title FROM moz_bookmarks AS mb, moz_places AS mp WHERE"
              " mb.fk = mp.id")
    lst = []
    bmarks = []
    for row in c:
        if not row[1].startswith("place:"):
            bmarks.append((localtime(int(row[0])/1000000), row[1], re.sub("\s+", ' ', row[2])))

    div_count = 0
    urls = []
    for l in b:
        l = l.strip()
        if l:
            if l.startswith("------"):
                div_count += 1
            elif div_count >= 2:
                flds = [fld.strip() for fld in re.split("\s\s+", l)]
                if len(flds) == 3:
                    flds.insert(2, '')
                urls.append(flds[3])

    init = False
    if len(b) <= 1:
        lst = ["Tags: ", '-'*78, '', "Name  Added  Tags  Url", '-'*78]
        b[0:0] = lst
        init = True

    addlst = ['']
    fldtpl = exist_eval("s:fldtpl")
    if not fldtpl: fldtpl = "%s    %s    %s    %s"

    del_list = eval("s:del_list")
    del_urls = [u.rstrip() for u in open(expanduser(del_list)).readlines()]
    skipped = 0

    maxt = 0
    tmp = []
    for added, url, name in bmarks:
        url = url.replace("http://", '')
        if url not in urls:
            if url in del_urls:
                skipped += 1
                continue
            if not name: name = "[no title]"
            if len(name) > maxt: maxt = len(name)
            tmp.append((name, added, url))

    maxt += 4
    fldtpl = fldtpl.split("s%")
    if len(fldtpl) == 1:
        fldtpl = "%%-%ds" % maxt + "%s    %s    %s"
    else:
        fldtpl = "%%-%ds%%" % maxt + join(fldtpl[1:], "s%")

    print "fldtpl: ", fldtpl

    for name, added, url in tmp:
        l = fldtpl % (name, strftime("%b %d %Y", added), '', url)
        addlst.append(str(l.encode("utf-8")))

    b[len(b):len(b)] = addlst
    if init: Sort().sort()
    if len(addlst) > 1: print "Added %s new bookmarks." % (len(addlst) - 1),
    if skipped: print "%d url(s) in the del_list skipped." % skipped

def sort_or_open():
    """If on a bookmark, open in browser, if on header, sort by it; if on a tag, sort by tag."""
    b = current.buffer
    div_count = 0
    lnum = current.window.cursor[0] - 1

    for n, l in enumerate(b):
        if div_count >= 2:
            if lnum >= n:
                num_open = 1
                val = exist_eval("a:2")
                if val:
                    num_open = int(val)
                for x in range(num_open):
                    flds = [fld.strip() for fld in re.split("\s\s+", b[lnum+x])]
                    if len(flds) == 3: flds.insert(2, '')

                    if len(flds) == 4:
                        for url in flds[3].split():
                            os.system("%s %s" % (eval("s:browser"), url))

            else: Sort().sort()
            break
        elif l.startswith("------"):
            div_count += 1

def new():
    """Add a new bookmark."""
    b = current.buffer
    lnum = current.window.cursor[0] - 1

    div_count = 0
    for n, l in enumerate(b):
        if div_count >= 2:
            if lnum < n: lnum = n
            break
        elif l.startswith("------"):
            div_count += 1

    # default line template or reuse one from sort(), to keep alignment
    fldtpl = exist_eval("s:fldtpl")
    if not fldtpl: fldtpl = "%s  %s  %s  %s"

    # insert new bookmark with default values
    added = strftime("%b %d %Y", localtime())
    b[lnum:lnum] = [fldtpl % ("Name", added, '', '_')]
    current.window.cursor = (lnum+1, 0)
    command("normal $r ")

def open_bkmarks():
    """Open bkmarks window."""
    sb = int(eval("&splitbelow"))
    command("set splitbelow")
    for b in buffers:
        if b.name and b.name.endswith(".bmrk"):
            bnr = eval("bufnr('%s')" % b.name)
            if int(eval("buflisted(%s)" % bnr)):
                command("split %s" % b.name)
                command('exe "normal 7\\<c-w>_"' % n)
                command("normal gg")
                break
    if not sb:
        command("set nosplitbelow")

def change_name():
    """Change name of bookmark."""
    i = current.line.index("  ")
    current.line = ' '*i + current.line[i:]
    command("normal 0l")

def sort_date():
    """Sort by date and go to first bookmark."""
    Sort().sort()
    current.window.cursor = (1,0)
    search("^---"); search("^---")
    command("normal j")


##### Utility functions

def delete():
    """Delete a bookmark and add its url to deleted file."""
    flds = [fld.strip() for fld in re.split("\s\s+", current.line)]

    if len(flds) == 3: url = flds[2]
    elif len(flds) == 4: url = flds[3]
    else:
        command("d")
        return

    del_list = expanduser(eval("s:del_list"))
    if os.path.exists(del_list): open(del_list, 'a').write(url + '\n')
    else: open(del_list, 'w').write(url + '\n')
    command("d")

def iexists(var):
    return int(eval("exists('%s')" % var))

def exist_eval(var):
    if iexists(var): return eval(var)
    else: return None

def let(var, val):
    command('let s:%s = "%s"' % (var, str(val)))

if __name__ == "__main__":
    cmd = exist_eval("a:1")
    if cmd:
        if   cmd == "update": update()
        elif cmd == "new": new()
        elif cmd == "toggle_onhold": toggle_onhold()
        elif cmd == "show_active": show_active()
        elif cmd == "change_name": change_name()
        elif cmd == "sort_or_open": sort_or_open()
        elif cmd == "delete": delete()
        elif cmd == "sort_date": sort_date()
#!/usr/bin/env python

"VimTobu"

from sqlalchemy import *
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base
import os
os.environ["DJANGO_SETTINGS"] = "dbsettings"
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return self.title


def main():
    engine = create_engine("sqlite:///:memory:", echo=True)
# vim: set fileencoding=utf-8 :
"""Draw text boxes."""

import sys
from os.path import dirname, split, splitext, exists, expanduser, join as pjoin
from string import join
from vim import *

sys.path.append(dirname(__name__))
from genpydoc import GenPyDoc

"""

+------+
| test |
| test |    x
| test |    x
+------+



"""

class Box:
    def line_replace(self, lnum, start_lst, txt):
        """Replace part of line b[lnum] with provided `txt`, starting at list of locations `start`."""
        start_lst = [x-1 for x in start_lst]
        line = list(' '*self.shift + self.b[lnum])
        length = len(txt)
        end_lst = [s+length for s in start_lst]

        for start, end in zip(start_lst, end_lst):
            ll = len(line)
            if ll < end:
                line.extend([' ']*(end-ll))
            line = line[:start] + list(txt) + line[end:]
        self.b[lnum] = join(line, '')

    def remove(self):
        """ Erase surrounding box.

            The box must not be adjacent to other boxes, specifically corner '+' must not be
            adjacent to any "-+|" chars.
        """
        lnum, col = current.window.cursor
        lnum -= 1
        b = current.buffer
        while 1:
            c = b[lnum][col]
            if c in "-+|":
                setchar(b, lnum, col, ' ')
                lc = self.find_border(b, lnum, col, c)
                if not lc: break
                else: lnum, col = lc

    def find_border(self, b, lnum, col, c):
        """Find location of border next to given location."""
        hlocs = [(lnum, col+1), (lnum, col-1)]
        vlocs = [(lnum+1, col), (lnum-1, col)]
        if   c == '-' : locs = hlocs
        elif c == '|' : locs = vlocs
        else          : locs = hlocs + vlocs

        for lnum, col in locs:
            try:
                if b[lnum][col] in "-+|":
                    return lnum, col
            except IndexError:
                pass

    def draw(self, padding=0):
        """ Draw box around visual selection. `padding`: 0 or 1.
        """
        self.shift = 0
        lnum = current.window.cursor[0]
        scol = int(eval('virtcol("\'<")'))
        ecol = int(eval('virtcol("\'>")'))

        if scol > ecol:
            scol, ecol = ecol, scol
        if scol < 3+padding:
            self.shift = 3+padding-scol
            scol += self.shift
            ecol += self.shift

        sline = int(eval('getpos("\'<")')[1])
        eline = int(eval('getpos("\'>")')[1])
        self.b, l = current.buffer, current.line
        length = ecol - scol + 4 + padding*2
        start = scol-2-padding

        # top and bottom
        self.line_replace(sline-2-padding, [start], "+%s+" % ('-'*(length-1)))
        self.line_replace(eline+0+padding, [start], "+%s+" % ('-'*(length-1)))

        # sides
        for x in range(sline, eline+1):
            self.line_replace(x-1, [start, start+length], '|')
        if padding:
            self.line_replace(sline-2, [start, start+length], '|')
            self.line_replace(eline, [start, start+length], '|')

class Line:
    def start(self):
        """Start line."""
        cmd = input()
        first = second = dist = None
        if not cmd:
            return
        elif len(cmd) == 1:
            first = cmd
        else:
            first, second, cmd = cmd[-2], cmd[-1], cmd[:-2]
            if cmd:
                dist = int(cmd)

        b = current.buffer
        command("set ve=all")
        dirpairs = dict(j='k', h='l', k='j', l='h')

        if   first == 'j': char, arrow = '|', '↓'
        elif first == 'k': char, arrow = '|', '↑'
        elif first == 'h': char, arrow = '|', '←'
        elif first == 'l': char, arrow = '|', '→'

        for x in range(99):
            command("normal " + first)
            lnum, col = getloc()
            if getchar(b, lnum, col) == ' ':
                setchar(b, lnum, col, char)
            else:
                command("normal " + dirpairs[first])
                lnum, col = getloc()
                setchar(b, lnum, col, arrow)
                break


def input(prompt="> "):
    return eval("input('%s ')" % prompt)

def getloc():
    lnum, col = current.window.cursor
    lnum -= 1
    print "col: ", col
    return lnum, col

def getchar(b, lnum, col):
    lnum, col = current.window.cursor
    lnum -= 1
    try: return b[lnum][col]
    except IndexError: return ' '

def setchar(b, lnum, col, char):
    l = list(b[lnum])
    ll = len(l)
    if col > ll:
        l += [' ']*(col-ll+1)
    print "l: ", l
    l[col] = char
    b[lnum] = join(l, '')

def iexists(var):
    return int(eval("exists('%s')" % var))

def exist_eval(var):
    if iexists(var): return eval(var)
    else: return None

if __name__ == '__main__':
    arg = exist_eval("a:1")
    if   arg == '2'          : Box().remove()
    elif arg == '1'          : Box().draw(int(arg))
    elif arg == '0'          : Box().draw(int(arg))
    elif arg == "line-start" : Line().start()
    elif arg == "line-stop"  : Line().stop()
    elif arg == "line-down"  : Line().down()
    elif arg == "line-up"    : Line().up()
    elif arg == "line-right" : Line().right()
    elif arg == "line-left"  : Line().left()

import re
from time import *
from datetime import *
from calendar import *
from vim import *

sys.path.append(expanduser("~/.vim/python/"))
import util
from util import *
reload(util) # if there is an error in a module, it's not auto-reloaded after the error is fixed

width = ieval("g:py_cal_width")


def mkmonth(t):
    """Make and return a list of lines for given month. `t` is a timetuple object."""
    wd = width - 2
    lst = monthcalendar(t[0], t[1])
    out = ["====== " + strftime("%B %Y", t)]    # e.g. June 2010

    # make line template
    daywidth = int(round(wd / 7)) - 2

    linetpl = ("%%-%ds| " % daywidth)*7
    linetpl = linetpl.rstrip()
    divtpl = ("%%-%ds|-" % daywidth)*6 + "%%-%ds|" % daywidth

    # add header
    header = "Mo Tu We Th Fr Sa Su".split()
    header = ' '*3 + linetpl % tuple(header)
    wd = len(header) - 1
    out.extend([ header.replace('|', ' ').rstrip(),  ' ' + '-'*wd ])

    # add weeks
    for n, week in enumerate(lst):
        w = linetpl % tuple(week)
        # monthcalendar() returns 0s for non-existing days; replace with spaces
        out.append(" | " + re.sub("^0  | 0 |  0$", ' '*3, w))
        l = " | " + linetpl % tuple(' '*7)
        ll = " |-" + divtpl % tuple( ['-'*daywidth]*7 )
        if n+1 == len(lst):
            ll = ' ' + '-'*wd
        out.extend([l, ll])    # blank lines for notes

    out.append('')

    return out

def add_month():
    """Add new month to the calender."""
    buf = current.buffer
    init = False

    # make timetuple of next (or initial) month
    if len(buf) == 1:
        # init empty file
        ttup = localtime()
        init = True
    else:
        normal("gg")
        search("======-")
        ln = lnum()
        search("====== ", 'b')
        l = current.line.strip("= ")
        t = strptime(l, "%B %Y")
        d = date(t[0], t[1], t[2]) + timedelta(31)
        ttup = d.timetuple()

    out = mkmonth(ttup)
    if init:
        # 2-line separater of month views and day entries
        sepline = '='*(width-1) + '-'
        out.extend([sepline, sepline])

    buf.append(out, ln-1)
    buf.append([out[0], ''])

    command("set nolist")
    cursor(ln, 0)

def entry():
    """Jump to or make new entry."""
    # find day number by tracing the bounding box.
    pos = cursor()
    s = search('|', 'b')
    if not s: return

    normal("2lk")
    for x in range(20):
        if getc() == '-':
            break
        normal("k")

    if getc() != '-':
        cursor(pos)
        return
    normal("j")
    if getc() == '[': normal("2l")

    day = eval("expand('<cWORD>')").rstrip(']')
    new = True

    if day.endswith('*'):
        new = False
        day = day[:-1]

    if not re.match("^\d{1,2}$", day):
        cursor(pos)
        return

    if new: normal("geelr*")    # add star - cmd: ge  e  l  r*

    # find what month we're at
    search("^====== ", 'b')
    l = current.line.strip("= ")
    t = strptime(l, "%B %Y")
    target_d = date(t[0], t[1], int(day)).timetuple()

    # find needed day's entry or the last one before it if making new
    search("^====== " + l)
    for x in range(int(day), 1, -1):
        d = date(t[0], t[1], x).timetuple()
        s = search("^=== " + strftime("%a %B %d, %Y", d))
        if s: break


    # add new entry
    if new:
        s = search(r"^=== \|^====== ", 'W')
        if not s:
            normal("G2o")
        # format e.g.: === Fri June 11, 2010
        current.buffer.append( ["=== " + strftime("%a %B %d, %Y", target_d), ''] , lnum())
        cursor(lnum()+2, 0)
    else:
        normal("j")

def today():
    """Mark today and clear mark from previous highlight."""
    t = date.today()
    month = strftime("%B %Y", t.timetuple())
    normal("gg")

    # remove old hl
    # need to match: "| [ 12 ]" OR "| [ 12*]"
    # pseudo-pattern: | [ \d{1,2} *{1,2} [ ]{1,2}]
    s = search("| \[ \d\{1,2}\*\{0,1}[ ]\{0,1}\]")
    if s:
        normal("2lxxf]r a  ")  # cmd: 2l xx f] r<space> a<space><space>
        normal("gg")

    # add new hl
    search(month)
    day = t.timetuple()[2]
    for x in range(8):
        search('-'*14)
        normal('j')
        s = search(r"| %s\*\{0,1} " % str(day))
        if s: break

    # some plugin (autoclose?) does not allow closing [] with R cmd

    mv = 5 if day > 10 else 4

    normal("2li  ")             # cmd: 2l i<space><space>
    normal("hr[%dlr]lxxb" % mv)     # cmd: h r[ 5l r] l xx b

def back():
    """Back to current day in month view (from entries section)."""
    if not current.line.startswith("==="):
        search("^===", 'b')

    try:
        ttup = strptime(current.line.strip("= "), "%a %B %d, %Y")
    except ValueError:
        print "This command when you're in daily entry"
        return
    search("^====== %s" % strftime("%B %Y", ttup), 'b')
    search("^====== %s" % strftime("%B %Y", ttup), 'b')

    day = ttup[2]

    for x in range(8):      # 8 not to stuck in a loop but cover 5 possible weeks
        search('-'*14)
        normal('j')
        s = search(r"| \(\[ \)\?%s\*\?" % str(day))
        if s: break
    search('\d')


if __name__ == "__main__":
    val = exist_eval("a:1")
    if val:
        if   val == "back": back()
        elif val == "today": today()
        elif val == "entry": entry()
        elif val == "add_month": add_month()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'vimtobu.db',            # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',
        'PORT': '',
    }
}

DATABASE_ENGINE   = 'sqlite3'
DATABASE_NAME     = 'vimtobu.db'
DATABASE_HOST     = ''
DATABASE_USER     = ''
DATABASE_PASSWORD = ''
#!/usr/bin/env python2.7
# Imports {{{
"""delete buffers filter

Written by AK <ak@lightbird.net>
"""

from __future__ import print_function, unicode_literals, division
import sys
from string import join
from os.path import expanduser, join as pjoin
from time import sleep
flush = sys.stdout.flush
vimpython_dir = expanduser("~/.vim/python/")

from avkutil import Term

from django.conf import settings
try:
    settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,
                       DATABASE_ENGINE="django.db.backends.sqlite3",
                       DATABASE_NAME=pjoin(vimpython_dir, "vimtobu.db"),
                       INSTALLED_APPS=["vimtobu"])
except RuntimeError:
    pass

from vimtobu.models import *

sep = '='*78
choicefn = pjoin(vimpython_dir, ".delbufs_choice.tmp")
# }}}

class DelBufsFilter:
    def __init__(self, filelst):
        lst = [fn.split(' ', 1) for fn in filelst.split(';')]
        self.filenames = {n: tup for n, tup in enumerate(lst)}
        self.picked = set()

    def main(self, filelst):
        """Main function."""
        self.t = Term()
        while 1: self.ui()

    def process_key(self, c):
        """Process command key."""
        self.matched = ''

        # Enter
        if c == '\n':
            self.write_choices()
            sys.exit()

        # Esc
        elif c == '\x1b':
            self.write_choices(True)
            sys.exit()

    def write_choices(self, cancel=False):
        with open(choicefn, 'w') as fp:
            fp.write("cancel" if cancel else str(self.picked))
        sys.exit()

    def do_input(self):
        while 1:
            prompt = ">" if self.ftype else "tags:"
            prompt = "\r%s %s" % (prompt, self.pat)

            # when BS key is pressed, we need to first overwrite the old character with a space,
            # then write just the prompt again to have cursor in the right place.
            print '\r> ',
            flush()
            self.process_key(self.t.getch())

            if self.ftype:
                # not search, last viewed/edited/created
                try:
                    pat = self.pat.strip()
                    i = int(pat)
                    if (i > 10 or i and (len(self.mdict) < i*10)) and self.mdict and (pat in self.mdict):
                        self.write_choice(self.mdict[pat])
                except ValueError:
                    pass
            elif len(self.pat) >= min_pattern:
                break

    def make_menu(self):
        menu = []
        for n, (bn,fn) in self.filenames:
            sel = '+' if bn in self.picked else ' '
            menu.append( ["%s %2s)  %s" % (sel, n, fn) ])
        return menu

    def ui(self):
        """UI."""
        print '\r' + join(self.make_menu(), '\n')

        self.matched = ''
        self.get_min_pat()

        # make a listing of matches and print it
        if self.pat:
            words = self.pat.split()
            tags = []
            i = None

            # parse num selection, parse tags and filter matches
            if words[-1].isdigit():
                i, words = int(words[-1]), words[:-1]
            for w in words:
                try: tags.append(Tag.objects.get(name=w))
                except Tag.DoesNotExist: pass
            if tags:
                matches = Item.objects.filter(tags__in=tags)

            if matches:
                n = matches.count()
                size = "  ----%s matches----" % n if n>menu_size else ''
                matches = matches[:max_matches]
                for n, m in enumerate(matches):
                    self.mdict[n+1] = m.pk

                if (i > 10 or i and (len(matches) < i*10)) and self.mdict and (i in self.mdict):
                    # e.g. #3 out of 8 items or #4 out of 35 items
                    self.write_choice(self.mdict[i])
                elif len(matches) == 1:
                    self.write_choice(matches[0].pk)
                self.i = i
                print "\r%s\n%s\n" % ( join(self.make_menu(matches), '\n'), size)
            else:
                print "\r\n----no matches found----"

# __main__: {{{
if __name__ == "__main__":
    parser = OptionParser()
    (options, args) = parser.parse_args()
    tf = VTobuFilter()
    arg = None
    if args:
        arg = args[0]
    if arg and arg not in "viewed created edited":
        print "arg should be: viewed or created or edited"
        sys.exit()
    try: tf.main(arg)
    except KeyboardInterrupt: sys.exit()
    except Exception, e:
        print e
        sleep(1.5)
        sys.exit()
# }}}
"""Add new entry."""

from vim import *
from string import join
from time import asctime

def finnew():
    b = current.buffer

    # try get line template from fin_update()
    fldtpl = "%-10s"*(ncols) + "%-15s%s"
    if int(eval("exists('s:fin_fldtpl')")):
        fldtpl = eval("s:fin_fldtpl")

    # find end of entries to insert new one
    headers = re.split("\s\s+", b[0])
    ncols = len(headers) - 2
    command("normal G")
    command("call search('-----', 'b')")
    lnum = current.window.cursor[0]
    while 1:
        lnum -= 1
        if b[lnum].strip():
            current.window.cursor = (lnum, 0)
            break

    # insert blank entry
    t = asctime().split()[:3]
    cols = [0] * ncols + [join(t), ' ']
    lnum -= 1
    b[lnum:lnum] = [fldtpl % tuple(cols)]
    # command("normal $")

finnew()
from time import asctime
from string import join
from os.path import expanduser
import re

from vim import *

sys.path.append(expanduser("~/.vim/python/"))
import util
from util import *
reload(util) # if there is an error in a module, it's not auto-reloaded after the error is fixed


def fin_update():
    """Update totals for all columns."""
    buf = current.buffer
    headers = re.split("\s\s+", buf[0])
    headers = [h.strip() for h in headers if h.strip()]
    ncols = len(headers) - 2
    maxlen = [len(h)+6 for h in headers[:-2] if h.strip()]

    initline = re.split("\s\s+", buf[2])  # initial balance
    initline = [i.strip() for i in initline if i.strip()]
    totals = [float(x) for x in initline[:ncols] if x.strip()]

    # loop through lines and add up totals
    lines = []
    for l in buf[3:]:
        if l.startswith("-----"):
            break
        elif l.startswith('#'):
            lines.append(l)
        elif l.strip():
            flds = [fld.strip() for fld in re.split("\s\s+", l) if fld.strip()]
            if len(flds) not in (ncols+2, ncols+1):
                print "Error: wrong number of fields in line: %s" % l
                return
            newflds = [0]*ncols
            for n, x in enumerate(flds[:ncols]):
                totals[n] += float(x)
                x = "%0.2f" % float(x)
                x = x.rstrip('0').rstrip('.')   # can't do both at the same time!!
                newflds[n] = x or '0'
            lines.append(newflds + flds[-2:])
        else:
            lines.append('')

    # make line template
    fldtpl = amtline_tpl = ''
    for x in maxlen:
        fldtpl += "%%%ds" % x
        amtline_tpl += "%%%ds" % x

    fldtpl += "    %-15s%s"
    amtline_tpl += "    %-15s%s"

    # make list of header, divider and rest of lines
    lst = ([fldtpl % tuple(headers)] +
           ['-'*divlen()] +
           [fldtpl % tuple(initline)])
    for l in lines:
        if isinstance(l, list):
            l = amtline_tpl % tuple(l)
        lst.append(l)

    # make totals line and insert into buffer
    totals = amtline_tpl % tuple(totals + ['', ''])
    buf[:] = lst + ['-'*divlen(), totals.rstrip()]
    normal(r"Gzb10")
    let("s:fin_fldtpl", fldtpl)

def divlen():
    return current.window.width - 3 - ieval("&foldcolumn")    # 2 for sign column

def finnew():
    """Add new entry."""
    # find end of entries to insert new one
    buf = current.buffer
    headers = re.split("\s\s+", buf[0])
    headers = [h.strip() for h in headers if h.strip()]
    ncols = len(headers) - 2

    fldtpl = exist_eval("s:fin_fldtpl") or "%10s"*(ncols) + "   %-15s%s"
    normal("G$")
    search("-----", 'b')
    up()
    normal('0')
    search('.', 'b')

    # insert blank entry
    t = asctime().split()[:3]
    cols = [0]*ncols + [join(t), ' ']
    buf.append(fldtpl % tuple(cols), lnum())
    normal('j')

def fin_init():
    """Initialize fin file."""
    # get headers and initial line
    b = current.buffer
    lst = []
    for l in b:
        if l.strip():
            lst.append(l)
        if len(lst) == 2:
            break

    headers = re.split("\s\s+", lst[0])
    ncols = len(headers)
    maxlen = [len(h)+4 for h in headers]
    headers += ["date", "desc"]
    initline = re.split("\s\s+", lst[1])

    # make line template
    fldtpl = ''
    for x in maxlen:
        fldtpl += "%%%ds" % x
    fldtpl += "    %-15s%s"

    # make list of header, divider and rest of lines
    t = asctime().split()[:3]
    initline += [join(t), "initial"]
    b[:] = ([fldtpl % tuple(headers)] +
            ['-'*divlen()] +
            [fldtpl % tuple(initline)] +
            ['', '-'*divlen()])
    let("s:fin_fldtpl", fldtpl)


if __name__ == "__main__":
    val = exist_eval("a:1")
    if val:
        if   val == "init"   : fin_init()
        elif val == "new"    : finnew()
        elif val == "update" : fin_update()
# vim: set fileencoding=utf-8 :
"""Vimject - GenPyDoc - generate python documentation."""

import re
from string import join
from os import sep
from os.path import split, expanduser
from inspect import *

from vim import *

# Init vars {{{
browser = "chromium-browser"
outfn = "%s-out.html"
htmltpl = """<html><head><title>%s</title>
    <style type="text/css">
        a { text-decoration: none; }
        h4 { color: #679; background: #f5f5f5; padding: 7px; border-top: 1px solid #ccc; }
        p { color: #666; display: inline; }
        h3 { text-align: center; color: #679; }
        .def { color: #366; }
        .cls { color: #a55; }
        .class { color: #a55; }
        .function { color: #484; }
        .args { color: #b53; }
        .docstring { color: #359; }
        .top { float: right; font-size: small; }

        #def { color: #76a; margin-bottom: 3px; }
        #main {
            width: 960px; border: 1px solid #aaa; margin: 30px; padding: 15px; color: #aaa;
            background: #eeeeee;
            }
        #cen { text-align: center; }
    </style>
    </head>
    <body> <h3>%s</h3>
    <div id="main">%s</div></body></html>
"""

# verbose regex, spaces ignored
docstring_pat = '\s*    (""".*?""").*    |\s*   (".*?").*    ' \
                "|\s*   ('''.*?''').*    |\s*   ('.*?').*    "
tab = ' '*4
nbsp = "&nbsp;"
nbsp_tab = nbsp*4
# }}}


def strip_blanks(line):
    return line if line.strip() else ''

def strip_leading(txt):
    leading = len(txt) - len(txt.lstrip())
    return leading, txt.lstrip()

class GenPyDoc:
    html = potl = False
    docstrings = True

    def make_list(self, use_inspect, fn):
        """Make a list of class / def names."""
        # strip out comments
        src = open(expanduser(fn))
        src = src.read().replace('\r\n', '\n')
        lines = src.split('\n')
        lines = [l for l in lines if not l.strip().startswith('#')]
        src = join(lines, '\n')

        # split the list
        if use_inspect:
            cls_def_pat = r"\n\s*(class|def) ([a-zA-Z0-9_]+)(:|\()"
            lst = re.findall(cls_def_pat, src)
            lst = [x[1] for x in lst]
        else:
            cls_def_pat = r"\n(\s*(?:class|def) [a-zA-Z0-9_]+(?:\(|:).*)"
            lst = re.split(cls_def_pat, src)[1:]
            newlst = []
            while 1:
                try:
                    newlst.append((lst.pop(0), lst.pop(0)))
                except IndexError:
                    break
            lst = newlst
        return src, lst

    def module_doc(self, use_inspect, m, src, out):
        """ Output module doc.

            use_inspect: use inspect module to get the doc
            m: module obj
            src: source to use if use_inspect=False
            out: output list
        """
        mdoc = None
        if use_inspect:
            mdoc = getdoc(m)
            if mdoc: mdoc = mdoc.split('\n')
        else:
            lines = [l for l in src.split('\n') if l.strip()]
            if lines[0].startswith("#!/"):
                del lines[0]
            src = join(lines, '\n')

            m = re.match(docstring_pat, src, re.DOTALL | re.VERBOSE)
            if m:
                mdoc = [x for x in m.groups() if x][0]
                mdoc = mdoc.split('\n')

                # leading and trailing newlines will be recreated later
                if not mdoc[0]:  del mdoc[0]
                if not mdoc[-1]: del mdoc[-1]

        if mdoc:
            if self.html:
                if len(mdoc) == 1:
                    out.extend(["<p>%s</p>" % mdoc[0]] +
                               ["<br /><br />"] )
                else:
                    out.extend(["<br/><p>"] +
                               [join(mdoc, "<br/>")] +
                               ["</p><br/>", "<br/><br/>"])
            elif self.potl:
                if len(mdoc) == 1:
                    out.extend([tab+'%s' % mdoc[0]] + [''])
                else:
                    out.extend([tab + ln for ln in mdoc] + [''])
            else:
                if len(mdoc) == 1:
                    out.extend(['"""%s"""' % mdoc[0]] + [''])
                else:
                    out.extend(['"""'] + mdoc + ['"""', ''])

    def make_idoc(self, item, use_inspect, m, src):
        """Extract item doc."""
        idoc = None
        if use_inspect:
            if hasattr(m, item):
                item = getattr(m, item)
                self.last = item
            else:
                item = getattr(self.last, item)

            cls_def = getsourcelines(item)[0][0]
            idoc = getdoc(item)
        else:
            cls_def, src = item
            cls_def = cls_def.replace('\n', '')
            m = re.match(docstring_pat, src, re.DOTALL | re.VERBOSE)

            if m:
                idoc = [x for x in m.groups() if x][0]

        cls_def = cls_def.rstrip(': ')
        indent = cls_def.index(cls_def.lstrip())
        if self.html: indentsp = nbsp*indent
        else:         indentsp = ' '*(indent+4)
        return cls_def, idoc, indent, indentsp

    def process_item(self, item, use_inspect, m, src, out):
        """ Process each def or class item.

            use_inspect: use inspect module to get the doc
            m: module obj
            src: source to use if use_inspect=False
            out: output list
        """
        cls_def, idoc, indent, indentsp = self.make_idoc(item, use_inspect, m, src)

        # does not support multiline defs but they are bad style?
        if self.html:
            indentsp = nbsp*(indent+4)*2
            leading, cls_def = strip_leading(cls_def)
            leading = nbsp*leading
            cls_def, name = cls_def.split(' ', 1)
            cls_def = "<span class='%s'>%s</span>" % (cls_def, cls_def)
            if '(' in name:
                name = re.split(r"[()]", name)
                name = "<span class='function'>%s</span>(<span class='args'>%s</span>)" % (name[0], name[1])
            else:
                name = "<span class='function'>%s</span>" % name
            out.append("<div id='def'>%s%s %s</div>" % (indentsp, cls_def, name))
        elif self.potl:
            if cls_def.startswith(' '):
                cls_def = re.split(r"(\s+)", cls_def)
                cls_def = cls_def[1] + '· ' + join(cls_def[2:], '')
            else:
                cls_def = '· ' + cls_def
            out.append(tab + cls_def)
        else:
            out.append(cls_def)

        # output docstring with indentation
        if idoc and self.docstrings:
            idoc = idoc.split('\n')
            if self.html:
                if len(idoc) == 1:
                    out.append("%s%s<p class='docstring'>%s</p><br />" % (nbsp_tab, indentsp, idoc[0]))
                else:
                    idoc = [l.replace(tab, '', 1) for l in idoc]
                    idoc = [l.replace(' ', nbsp) for l in idoc]
                    idoc = [indentsp + l + "<br />" for l in idoc]
                    idoc[0] = nbsp_tab + idoc[0]
                    out.extend(["<p class='docstring'>%s</p><br />" % join(idoc)])
            else:
                if self.potl:
                    ind_no_tab = indentsp
                    indentsp += tab
                if len(idoc) == 1:
                    out.append('%s%s' % (indentsp, idoc[0]))
                else:
                    # In potl files, since first line's indent is stripped out, we need to first remove
                    # indent that will be added, from all lines, (minus one normal level of indent
                    # that all lines in potl mode have), then add needed indent.
                    if self.potl:
                        idoc = [l.replace(ind_no_tab, '', 1) for l in idoc]
                    idoc = [strip_blanks(indentsp + l) for l in idoc]
                    out.extend(idoc)

        if self.html:
            out.append("<br />")
        elif not self.potl:
            out.append('')

    def process_fn(self, fn, out):
        """Generate documentation for filename `fn`; `out` is the list of output lines."""
        # import module
        path = expanduser(fn).split(sep)
        path, fname = join(path[:-1], sep), path[-1]
        sys.path.append(path)
        use_inspect = True
        try:
            m = None
            # m = __import__(fname.split('.')[0])
            # reload(m)   # if file was changed, it's not autoreloaded even if function is rerun
            # memb = getmembers(m)
        except:
            use_inspect = False

        # don't use inspect, for consistency and because parsing seems to work ok
        use_inspect = False

        src, lst = self.make_list(use_inspect, fn)

        # filename and docstring
        if self.html:
            header = "<a name='%s' /><h4>%s" \
                     "<a href='#top' class='top'>&#x2191; &#x2191;</a></h4>"
            out.extend([header % (fname, fname)] + [''])
        elif self.potl:
            out.extend(['', '· '+fn])
        else:
            out.extend(['#'*78, '# '+fn, ''])

        self.module_doc(use_inspect, m, src, out)

        # output each class and def and their docstrings
        self.last = None
        for item in lst:
            self.process_item(item, use_inspect, m, src, out)

        if not self.html: out.extend(['', ''])

    def genpydoc(self, filelist, mode="txt", docstrings=True):
        """ Generate docs file for all python files in a project or dir, depending on where cursor is.

            mode: txt | potl | html
            docstrings: if False, skip function's docstrings
        """
        self.docstrings = docstrings
        if   mode == "html": self.html = True
        elif mode == "potl": self.potl = True
        filelist = [f for f in filelist if f.endswith(".py")]

        # get project or dir name
        pname = "Project"
        l = current.line
        if l.strip():
            if l.startswith("---"):
                pname = l.strip("- ").capitalize()
            else:
                l = l.strip(' '+sep)
                pname = l.split(sep)[-1].capitalize()

        out = []
        if self.html:
            fns = [split(fn)[-1] for fn in filelist]

            # write HTML without docstrings
            self.docstrings = False
            out.append("<p><a name='top' /><a href='%s'>%s</a></p><br />" %
                       (outfn%(pname+"-docs"), "with docstrings"))
            out.append(join(["<a href='#%s'>%s</a>" % (fn, fn) for fn in fns], ' | '))
            for fn in filelist:
                self.process_fn(fn, out)
            with open(outfn % pname, 'w') as fp:
                fp.write(htmltpl % (pname, pname, join(out, '\n')))

            # write HTML with docstrings
            self.docstrings = True
            out = []
            out.append("<p><a name='top' /><a href='%s'>%s</a></p><br />" %
                       (outfn % pname, "without docstrings"))
            out.append(join(["<a href='#%s'>%s</a>" % (fn, fn) for fn in fns], ' | '))
            for fn in filelist:
                self.process_fn(fn, out)
            with open(outfn % (pname+"-docs"), 'w') as fp:
                fp.write(htmltpl % (pname, pname, join(out, '\n')))

            os.system("%s %s" % (browser, outfn % pname))
            return

        for fn in filelist:
            self.process_fn(fn, out)

        if not out: return

        # go to main window area, create new buffer, write output, set filetype
        command("call NextWin()")
        command("new")
        current.buffer[:] = out
        command("normal gg")
        if self.potl:
            command("set ft=potl bt=nofile")
            command("hi Normal guifg=#999999")
        else:
            command("set filetype=python buftype=nofile")

# vim: set fileencoding=utf-8 :
""" Graph - insert a visual graph of numbers on current line. """

# Imports {{{
import sys
from os.path import expanduser
from string import join
from vim import *

sys.path.append(expanduser("~/.vim/python/"))
import util
from util import *
# if there is an error in a module, it's not auto-reloaded after the error is fixed..
reload(util)


weeks   = True if ',' in current.line else False
days    = not weeks
compact = days
# note: we need these to be unicode to pad them to proper length and then encode to str
bchar   = u'▮'
wchar   = u'▮'
barunit = bchar if compact else bchar*4
tpl     = "%1s" if compact else "%5s"
gheight = 10 if compact else 12
lst     = []
# }}}


class Graph:
    def create(self):
        """ Append to current buffer a graph of numbers in current line.

            Usage: visually select lines to process and use visual mode mapping.

            Although numbers can represent anything, right now the code is adapted for each number
            to be either number of hours per day or per week.

            per day: optionally, last number can start with a colon, it will be interpreted as
                weekday number, '1' being monday.

            per week: detected by presence of commas; commas and semicolons will be stripped,
                first word and last two words will be skipped.
        """

        # parse input numbers
        normal("']")    # last line of visual selection
        l = eval('@"')
        l = l.replace(',', '').replace(';', '')
        numbers = l.split()[1:-2] if weeks else l.split()
        start_weekday, end_weekday = 1, 0

        # calculate start weekday
        if ':' in l:
            numbers, end_weekday = numbers[:-1], int(numbers[-1][1:])
            daysnum = len(numbers) - end_weekday   # omit last week
            start_weekday = 8 - daysnum%7
        numbers = [float(n) for n in numbers]

        # append column lists to buffer
        cols = self.make_colums(numbers, start_weekday)
        temp = []
        for x in reversed(range(gheight)):
            line = []
            for col in cols:
                y = (tpl % col[x]).encode("utf-8")
                line.append(y)
            lst.append(join(line, '') + '  |')

        lst.append(self.stats(numbers, True))
        lst.append('')

        # add grouped stats, append to buffer
        numbers = numbers[:-end_weekday] if days else numbers
        if weeks:
            self.grouped_stats(numbers, 4)
        else:
            self.grouped_stats(numbers, 7)
            self.grouped_stats(numbers, 28)
        current.buffer.append(lst, lnum())

    def make_colums(self, numbers, start_weekday):
        """Create column lists"""
        self.mx = max(numbers)
        cols = []
        for i, n in enumerate(numbers):
            col = ['-'] if compact else ['', self.ftime(n), "-----"]
            col.extend(make_bar(n, self.mx, barunit, 8) + [''])
            cols.append(col)
            x = 4 if weeks else 7
            if (i+start_weekday) % x == 0:
                cols.append([' ']*gheight)
        return cols

    def ftime(self, h):
        if weeks:
            return str(int(round(h)))
        else:
            mins = int((h - int(h)) * 60)
            return "%d:%02d" % (int(h), mins)

    def grouped_stats(self, numbers, length):
        """Append stats to buffer, grouped by lengths (e.g. 7 for by-week, 28 by 'month')."""
        numbers = list(reversed(numbers))
        numbers = zip(*[numbers[i::length] for i in range(length)])
        if not numbers: return
        if   length == 7       : lst.append("Weekly:")
        elif length in (4, 28) : lst.append("Monthly:")

        tmp = []
        mx = max([sum(g) for g in numbers])
        for gnum, group in enumerate(numbers):
            bar = make_bar(sum(group), mx, wchar.encode("utf-8"), 20)
            bar = "  |%s|" % join(bar, '')
            tmp.append(self.stats(group) + bar)
            if days and (gnum+1)%4 == 0: tmp.append('')
        lst.extend(list(reversed(tmp)) + [''])

    def stats(self, numbers, full=False):
        """Calculate statistics."""
        avg = sum(numbers) / float(len(numbers))
        nz = [n for n in numbers if n]
        avgnz = sum(nz) / float(len(nz))
        skipped = len(numbers) - len(nz)
        avg, avgnz, mx, total = [self.ftime(x) for x in (avg, avgnz, self.mx, sum(numbers))]
        if full:
            i = "Days" if days else "Weeks"
            stat = "[Avg %s] [Avg NZ %s] [Max %s] [%s %d] [%s NZ %d] [Skipped %s %d] [Total %s]"
            return stat % (avg, avgnz, mx, i, len(numbers), i, len(nz), i, skipped, total)
        else:
            return "[Avg %s] [Max %s] [Skipped %d] [Total %s]" % (avg, mx, skipped, total)

def make_bar(n, mx, barunit, total):
    bar = int(round((n / mx) * total))
    return [barunit]*bar + [' ']*(total-bar)


if __name__ == '__main__':
    Graph().create()
"""Helpgrep given words in any order; empty input repeats last search."""

from vim import *
from string import join

def exists(var):
    return int(eval("exists('%s')" % var))

def helpgrep():
    command("call inputsave()")     # avoid problems with vim's typeahead mechanism
    pat = eval("input('HelpGrep> ')")
    command("call inputrestore()")
    if not pat:
        if exists("s:pat"): pat = eval("s:pat")
        else: return

    command("let s:pat='%s'" % pat)
    words = [".*%s.*" % w for w in pat.split()]
    command(":helpgrep %s" % join(words, "\&"))

if __name__ == "__main__":
    helpgrep()
"""LineNums version in python. Not used because it's much more sluggish."""

from vim import *

def linenums():
    lines = int(eval("s:lines"))
    if not int(eval("exists('s:lnums_defined')")):
        command(":highlight SignColumn guibg=darkgreen")
        for i in range(1, lines):
            command(":sign define %s text=%s texthl=Search" % (i,i))
        command("let s:lnums_defined = 1")

    top_line_num = int(eval('line("w0")'))
    if int(eval('exists("s:old_num")')):
        if eval("s:old_num") == top_line_num and eval("a:0") == '0':
            # if arg is passed, (a:0 will be 1), force redraw
            return
    buf = eval('bufnr("%")')

    # Place line numbers
    fold_adj = 0
    x = top_line_num
    for i in range(1, lines):
        # '2' here is just any unique number
        command(":sign place 2 line=%s name=%s buffer=%s"  % (x, i, buf))
        fold_end = eval("foldclosedend(%s)" % x)
        x += 1
        if fold_end != '-1':
            x = fold_end + 1
    command("let s:old_num = %s" % top_line_num)


if __name__ == '__main__':
    linenums()
#!/usr/bin/env python
from django.conf import settings
settings.configure(DEBUG=True, TEMPLATE_DEBUG=True, DATABASE_ENGINE="django.db.backends.sqlite3",
                   DATABASE_NAME="vimtobu.db", INSTALLED_APPS=["vimtobu"])
from django.core.management import execute_manager

if __name__ == "__main__":
    execute_manager(settings)
""" Only - similar to :only but keep special windows open """

from vim import *

def only():
    bufname = current.buffer.name
    for x in range(5):
        command("call NextWin()")
        if current.buffer.name != bufname:
            wincmd('c')

if __name__ == '__main__':
    only()
import os, sys
from string import join
from time import asctime, sleep
from os.path import expanduser, basename, split, join as pjoin

sys.path.append(expanduser("~/.vim/python/"))
import util
from util import *
from vim import *

cls_def_pat = r"^\s*\(class\|def\) [a-zA-Z0-9_]\+\(:\|(.*)\)"

def add_todo():
    """Add a todo item."""
    fn     = expanduser("~/docs/lst.todo")
    todo   = input("new todo >")
    fldtpl = exist_eval("s:fldtpl") or " %-25s%-10s%-10s%-6s%-6s%-8s%s"

    if todo:
        todo = fldtpl % (todo, '', '1', '1', '0', 'No', join(asctime().split()[:3]))
        with open(fn) as fp: lst = fp.readlines()
        lst.insert(2, todo + '\n')
        with open(fn, 'w') as fp: fp.writelines(lst)

def buflisted(expr): # in util
    """Is buffer 'listed' (shows up in :ls)?"""
    return int(eval("buflisted('%s')" % expr))

def valid(fn):
    if fn and buflisted(fn):
        for x in ".trak .todo .proj".split():
            if fn.endswith(x): return False
        return True

def delbuffers():
    """ Show a list of buffers, mark for deletion & delete.

        In scratch buffer:
            Space - mark buffers (in visual or normal mode)
            d     - save & close all marked buffers; close scratch window
    """
    if eval("&filetype") == "vimject":
        wincmd('l')
    buf = current.buffer
    let("s:current_buffer", current.buffer.name)
    command("new")
    command("set buftype=nofile")

    l = ["  %d %s" % (n, b.name) for n, b in enumerate(buffers) if valid(b.name)]
    current.buffer[0:1] = l
    command("noremap <buffer> <Space> :call Other('delbuf_mark')<cr>")
    command("noremap <buffer> o :call Other('switch_to_buf')<cr>")
    command("nnoremap <buffer> <Enter> :call Other('del_marked_bufs')<cr>")

def switch_to_buf():
    bname = current.line[1:].strip().split(' ', 1)[1]
    bdelete()
    swbuffer(bname)

def bdelete(expr=None):
    if expr : command("bdelete %s" % fnescape(expr))
    else    : command("bdelete")

def swbuffer(expr):
    try:
        command("buffer %s" % fnescape(expr))
        return True
    except:
        return False

def delbuf_mark():
    l = current.line
    l = ('+' if l.startswith(' ') else ' ') + l[1:]
    current.line = l
    down()

def lrmwords(x, n=1):
    """Remove `n` words (single space separated) from left side of string `x`."""
    return x.split(' ', n)[n]

def del_marked_bufs():
    """Delete all marked buffers."""
    # make a list of buffers for deletion, remove initial buffer from list
    buf     = current.buffer
    scratch = bufnr('%')
    origbuf = eval("s:current_buffer")
    lst     = [lrmwords(l, 2) for l in buf if l.startswith('+')]
    delcur  = origbuf in lst
    if delcur: lst.remove(origbuf)

    # save and delete marked buffers
    for fn in lst:
        swbuffer(fn)
        command("write")
    swbuffer(scratch)
    for fn in lst:
        bdelete(fn)

    if delcur: delbuffer(origbuf)
    bdelete(scratch)

def last_of_type(buftype):
    """Switch to last viewed buffer of `buftype` type (extension)."""
    bufname  = current.buffer.name
    prevbufs = exist_eval("g:bufenter_list")
    switched = False

    # try to switch to previous non-special buffer
    if prevbufs and len(prevbufs) > 1:
        prevbufs = reversed(prevbufs[:-1])
        for b in prevbufs:
            if bufloaded(b) and b != bufname and b.endswith(buftype):
                swbuffer(b)
                break

def last_of_type_py(): last_of_type(".py")
def last_of_type_html(): last_of_type(".html")

def delbuffer(bufname=None):
    """Switched to previous 'non-special' buffer & delete current buffer, keeping windows intact."""
    # save if possible and init bufname
    if eval("&buftype") != "nofile":
        command("write")
    if not bufname:
        bufname = current.buffer.name

    # try to switch to previous non-special buffer
    prevbufs = exist_eval("g:bufenter_list")
    switched = False
    if prevbufs and len(prevbufs) > 1:
        prevbufs = reversed(prevbufs[:-1])
        for b in prevbufs:
            if bufloaded(b) and b != bufname:
                swbuffer(b)
                switched = True
                break

    # fall back on :bprevious
    if not switched:
        for x in range(len(buffers)):
            command("bprevious")
            b = current.buffer.name
            if valid(b) and b != bufname and bufloaded(b):
                break

    # del buffer
    if current.buffer.name != bufname:
        # the check should not be required, but just in case, make sure window layout is not broken
        bdelete(bufname)
    return

    lst = [b.name for b in buffers if valid(b.name) if b.name != bufname]
    buflist = [b.name for b in buffers if b.name != bufname]

    buf2lst = None
    if lst       : buf2lst = lst[0]
    elif buflist : buf2lst = buflist[0]

    if buf2lst:
        # sometimes buffer switch fails when it's a full path; fucking Vim
        for buf in buf2lst:
            if swbuffer(buf):
                break
    else:
        command("new")
    bdelete(bufname)

def toggle_append():
    """ Toggle between appending to the 'x' register and normal copy.

        (pasting will terminate this mode)
    """
    xamode = iexist_eval("s:xappend_mode")

    if xamode:
        command("silent! nunmap y")
        command("silent! nunmap p")
        command("silent! nunmap P")
        command("silent! nunmap yy")
        command("silent! vnoremap y y`[")
        let("s:xappend_mode", 0)
    else:
        let('@x', '')
        command('nnoremap y "Xy')
        command('vnoremap y "Xy')
        command('nnoremap yy "Xyy')
        command('nnoremap p "Xp:call Other("toggle_append")<cr>')
        command('nnoremap P "XP:call Other("toggle_append")<cr>')
        let("s:xappend_mode", 1)
    print "X append mode " + ("off" if xamode else "on")

def select_function():
    """Visually select current function."""
    down()
    nwsearch(cls_def_pat, 'b')
    ln = lnum()
    nwsearch(cls_def_pat)
    up()
    normal("V%sgg" % ln)

def nwsearch(pat, flags=''):
    """No-wrap search. (in util, can be removed...)"""
    # go to end or beginning of line to ensure we start searching from next line
    if not flags : normal('$')
    else         : normal('0')
    return search(pat, flags+'W')

def delswp():
    """Delete vim swap file after restoring."""
    fn       = current.buffer.name
    path, fn = split(fn)
    swp      = pjoin(path, ".%s.swp" % fn)
    if os.path.exists(swp):
        os.remove(swp)
        print "Deleted " + swp

def iexist_eval(var):
    x = exist_eval(var)
    return None if x==None else int(x)

def super_line():
    """Insert line with a super() call for current class and function."""
    ln = blnum()

    search("^\s*def ", 'b')
    ind = indent() + 4
    l   = current.line
    if "self" not in l: return
    args     = l.split("self")[1].strip(", ):")
    function = l.split()[1].split('(')[0]

    search("^\s*class ", 'b')
    cls = current.line.split()[1].split('(')[0].strip(':')
    current.buffer[ln] = "%ssuper(%s, self).%s(%s)" % (' '*ind, cls, function, args)
    blnum(ln)
    normal('^')

def function_factor():
    """ Factor out function with return values:
        x, y = func(a, b)  ->  def func(a, b): return x, y
    """
    # go to start of visual selection, calculate indent
    normal("'<")
    l   = current.line
    ln  = lnum()
    ind = ind2 = indent(ln)
    if ind >= 4: ind -= 4

    # parse function call line
    l     = l.split('=')
    func  = l.pop().strip()
    rvals = l.pop() if l else ''
    s     = ''

    if func.startswith("self."):
        func = func[5:]
        s    = "self" if "()" in func else "self, "

    # generate def and return lines
    func  = func.replace('(', '('+s)
    out   = ["%sdef %s:" % (ind*' ', func)]
    ret   = "%sreturn %s\n" % (ind2*' ', rvals.strip()) if rvals else ''
    lines = eval('@y').split('\n')

    # cut function body, go to insertion point
    normal('gvoj"yx')   # cut visual selection to y register: gv o j "y x
    search_or_end(cls_def_pat)
    up()

    # assemble out list and insert into buffer
    if not lines[-1]: lines = lines[:-1]
    out.extend(lines)
    if ret: out.append(ret)
    current.buffer.append(out + [''], lnum())

def add_print():
    l             = current.line
    col           = current.window.cursor[1] + 1
    before, after = l[:col], l[col:]
    leading       = ''

    if ' ' in before:
        ind = before.rindex(' ') + 1
        leading, before = before[:ind], before[ind:]
    q = "'" if '"' in before else '"'
    before = 'print %s%s%s, %s' % (q, before, q, before)

    current.line = leading + before + after

def extract_arg():
    """Extract argument(s) from function call, give it a name and place on a line above."""
    let('@x', input("name: ") or 'x')
    normal('gv"yx')
    cmd = 'p' if (col()+1)==len(current.line) else 'P'
    normal('"x' + cmd)
    ind  = indent(lnum())
    x, y = eval('@x'), eval('@y')
    line = "%s%s = %s" % (ind*' ', x, y)
    current.buffer.append(line, lnum()-1)

def up(n=1): # in util, can delete
    normal("%dk" % n)

def down(n=1): # in util, can delete
    normal("%dj" % n)


if __name__ == '__main__':
    arg = exist_eval("a:arg")
    if arg:
        locals()[arg]()
# vim: set fileencoding=utf-8 :
# Imports {{{
"""Pseudo code outline.

Generate / toggle between python files and pseudo-code outline view.
"""
import os, sys
from os.path import dirname, split, splitext, exists, expanduser, join as pjoin
from pprint import pprint
from time import sleep

from vim import *

vimpython_dir = expanduser("~/.vim/python/")
sys.path.append(vimpython_dir)
from util import *
import util
reload(util) # if there is an error in a module, it's not auto-reloaded after the error is fixed..

from genpydoc import GenPyDoc
# }}}

# match: class X:  def main(y):
bul = '·'
cls_def_pat = r"^\s*\(class\|def\) [a-zA-Z0-9_]\+\(:\|(.*)\)"
otl_pat = bul + r" \(class\|def\) "

class PCOutline:
    def main(self):
        """ Toggle between pseudo-code outline and python source file.

            (If pseudo-code does not exist, generate it, but do not update it automatically.)
        """
        # init variables
        path = current.buffer.name
        dirn = dirname(path)
        fn = split(path)[-1]
        fn, ext = splitext(fn)
        if ext not in (".py", ".potl"):
            print "Only handling .py and .potl files.."
            return

        if ext == ".py":
            otl_fn = ".%s%s.potl" % (fn, ext)
            otl_path = pjoin(dirn, otl_fn)
            if self.generate_new(path, otl_path): return

            # find current item and switch to outline
            normal('j')
            found = nwsearch(cls_def_pat, 'b')

            if not found:
                found = nwsearch(cls_def_pat)
                if not found:
                    print "No classes or defs found!"
                    return
            cls_def = escape_pat(current.line.rstrip(':').strip())
            command("edit " + otl_path)

            if not nwsearch(cls_def):
                self.update_outline(cls_def, path)

        elif ext == ".potl":
            # find current item and switch to normal
            normal('j')
            found = nwsearch(otl_pat, 'b')
            if not found:
                found = nwsearch(otl_pat)
                if not found:
                    print "No classes or defs found!"
                    return
            cls_def = current.line.strip()[3:]
            command("edit " + pjoin(dirn, fn[1:]))
            search(escape_pat(cls_def))

    def update_outline(self, cls_def, path):
        """If current item not found, insert all missing items."""
        # command("redraw!")
        buf = current.buffer
        normal("gg")
        normal("zR")    # otherwise item x with a docstring will get item y appended before x's docstring
        nwsearch(bul)   # filename header
        if nwsearch(bul) : normal('k')
        else             : normal('G')
        lst = self.group_items(self.gendoc(path))

        for n, item in enumerate(lst):
            lstr = escape_pat(item[0].strip())
            if lstr and not nwsearch(lstr[3:]):
                # print "lstr", repr(lstr)
                if not nwsearch(bul): normal('G')
                current.buffer.append(item, lnum()-1)
        search(cls_def)

    def generate_new(self, path, otl_path):
        """Generate new"""
        if not os.path.exists(otl_path):
            lst = self.gendoc(path)
            with open(otl_path, 'w') as fp:
                fp.writelines([l + '\n' for l in lst])
            command("edit " + otl_path)
            return True

    def group_items(self, lst):
        """Group items with their docstrings, omit file header."""
        nlst, itemlst = [], []
        last = len(lst)-1

        for n, l in enumerate(lst):
            lstr = l.strip()
            if lstr.startswith(bul):
                if not itemlst:
                    itemlst.append(l)
                else:
                    if not itemlst[0].startswith(bul):
                        nlst.append(itemlst)            # skip file header
                    itemlst = [l]
            else:
                itemlst.append(l)

            if n==last and itemlst:
                nlst.append(itemlst)
        return nlst

    def gendoc(self, path):
        gpd = GenPyDoc()
        gpd.potl = True
        lst = []
        gpd.process_fn(path, lst)
        return lst

def escape_pat(pat):
    """ Escape pattern for vim search()

        - change ' to . because vim does not allow escaping ' with backslashes.
    """
    # note: group that inserts backslashes should be after group that escapes them!
    # subs = [s.split() for s in ("'  .",   r"\  \\",   r"*  \*",  r"=  \=")]
    subs = [s.split() for s in ("'  .",   r"\  \\",   r"*  \*",  r"[  \[",  r"]  \]")]
    for x, y in subs: pat = pat.replace(x, y)
    return pat

def nwsearch(pat, flags=''):
    """No-wrap search."""
    # go to end or beginning of line to ensure we start searching from next line
    if not flags : normal('$')
    else         : normal('0')
    return search(pat, flags+'W')

if __name__ == '__main__':
    PCOutline().main()
# -*- coding: utf-8 -*-
"""Python outliner."""

import sys
from time import sleep
from os.path import expanduser
sys.path.append(expanduser("~/.vim/python/"))

from vim import *
from util import *

def new_header():
    """ Add a new outliner header

        - new header will be the same level as current header
        - header is added right before the next header of same level
        - if no header at the same level is found, new one is added at the end of file
    """
    # init vars
    buf = current.buffer
    ind = 0
    lnum = blnum()
    down()
    sleep(0.01)                 # make sure search starts from current line, not line above (!)

    # find next 'sibling' header and add the new header
    if search('·', 'bW'):       # back nowrap
        ind = col()
        while 1:
            found = search(r"^[ ]*·", 'W')
            ind2 = len(current.line) - len(current.line.lstrip())
            if not found or ind2 <= ind:
                lnum = len(buf) if not found else blnum()
                break
    buf.append(' '*ind + '· ', lnum)
    blnum(lnum)

if __name__ == "__main__":
    val = exist_eval("a:1")
    if val:
        globals()[val]()
"""Fold python comments and strings."""
import re
from vim import *

def pydocfold():
    cur = 0
    b = current.buffer
    end = len(b)
    startfold = comment = False
    command("set foldmethod=manual")
    command("set fml=0")
    for cur in range(end):
        l = b[cur].strip()
        lst = l.startswith
        lend = l.endswith
        if comment and not lst("#"):
            # close comments fold
            command("%s,%sfold" % (startfold, cur))
            startfold = comment = False
            continue

        if startfold != False and lend('"""'):
            # close multiline fold
            command("%s,%sfold" % (startfold, cur+1))
            startfold = False
            continue

        if lst('"""') and not re.match('^""".*"""$', l) and startfold == False:
            # start multiline fold
            startfold = cur+1

        if not comment and lst("#"):
            # start comment fold
            comment = True
            startfold = cur+1

        # single line dosctrings
        if startfold == False:
            if lst('"') and lend('"') and not lend('"""'):
                # dbl quote docstring
                command("%sfold" % (cur+1))
            if (lst("'") and lend("'")) or (lst('"""') and lend('"""') and l != '"""'):
                # single quote or triple quote docstring
                command("%sfold" % (cur+1))

    # command("hi Folded guifg=#4f4f4f guibg=#3f3f3f")    # "almost hide" in zenburn scheme

if __name__ == "__main__":
    pydocfold()
"""Create a copy of buffer with stripped python comments and docstring."""
import re
from vim import *


def pystripdoc():
    # close preview window; copy the buffer into a new window
    command("pclose!")
    command("setlocal ft=python")
    command("silent %y a")
    command("below new")
    command("silent put a")

    cur = 0
    b = current.buffer
    end = len(b)
    startdel = comment = False
    dellst = []

    # make a list of lines to delete
    for cur in range(end):
        if cur >= len(b):
            break
        l = b[cur].strip()
        lst, lend = l.startswith, l.endswith
        if comment and not lst("#"):
            # end multiline comment
            dellst.append((startdel, cur))
            startdel = comment = False
            continue

        if startdel != False and lend('"""'):
            # end multiline docstring
            dellst.append((startdel, cur+1))
            startdel = False
            continue

        if lst('"""') and not re.match('^""".*"""$', l) and startdel == False:
            # start multiline docstring
            startdel = cur+1

        if not comment and lst("#"):
            # start multiline comment
            comment = True
            startdel = cur+1

        # single line dosctrings
        if startdel == False:
            if lst('"') and lend('"') and not lend('"""'):
                # dbl quote docstring
                dellst.append((cur+1,))
            if (lst("'") and lend("'")) or (lst('"""') and lend('"""') and l != '"""'):
                # single quote or triple quote docstring
                dellst.append((cur+1,))

    # delete lines
    dellst.reverse()
    for tup in dellst:
        if len(tup) == 1: command("%sd" % tup[0])
        else: command("%s,%sd" % tup)

    command("setlocal ft=python")
    command("setlocal previewwindow")


if __name__ == "__main__":
    pystripdoc()
#!/usr/bin/env python
""" Reminders - periodically remind about upcoming tasks. """

# Imports, Init {{{
# from vim import *
import sys
import shelve
from datetime import date, timedelta
from string import join
from os.path import expanduser
from operator import attrgetter

try:
    import vim
    from_vim = True
except ImportError:
    input = raw_input
    from_vim = False

if from_vim:
    import util
    from util import *
# }}}

# Init {{{
today    = date.today()
tpl      = "%3s %-22s %3s days [ %2d ]"
days     = "yesterday today tomorrow".split()
tasklist = [
        # to disable, set 'every' to a high number
        # ... , every x days, start on
        ["asanas"              , 2, (2011, 4, 10)],
        ["tidy-up"             , 2, (2011, 4, 10)],
        ["dusting"             , 2, (2011, 4, 12)],
        ["yahoo mail"          , 2, (2011, 4, 11)],
        ["brush"               , 2, (2011, 4, 12)],

        ["pranayama"           , 2, (2012, 2, 16)],
        ["bandhas"             , 2, (2012, 2, 16)],
        ["ears"                , 3, (2011, 4, 10)],
        ["plants"              , 4, (2011, 4, 10)],
        ["cleaning"            , 4, (2011, 4, 11)],
        ["clean sinks"         , 4, (2011, 6, 11)],
        ["headstand"           , 5, (2011, 4, 10)],
        ["vacuum"              , 5, (2011, 4, 10)],

        ["clean humidifier"    , 6, (2011, 4, 16)],
        ["backup"              , 7, (2011, 4, 10)],
        ["plants2"             , 8, (2011, 4, 10)],
        ["sheets"              , 10, (2012, 2, 23)],
        ["neti"                , 14, (2011, 4, 11)],
        ["nails"               , 25, (2011, 4, 11)],
        ["grandma"             , 35, (2012, 2, 5)],
        ]

# }}}

class Container:
    def __init__(self, **kwds)  : self.__dict__.update(kwds)
    def __setitem__(self, k, v) : self.__dict__[k] = v
    def __delitem__(self, k)    : del self.__dict__[k]
    def __getitem__(self, k)    : return self.__dict__[k]
    def __any__(self)           : return any(self.__dict__)
    def __str__(self)           : return str(self.__dict__)
    def __unicode__(self)       : return unicode(self.__dict__)
    def pop(self, *args)        : return self.__dict__.pop(*args)
    def update(self, arg)       : return self.__dict__.update(arg)
    def items(self)             : return self.__dict__.items()
    def keys(self)              : return self.__dict__.keys()
    def values(self)            : return self.__dict__.values()
    def dict(self)              : return self.__dict__
    def pp(self)                : pp(self.__dict__)


class Task(object):
    """Task definition."""
    def __init__(self, lst):
        self.name, self.every, self.start = lst
        if isinstance(self.start, tuple):
            self.start = date(*self.start)

    def __eq__(self, other):
        return (self.name, self.every) == (other.name, other.every)

    def __hash__(self):
        return hash(self.name) ^ hash(self.every)

    def activeX(self, day):
        """UNUSED day := yesterday | today | tomorrow"""
        adjust = 0
        if   day == "yesterday": adjust = -1
        elif day == "tomorrow": adjust = 1
        return (self.days()+adjust) % self.every == 0

    def active(self, day):
        """True if active on `day` date."""
        # if self.name == "clean humidifier":
            # print "self.every", self.every
            # print (self.days(day) % self.every) == 0
        days = self.days(day)
        return days >= 0 and (days % self.every) == 0

    def __str__(self):
        return "%-28s [ %2d ]" % (self.name, self.every)

    def __repr__(self):
        return "task: %s" % self.name

    def days(self, to_date=today):
        """Number of days from start to `to_date`."""
        return (to_date - self.start).days


class TaskItem(object):
    """Task item for a particular date."""
    show = True

    def __init__(self, *args):
        self.task, self.duedate, self.every = args

    def __eq__(self, other):
        return (self.task, self.duedate) == (other.task, other.duedate)

    def __hash__(self):
        return hash(self.task) ^ hash(self.duedate)

    def __str__(self):
        return self.task

    def tprint(self, n):
        print tpl % (str(n) + ')', self, self.late(), self.every)

    def late(self):
        """How late is the task, in days; 0 if task due today."""
        return (today - self.duedate).days


class Tasks(Container):
    def __init__(self):
        self.load()
        self.create()

    def any(self):
        """unused"""
        return self.yesterday or self.today or self.tomorrow

    def show_all(self):
        """unused"""
        if self.any():
            for day in days:
                if self[day]:
                    print "    %s" % day.capitalize()
                    print join([str(t) for t in self[day]], '\n')
                    print "---"
        else:
            print "No tasks"

    def load(self):
        self.shelve       = shelve.open(expanduser("~/.reminder_tasks"))
        self.tasks        = self.shelve.get("tasks", {})
        self.items        = self.shelve.get("items", set())
        self.last_checked = self.shelve.get("last_checked", today)

    def save(self):
        self.shelve["tasks"]        = self.tasks
        self.shelve["items"]        = self.items
        self.shelve["last_checked"] = today
        self.shelve.close()

    def create(self):
        """Schedule new tasks and add them to `self.tasks`."""
        for name, every, start in tasklist:
            task = self.tasks.get(name, None)
            if task:
                if task.every != every:
                    task.every = every
            else:
                self.tasks[name] = Task((name, every, start))

        duedate = max(self.last_checked, today - timedelta(30))

        dbg = 0
        while 1:
            new = [t for t in self.tasks.values() if t.active(duedate)]

            if dbg and new: print "duedate", duedate
            for t in new:
                item = TaskItem(t.name, duedate, t.every)
                itemlst = [i for i in self.items if i.task==item.task]

                if dbg: print "item", item, item in self.items
                if dbg: print "len(itemlst)", len(itemlst)
                if dbg and itemlst: print "show:", [i.show for i in itemlst]
                if dbg: print ' '

                self.items.add( item )
            if new: print
            duedate += timedelta(1)
            if duedate > today:
                break

    def mark_done(self, name):
        item = None
        for i in self.items:
            if i.task == name:
                i.show = False
                item = i
        if item:
            self.tasks[item.task].start = today + timedelta(item.every)

    def get_new(self):
        """Get a sorted list of new tasks."""
        # sort by due date and filter out newer copies of active tasks
        items = sorted([t for t in self.items if t.show], key=attrgetter("duedate"))
        new = {}

        for t in items:
            if t.task not in new:
                new[t.task] = t

        # sort by 'lateness'
        return sorted(new.values(), key=lambda x: x.late(), reverse=True)

    def show(self):
        """Display the list of current tasks."""
        items = self.get_new()
        print ' '
        for n, item in enumerate(items):
            item.tprint(n+1)

        # accept list of 'done' tasks and mark them as hidden
        print " \nTo mark as done, use command: d num [num2 num3 ...]"
        uinp = input("> ")

        if uinp and uinp.startswith('d'):     # esc in input() returns None
            uinp = uinp[1:].strip().split()
            for num in uinp:
                try:
                    item = items[int(num)-1]
                    self.mark_done(item.task)
                except ValueError, IndexError:
                    print "invalid input:", num


if __name__ == '__main__':
    t = Tasks()
    t.show()
    t.save()
"""Resize Vim window cycling through a number of default sizes."""
import sys
from vim import *
from os.path import expanduser
sys.path.append(expanduser("~/.vim/python/"))
import util
from util import *

minwidth  = 100
maxheight = 63

sizes = [ # 59 / 66
         (20        , minwidth),
         (35        , minwidth),
         (54        , minwidth),
         (maxheight , minwidth),
         (maxheight , 136),
         (maxheight , 160),
         (maxheight , 200),
         (maxheight , 245),
]


def setsize(line, col):
    command("set lines=%s columns=%s" % (line, col))

def resize():
    lines = ieval("&lines")
    cols  = ieval("&columns")
    dir   = ieval("a:dir")

    if dir == 0: sizes.reverse()

    for ln, col in sizes:
        if (dir==0 and (ln < lines or col < cols)) or \
           (dir==1 and (ln > lines or col > cols)):
                setsize(ln, col)
                break

if __name__ == '__main__':
    resize()
"""
Searchcode plugin - search in code only, skipping strings and python-style comments

Notes:
 - Search is case insensitive
 - If you hit Enter at prompt, last search is repeated
 - Bug: won't skip some strings, e.g. if a few strings are mixed with code on one line,
   but should be good for docstrings and comments
"""

from vim import *
from re import *
import sys

multiline_dbl_quote = multiline_single_quote = False

def exists(var):
    return int(eval("exists('%s')" % var))

def main():
    # get pattern
    pat = None
    arglen = eval("a:0")                # length of arg list
    if arglen == "0":
        command("call inputsave()")     # avoid problems with vim's typeahead mechanism
        pat = eval("input('/')")
        command("call inputrestore()")
    if not pat:
        if exists("s:pat"):
            pat = eval("s:pat")
        else:
            return
    pat = pat.lower()
    command("let s:pat='%s'" % pat)

    # init vars
    w = current.window
    curline, col = w.cursor
    b = current.buffer
    end = len(b)

    if pat:
        found = iterate(curline, end, w, b, pat)
        if not found:
            found = iterate(0, curline, w, b, pat)
            if not found:
                print "pattern not found:", pat

def st_end_multi(l):
    "Line starts or ends multiline docstring."
    l = l.strip(); lst = l.startswith; lend = l.endswith
    if lst('"""') or lend('"""') or lst("'''") or lend("'''"):
        return True

def dblquotes(l):
    "Double quotes enclosed string."
    if l.find('"') != -1 and l.find('"') < l.find("'"):
        return True

def find(l, pat, quote, w):
    "Find pattern in line, excluding string."
    st, end = l.find(quote), l.rfind(quote)
    # print "st, end: ", st, end
    subl = l[st:end]
    i = subl.find(pat)
    if i != -1:
        if i > st:
            i += end-st
        w.cursor = (cur+1, i)
        return True

def iterate(fr, to, w, b, pat):
    ''' Iterate over lines, search for pattern.

        Handle these cases (and similarly for single quotes):
        """ docstring """
        """
        docstring
        """
        """ docstring
        ... """
        " docstring "

        This one's not handled yet:
        print """
        stuff
        """
    '''
    global multiline_dbl_quote, multiline_single_quote
    for cur in range(fr, to):
        l = b[cur].strip()
        lst = l.startswith
        lend = l.endswith

        # skip lines
        if match('^""".*"""$', l) or match("^'''.*'''$", l):
            continue
        elif lst('"""') and not multiline_dbl_quote:
            multiline_dbl_quote = True
            continue
        elif lst("'''") and not multiline_single_quote:
            multiline_single_quote = True
            continue
        elif multiline_dbl_quote and lend('"""'):
            multiline_dbl_quote = False
            # print "multiline_dbl_quote end"
            continue
        elif multiline_single_quote and lend("'''"):
            multiline_single_quote = False
            continue
        elif lst("#") or (lst('"') and lend('"')) or (lst("'") and lend("'")):
            continue
        elif multiline_dbl_quote or multiline_single_quote:
            continue

        # lines we can search
        l = b[cur].lower()
        if "#" in l:
            l = l.split("#")[0]
        elif "'''" in l or '"""' in l and not st_end_multi(l):
            pass
        elif '"' or "'" in l:
            if dblquotes(l): quote = '"'
            else: quote = "'"
            found = find(l, pat, quote, w)
            if found:
                return True
        i = l.find(pat)
        if i != -1:
            w.cursor = (cur+1, i)
            return True


if __name__ == "__main__":
    main()
"""
Sortable table, sort by headers, alphanumeric or numeric, automatically detect column data type.
"""

from vim import *
from time import *
import re, sys
from copy import deepcopy
from os.path import expanduser, join as pjoin
from string import join
sys.path.append(expanduser("~/scripts/"))

class Sort:
    def cmp1(self, a, b):
        """Compare two items, used by sort, can compare numbers or alphanumeric. Note: see
        todo_sort.py for an example of sorting by date."""
        a, b = a[self.index], b[self.index]
        if self.sortmode[self.index] == 0:
            a, b = float(a), float(b)

        elif self.sortmode[self.index] == 2:
            try:
                a = strptime(a, "%a %b %d")
                b = strptime(b, "%a %b %d")
            except:
                pass
        return cmp(a, b)

    def sort(self):
        pos = current.window.cursor
        b = current.buffer
        self.index = 0

        # find out what to sort by
        headers = [fld.strip() for fld in re.split("\s\s+", b[0])]
        ncols = len(headers)
        cword = eval("expand('<cword>')")     # word under cursor
        if cword in headers:
            self.index = headers.index(cword)

        # parse the data
        rows = []
        maxl = [2]*ncols
        self.sortmode = [0]*ncols
        skipped = []
        for l in b[2:]:
            if l.strip():
                flds = [fld.strip() for fld in re.split("\s\s+", l)]
                if len(flds) != ncols:
                    print "Wrong num. of columns, skipping line: %s" % l
                    skipped.append(l)
                    continue
                for n, fld in enumerate(flds):
                    if len(fld) > maxl[n]:
                        maxl[n] = len(fld)
                    if not (re.match("^[0-9.]+$", fld) and fld != '.'):
                        self.sortmode[n] = 1
                rows.append(flds)

        maxl = [x+3 for x in maxl]

        # sort, asc or desc
        orig = deepcopy(rows)
        rows.sort(cmp=self.cmp1)
        if orig == rows:
            rows.sort(cmp=self.cmp1, reverse=True)

        # make line template, insert headers, rows
        fldtpl = ''
        total = 0
        for ml in maxl:
            total += ml
            fldtpl += "%%-%ds" % ml

        total -= 3
        r = [fldtpl % tuple(t) for t in rows]
        hr = fldtpl % tuple(headers)

        del b[:]
        out = [hr.strip(), '-'*total] + [r.strip() for r in r]
        if skipped: out += ['',''] + skipped
        b[0:0] = out

        current.window.cursor = pos     # restore cursor


if __name__ == '__main__':
    Sort().sort()
"""
Module doc.
"""

def test():
    "function doc."
    a = 5

class A:
    "Class doc."
""" Add a new todo item. """
from vim import *
from time import *
from string import join

def newtodo():
    b = current.buffer

    # default line template or reuse one from sort(), to keep alignment
    fldtpl = " %-25s%-10s%-10s%-6s%-6s%-8s%s"
    if int(eval("exists('s:fldtpl')")):
        fldtpl = eval("s:fldtpl")

    # insert header and divider
    flds = tuple(eval("s:headers").split())
    if not b[0].startswith(' ' + flds[0]):
        b[0:0] = [fldtpl % flds, '-'*76]

    # insert new task with default values
    lnum = current.window.cursor[0] - 1
    if lnum < 2: lnum = 2
    start = asctime().split()[:3]
    flds = ("Task", '', '1', '1', '0', "No", join(start))
    b[lnum:lnum] = [fldtpl % flds]

    current.window.cursor = (lnum+1, 0)

if __name__ == '__main__':
    newtodo()
"""Open todo window."""
from vim import *

def opentodo():
    sb = int(eval("&splitbelow"))
    command("set splitbelow")
    for b in buffers:
        if b.name and b.name.endswith(".todo"):
            bnr = eval("bufnr('%s')" % b.name)
            if int(eval("buflisted(%s)" % bnr)):
                command("split %s" % b.name)

                # resize window to show all active tasks only
                for n, l in enumerate(current.buffer):
                    if not l.strip():
                        n += 2
                        if n < 6: n = 6
                        command('exe "normal %d\\<c-w>_"' % n)
                        command("normal gg")
                        break
                break
    if not sb:
        command("set nosplitbelow")

if __name__ == '__main__':
    opentodo()
"""
Sort todo item list. By default, sorting is by priority, to sort by a different header,
cursor should be positioned on the header and sort command activated.
"""

from vim import *
from time import *
import re, sys
from os.path import expanduser, join as pjoin
from string import join
from copy import deepcopy
sys.path.append(expanduser("~/scripts/"))

leftmargin = 1

class Sort:
    def cmp1(self, a, b):
        """Compare two items, used by sort, can compare numbers, alphanumeric or dates."""
        a, b = a[self.index], b[self.index]
        if self.index in (2,3,4):
            a, b = int(a), int(b)
        elif self.index == 6:
            try:
                a = strptime(a, "%a %b %d")
                b = strptime(b, "%a %b %d")
            except:
                pass
        return cmp(a, b)

    def sort(self):
        # find out what to sort by
        headers = tuple(eval("s:headers").split())
        self.index = 2                        # header to sort by
        cword = eval("expand('<cword>')")     # word under cursor
        pos = current.window.cursor
        b = current.buffer
        if cword in headers:
            self.index = headers.index(cword)

        # parse the task list
        tasks = []
        maxl1 = 4; maxl2 = 7    # task and project name max widths
        for l in b[2:]:
            if l.strip():
                flds = [fld.strip() for fld in re.split("\s\s+", l)]
                if len(flds) not in (6,7):
                    print "Error: wrong number of fields in line: %s" % l
                    return
                if len(flds) == 6: flds.insert(1, '')   # no project
                if len(flds[0]) > maxl1: maxl1 = len(flds[0])
                if len(flds[1]) > maxl2: maxl2 = len(flds[1])
                tasks.append(flds)
        maxl1 += 3; maxl2 += 2

        # separate Done, OnHold and sort the rest
        done = [t for t in tasks if t[4] == "100"]
        onhold = [t for t in tasks if t[5].lower() == "yes" and t[4] != "100"]
        tasks = [t for t in tasks if t[4] != "100" and t[5].lower() != "yes"]

        # sort in asc order; if was sorted, sort in desc order
        was_sorted = True
        for t in (done, onhold, tasks):
            original = deepcopy(t)
            t.sort(cmp=self.cmp1)
            if t != original: was_sorted = False

        if was_sorted:
            for t in (done, onhold, tasks):
                t.sort(cmp=self.cmp1, reverse=True)

        # make line template, insert headers, tasks, OnHold and Done
        divlen = maxl1 + maxl2 + 40 + leftmargin     # divider line
        del b[:]
        fldtpl = ' '* leftmargin + "%%-%ds%%-%ds" % (maxl1, maxl2) + "%-10s%-6s%-6s%-8s%s"
        b[0:0] = ([fldtpl % headers, '-'*divlen] +
                  [fldtpl % tuple(t) for t in tasks] + [''] +
                  [fldtpl % tuple(t) for t in onhold] + [''] +
                  [fldtpl % tuple(t) for t in done])

        # save line template to use when adding new tasks (to keep alignment)
        command("let s:fldtpl='%s'" % fldtpl)
        current.window.cursor = pos     # restore cursor


if __name__ == '__main__':
    Sort().sort()

# Imports {{{
import os
import re
from time import *
import time
from string import join
from datetime import datetime
from collections import defaultdict
from os.path import expanduser

from vim import *

sys.path.append(expanduser("~/.vim/python/"))
import util
reload(util) # if there is an error in a module, it's not auto-reloaded after the error is fixed..
from util import *

modifier = 0.55

# example on/off lines:
# myproj          [on]  [11:40 AM] []            [0:00]  [rate:16] [$0]
# myproj          [off] [11:40 AM] [11:51 AM]    [0:11]  [rate:16] [$3]
projpat = (r"(.*)\[(on|off)\] "
            "[ ]+ \[([0-9: APM]+)\] "
            "[ ]+ \[([0-9: APM]+|)\] "
            "[ ]+ \[([0-9:]+)\] "
            "[ ]+ \[rate:([0-9\.]+)\] "
            "[ ]+ \[\$? ([0-9\.]+) \] [ ]* ")

tploff =  "%s[%s] [%s] [%s]    [%s]   [rate:%s] [%s]"
tplon =   "%s[%s]  [%s] [%s]            [%s]   [rate:%s] [%s]"
tplblnk = "%s   [off] [] []     [0:00]       [rate:0] [0]"
_last = "g:trak_last_start"
# }}}

def add_date():
    """Insert today's date."""
    today = time.strftime("%a, %b %d %y", localtime())
    bufappend( ["--- %s" % today] , lnum() )

def new_proj():
    """Add a new project."""
    n = input("Name: ")
    if n:
        bufappend(tplblnk % n, lnum())
        normal("j0")

def reset_time():
    """Reset time to 0:00."""
    s = re.search(projpat, current.line, re.VERBOSE)
    if s:
        g = list(s.groups())
        g[4] = "0:00"
        g[6] = '0'
        tpl = tplon if g[1] == "on" else tploff
        current.line = tpl % tuple(g)

def addperc(): add_time(addperc=modifier)

def add_time(addperc=False):
    """ Add or subtract total time for current line's project (by inputting -time).

        addperc: add `addperc` percent
    """

    s = re.search(projpat, current.line, re.VERBOSE)
    if s:
        g = list(s.groups())
        total = g[4]
        try:
            h, m = total.split(':')
            total = int(h)*60 + int(m)
        except:
            print "Error parsing current line."
            return

        if addperc : add = str(int(total*addperc))
        else       : add = input("Add minutes:")

        if add and re.match("-?[0-9]+\.[0-9]+", add):
            total += float(add) * 60
        elif add and re.match("-?[0-9]+", add):
            total += int(add)

        g[4] = "%d:%02d" % (total/60, total%60)

        rate = int(g[5])
        earned = int(rate*total/60.0)
        if earned: g[6] = "$%s" % earned

        tpl = tplon if g[1] == "on" else tploff
        current.line = tpl % tuple(g)

def calc_current():
    """Calculate current time."""
    start = exist_eval("g:trak_last_start")
    if start:
        current = (time.time() - float(start)) / 60.0
        print "%d:%02d" % (current/60, current%60)
    else:
        print "No last start var"

def calc_worked(g):
    """Calculate worked time and how much was earned. `g` is a list parsed from entry line."""
    if g[1] == "off":
        return g[4], '$'+g[6], None

    start = time.strptime(g[2].strip(), "%I:%M %p")

    total = 0
    if g[4]:
        t = g[4].split(':')
        total = int(t[0])*60 + int(t[1])

    # calculate time worked
    start_dt = list(localtime())
    start_dt[3:5] = start[3:5]     # update hour and minute
    start_dt = datetime(*start_dt[:5])
    delta = datetime.now() - start_dt

    # add up total and change line
    mins = round(delta.seconds / 60.0)
    total += mins
    worked = "%d:%02d" % (total/60.0, total%60)

    # rate
    earned = "$%d" % round( float(g[5])*total/60.0 ) if g[5] else "$0"
    return worked, earned, mins

def start_stop(ln=None, newline=True):
    """Toggle project on/off."""

    if ln == None: ln = lnum() - 1
    buf = current.buffer
    let("s:trak_bufname", buf.name)
    line = buf[ln]

    s = re.search(projpat, line, re.VERBOSE)
    if s:
        g = list(s.groups())
        if g[1] == "on":
            if exists(_last):
                command("unlet %s" % _last)

            g[4], g[6], mins = calc_worked(g)
            g[1] = "off"

            t = time.strftime("%I:%M %p", datetime.now().timetuple())
            g[3] = "%8s" % t.lstrip('0')
            buf[ln] = tploff % tuple(g)
            print "Added %d:%02d" % (mins/60, mins%60)

        elif g[1] == "off":
            auto_off()
            t = time.strftime("%I:%M %p", localtime())
            let(_last, time.time())
            # 0:name, 1:on/off, 2:start, 3:total, 4:rate, 5:$
            g[1:4] = [ "on", "%8s" % t.lstrip('0'), '' ]

            if newline:
                g[4] = "0:00"
                g[6] = "$0"
                buf.append(tplon % tuple(g), ln+1)
                normal('j')
            else:
                current.line = tplon % tuple(g)

def auto_off():
    """ Turn off last project when setting new one 'on'. If changing this function, must be careful
        to avoid infinite loop because start_stop() calls this function and we also call start_stop()
        from here as well.
    """
    orig = blnum()
    s = search("^--- ", 'b')
    if not s: bcursor(0,0)      # handle no date

    # find last active and turn it off
    s = search("  \[on\] \[")
    if s:
        start_stop(blnum(), False)

    bcursor(orig, 0)

def psec(minsec):
    """Split and parse min:sec to secondsself."""
    t = minsec.split(':')
    return int(t[0])*60 + int(t[1])

def report(inline=False):
    """ Insert a report of totals, grouped by project.

        Set `inline` to echo on command line instead of adding lines to the file.
    """
    if not current.line.startswith("---"):
        search("^---", 'b')
    start = end = blnum()+1
    buf = current.buffer

    # find end of current day
    for n, l in enumerate(buf[start:]):
        if not l.strip():
            pass
        elif re.match(projpat, l, re.VERBOSE):
            end = start + n + 1
        else:
            break

    lines = buf[start:end]
    print_groups = False    # print grouped projects only if there are multiple entries for a project

    # make a dictionary of projects: {name: [time, earned], ...}
    projects = defaultdict(list)
    for l in lines:
        s = re.search(projpat, l, re.VERBOSE)
        if s:
            g = s.groups()
            name = g[0].strip()

            worked, earned, _ = calc_worked(g)

            lst = projects[name]
            if not lst: lst = [0, 0]
            else: print_groups = True

            projects[name] = [ lst[0] + psec(worked), lst[1] + int(earned[1:]) ]

    total_all = made_all = divlen = 0

    # make templates for just time and time + earned
    maxl = max( [0] + [len(p) for p in projects] )
    maxl += 5
    tpl = "%%-%ds%%d:%%02d" % maxl
    tpl2 = tpl + "  $%d"

    # make a list of report lines
    lst = []
    for name, (total, made) in projects.items():
        if made:
            l = tpl2 % (name, total/60, total%60, made)
        else:
            l = tpl % (name, total/60, total%60)

        divlen = max(divlen, len(l))
        if print_groups: lst.append(l)
        total_all += total
        made_all += made

    # add divider and totals
    total = []
    if len(projects) > 1 or not lst:
        total = [tpl2 % ("Total:", total_all/60, total_all%60, made_all)]
    total = []
    if inline:
        print join(lst + total, " | ")
    else:
        divider = ['-'*divlen] if len(lst) > 1 else []
        divider = []
        current.buffer.append(divider + lst + total, end)
        blnum(end + len(lst) + len(total))

def inline_report():
    report(inline=True)

def start_stop2():
    start_stop(None, False)


if __name__ == "__main__":
    cmd = exist_eval("a:1")
    if cmd: globals()[cmd]()
#!/usr/bin/env python
"""ulist - format unordered list. """

from string import join
from re import search

def from_vim():
    """Get vars and lines from Vim and call format().
    """
    import vim
    b = vim.current.buffer
    lnum = int(eval("a:lnum")) + 1
    count = int(eval("a:count"))
    textwidth = int(eval("&tw"))
    # b[lnum:lnum+count] = format(b[lnum:lnum+count], textwidth)
    return format(b[lnum:lnum+count], textwidth)

def format(lines, textwidth):
    """Format and return lines."""
    nl = []
    indent = use_indent = 0
    newl = None
    for l in lines:
        bullet = False
        if l.strip().startswith("-"):
            bullet = True
            indent = l.find("-")
            if len(l) > textwidth:
                words = l.split()
                newl = []
                bullet = True
                for w in words:
                    testline = join(newl + [w], ' ')
                    use_indent = indent
                    if not bullet:
                        use_indent = indent + 2
                    print "use_indent: ", use_indent
                    if use_indent + len(testline) <= textwidth:
                        newl.append(w)
                    else:
                        nl.append(' '*use_indent + join(newl, ' '))
                        newl = [w]
                        bullet = False
        else:
            if l.strip():
                indent = l.find(l.strip()[0])
            words = l.split()
            if not newl:
                newl = []
            for w in words:
                testline = join(newl + [w], ' ')
                use_indent = indent
                if not bullet:
                    use_indent = indent + 2
                if use_indent + len(testline) <= textwidth:
                    newl.append(w)
                else:
                    nl.append(' '*use_indent + join(newl, ' '))
                    newl = [w]
                    bullet = False


    print "====================================================================================="
    return nl

def test():
    """"""
    lines = """
    - docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test
    - docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test
    docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test docstring for test
    """.split("\n")
    for l in format(lines, 79):
        print l

if __name__ == "__main__":
    # test()
    from_vim()
from vim import *

def iexists(var):
    return int(eval("exists('%s')" % var))

exists = iexists

def exist_eval(var):
    if iexists(var): return eval(var)
    else: return None

def iexist_eval(var):
    x = exist_eval(var)
    return None if x==None else int(x)

def ieval(var):
    return int(eval(var))

def input(prompt='>', strip=True):
    i = eval("input('%s')" % prompt)
    return i.strip() if i else i

def edit(path):
    # print "path", path
    # print "fnescape(path)", fnescape(path)
    command("edit %s" % fnescape(path))

def expand(pattern):
    return eval("expand('%s')" % pattern)

def nextwin(arg=''):
    command("call NextWin(%s)" % arg)

def bufnr(pattern):
    return eval('bufnr("%s")' % pattern)

def buffer(bufnr):
    command("buffer %s" % bufnr)

def cursor(row_or_tup=None, col=None):
    if row_or_tup != None or col != None:
        x = row_or_tup if col==None else (row_or_tup, col)
        current.window.cursor = row_or_tup if col==None else (row_or_tup, col)
    else:
        return current.window.cursor

def col(n=None):
    return cursor()[1] if n==None else cursor(lnum(), n)

def bcursor(row_or_tup=None, col=None):
    """Get or set buffer cursor (starting with 0-index)."""
    if row_or_tup is None and  col is None:
        c = cursor()
        return c[0]-1, c[1]
    elif col is None:
        cursor(row_or_tup[0]+1, row_or_tup[1])
    else:
        cursor(row_or_tup+1, col)

def lnum(n=None):
    return cursor()[0] if n==None else cursor(n, col())

def blnum(n=None):
    """Get or set buffer line num (starting with 0-index)."""
    return lnum()-1 if n==None else lnum(n+1)

def indent(ln=None):
    if ln==None: ln = lnum()
    return int(eval("indent(%s)" % ln))

def setvar(k, v):
    command("set %s=%s" % (k, v))

def normal(cmd):
    command("normal! "+cmd)

def search(pat, flags=''):
    """Search for pattern. flags='b' to search backwards, returns 0 if not found."""
    if flags:
        flags = ", '%s'" % flags
    return int(eval("search('%s'%s)" % (pat, flags)))

def search_or_end(pat, flags=''):
    """Search for `pat`, if not found, go to end of file (or beginning if searching backwards)."""
    flags += 'W'
    rc = search(pat, flags)
    if not rc:
        normal("gg" if 'b' in flags else 'G')
    return rc

def nwsearch(pat, flags=''):
    """No-wrap search."""
    # go to end or beginning of line to ensure we start searching from next line
    if not flags : normal('$')
    else         : normal('0')
    return search(pat, flags+'W')

def let(var, val):
    command('let %s = "%s"' % (var, str(val)))

def bufappend(*args):
    current.buffer.append(*args)

def getc():
    """Get char at cursor location."""
    return current.line[col()]

def wincmd(cmd):
    command("wincmd " + cmd)

def fnescape(fn):
    return eval("fnameescape('%s')" % fn)

def bufloaded(bufname):
    return ieval("bufloaded('%s')" % fnescape(bufname))

def mode(expr=0):
    """Return full mode name if `expr`=1; usually returns 'n' or 'c'."""
    return eval("mode(%d)" % expr)

def nextnonblank(lnum):
    return eval("nextnonblank(%s)" % lnum)

def prevnonblank(lnum):
    return eval("prevnonblank(%s)" % lnum)

def pumvisible():
    return eval("pumvisible()")

def winline():
    """Screen line of cursor in the window, first line returns 1."""
    return int(eval("winline()"))

def lastwinnr():
    """Number of last accessed window."""
    return int(eval("winnr('#')"))

def buflist(tabnum=None):
    """List of buffer numbers in tabpage `tabnum`."""
    return eval("tabpagebuflist(%s)" % ('' if tabnum==None else tabnum))

def buflisted(expr):
    """Is buffer 'listed' (shows up in :ls)?"""
    return int(eval("buflisted(%s)" % expr))

def up(n=1):
    normal("%dk" % n)

def down(n=1):
    normal("%dj" % n)
#!/usr/bin/env python
""" Vim interactive help.
"""

import re

test_txt = """
==============================================================================
1. Deleting text					*deleting* *E470*

["x]<Del>	or					*<Del>* *x* *dl*
["x]x			Delete [count] characters under and after the cursor
			[into register x] (not |linewise|).  Does the same as
			"dl".
			The <Del> key does not take a [count].  Instead, it
			deletes the last character of the count.
			See |:fixdel| if the <Del> key does not do what you
			want.  See |'whichwrap'| for deleting a line break
			(join lines).  {Vi does not support <Del>}

							*X* *dh*
["x]X			Delete [count] characters before the cursor [into
			register x] (not |linewise|).  Does the same as "dh".
			Also see |'whichwrap'|.

"""

def main():
    fn = "change.txt"
    txt = open(fn).read()
    process_text(txt)

def process_text(txt):
    sections = txt.split('='*78 + '\n')[1:]
    for section in sections:
        l1, section = section.split('\n', 1)
        sname, stags = l1.split('\t', 1)
        sname = sname.split('.')[1].strip()
        stags = stags.strip().split()
        stags = [t[1:-1] for t in stags]
        print "section: ", repr(section)
        indexes = re.finditer(r"\n [^\n]+ \* [a-zA-Z0-9_]+ \* \n", section, re.VERBOSE)
        for ind in indexes:
            print "ind: ", ind
            print "ind.start(): ", ind.start()
    print '='*20 + '\n'

def test():
    """Test."""
    process_text(test_txt)


if __name__ == '__main__':
    test()
    # main()
# vim: set fileencoding=utf-8 :

# Imports {{{
import os
import sys
import time
import shutil
from string import join
from os import sep, listdir
from os.path import dirname, isdir, expanduser, join as pjoin

from vim import *

# note: can't use __name__ in vim!!?
sys.path.append(expanduser("~/.vim/python/"))
import genpydoc
import util
from util import *

# if there is an error in a module, it's not auto-reloaded after the error is fixed..
reload(util)
reload(genpydoc)

programs = dict(py="python", sh="bash", html="firefox")
# }}}


def togglewin():
    """Toggle project window on/off."""
    cols = ieval("&columns")
    proj_width = 27
    splitright = eval("&splitright")
    let("&splitright", 1)

    # try to find project win
    for w in windows:
        if w.buffer.name.endswith(".proj"):
            if w.width == cols:
                # split into project / main areas
                command("vsplit")
                w.width = proj_width
            else:
                # toggle project win off
                let("s:last_proj", w.buffer.name)
                wwidth = w.width
                wincmd("h")
                wincmd("c")
                let("&columns", cols-wwidth)
            return

    # toggle project win on
    let("&columns", cols+proj_width)
    command("vsplit")
    wincmd("h")
    wincmd("j")
    current.window.width = proj_width
    lp = exist_eval("s:last_proj")
    if lp:
        command("buffer " + lp)
    else:
        for b in buffers:
            if b.name.endswith(".proj"):
                command("buffer " + b.name)
                break
    let("&splitright", splitright)

def grepall():
    """Grep all files in a project or dir, depending on where cursor is."""
    filelst = filelist()
    nextwin()
    pat = input("pattern:")
    if pat:
        try:
            command("vimgrep %s %s" % (pat, join(filelst)))
        except error:
            pass  # print "Not Found"

def filelist():
    """Open all files in a project or dir, depending on where cursor is."""
    filelst = []
    ldir = lproj = dirname = False
    s = ''
    l = current.line.strip()

    # find out if cursor on dir name or project name
    if l and (l[0] in '~'+sep or l.endswith(sep)):
        if l[0] not in '~'+sep:
            l = pjoin(headpath, l)  # relative path
        ldir = True
        dirname = l
    elif l.startswith("---"):
        lproj = True
    else:
        return []

    # loop over lines and add files
    for l in current.buffer[lnum():]:
        l = l.strip()

        if ldir and (l and l[0] in '~'+sep):
            # finished directory
            break
        elif not l or l.startswith('#'):
            # blank lines & comments are allowed everywhere
            continue
        elif l[0] in '~'+sep:
            # new directory
            dirname = l
        elif l.startswith("---"):
            # finished project
            break
        else:
            if dirname and l:
                if not isdir(expanduser(dirname)):
                    print "Error: missing directory (%s)" % dirname
                    time.sleep(1.5)
                    return []
                filelst.append(pjoin(dirname, l))

    return filelst

def openall():
    filelst = filelist()
    nextwin()
    for fn in filelst: edit(fn)

def fileop(mode):
    """Copy / rename / delete file."""
    b = current.buffer
    ln = orig = lnum()
    headpath = expand("%:h")
    name = l = current.line.strip()
    if not l or (l[0] in '~'+sep or l.endswith(sep) or l.startswith("--- ")):
        return

    # search upwards for directory and copy file
    while 1:
        if not ln: return
        ln -= 1
        l = b[ln].strip()
        if l and (l[0] in '~'+sep or l.endswith(sep)):
            if l[0] not in '~'+sep:
                l = pjoin(headpath, l)  # relative path

            if mode != "delete":
                to = input("New file name: ")
            else:
                if input("Delete file from disk? [y/n] ") not in 'Yy':
                    return

            if mode == "delete" or to:
                l = expanduser(l)
                fn = pjoin(l, name)
                if mode == "copy":
                    shutil.copy(fn, pjoin(l, to))
                    b.append(["  " + to], orig)
                elif mode == "rename":
                    b[orig-1] = "  " + to
                    os.rename(fn, pjoin(l, to))
                elif mode == "delete":
                    del b[orig-1]
                    os.remove(fn)
            return

def openfile(run=False, switch_to=True):
    """Open or run a file."""
    name, b = current.line.strip(), current.buffer
    ln = lnum()
    headpath = expand("%:h")

    # open a directory?
    if name and (name[0] in '~'+sep or name.endswith(sep)):
        if name[0] not in '~'+sep:
            name = pjoin(headpath, name)    # relative path
        nextwin()

        if int(exist_eval("g:loaded_nerd_tree")):
            edit(name)
        else:
            command("browse edit %s" % name)
        return

    # search upwards for directory and open or run file
    while 1:
        if not ln: return
        ln -= 1
        l = b[ln].strip()
        if l and (l[0] in '~'+sep or l.endswith(sep)):

            if l[0] not in '~'+sep:
                l = pjoin(headpath, l)  # relative path

            ext = name.split('.')[-1]
            if ext in programs and run:
                command(":!%s %s" % (programs[ext], pjoin(l, name)))
            else:
                # if len(buffers) == 1 or (ieval("g:pysuite_tabbar") and len(buffers)==2):
                if len(buffers) == 1:
                    # open first file after starting vim
                    splitright = eval("&splitright")
                    let("&splitright", 0)
                    command("vsplit")
                    current.window.width = 23
                    wincmd('l')
                    edit(pjoin(l, name))
                    let("&splitright", splitright)
                else:
                    normal("mvH")
                    wincmd('l')
                    # '1' arg skips todo and trak buffers; we may end up loading into proj buffer if
                    # only proj, todo and trak buffers exist - that's bad but should be v. rare
                    # nextwin(1)
                    edit(pjoin(l, name))
                    if not switch_to:
                        wincmd('h')
                        command("'v")
            return

def cur_fname():
    """Unused?!"""
    ln = lnum()
    while 1:
        if not ln: return
        ln -= 1
        l = current.buffer[ln].strip()
        if l[0] in '~'+sep:
            return l

def unload_all():
    """Unload (:bdelete) all files in a project or dir, depending on where cursor is."""
    filelst = filelist()
    if not filelst:
        l = current.line.strip()
        if l and not l.startswith('#'):
            filelst = [l]

    if not filelst: return

    # make list of all listed buffers
    bnames = [b.name for b in buffers if b.name and not b.name.endswith(".proj")]
    tmp = [x.split('/')[-1] for x in bnames]

    bnums = []
    for bn in bnames:
        try: bnums.append(bufnr(bn))
        except: continue
    bnums = [ b for b in bnums if (ieval("buflisted(%s)" % b) > 0) ]
    project_buf = eval(bufnr('%'))
    nextwin()
    currb = eval(bufnr('%'))

    # make list of buf numbers we need to unload
    flbnums = []
    for bn in filelst:
        try: flbnums.append(bufnr(bn))
        except: continue

    flbnums = [n for n in flbnums if n != '-1']

    # If current buffer needs to be unloaded, we need to switch to some other buffer
    # to preserve windows layout.
    switch_to = None
    for bn in bnums:
        if bn not in flbnums:
            switch_to = bn
            break

    # unload buffers
    for fn in filelst:
        try:
            bnr = bufnr(expanduser(fn))
        except:
            continue
        if ieval("buflisted(%s)" % bnr):
            buffer(bnr)
            if not ieval("&modified"):
                if switch_to:
                    buffer(switch_to)
                else:
                    command("bnext")

                try: command("bdelete %s" % bnr)
                except: pass
            else:
                print "'%s' has unsaved changes" % fn

    # try to switch to original buffer; go back to project window
    if currb not in flbnums:
        buffer(currb)
    wincmd('h')

def addall():
    """Add all files to current dir."""
    def flt(fn, dirname):
        if fn.startswith('.'):
            return False
        elif isdir(pjoin(dirname, fn)):
            return False

        for end in ".pyc .swp .swo".split():
            if fn.endswith(end):
                return False
        return True

    l = current.line
    if l and l[0] in "~"+sep:
        l = expanduser(l)
        lst = ["  " + fn for fn in listdir(l) if flt(fn, l)]
        if lst:
            lst.sort()
            current.buffer.append(lst, lnum())
            normal("j0")
        else:
            print "No files in " + l


def getcwd():
    """Insert current working directory in project buffer."""
    current.buffer.append( eval("getcwd()"), lnum() )
    normal("j0")


# if __name__ == "__main__" {{{
if __name__ == "__main__":
    val = exist_eval("a:1")
    genpd = genpydoc.GenPyDoc()
    lst = filelist()
    if val:
        if   val == "genpydoc"            : genpd.genpydoc(lst)
        elif val == "genpydoc_html"       : genpd.genpydoc(lst, "html")
        elif val == "genpydoc_html_nodoc" : genpd.genpydoc(lst, "html", docstrings=False)
        elif val == "genpydoc_potl"       : genpd.genpydoc(lst, "potl")
        elif val == "genpydoc_potl_nodoc" : genpd.genpydoc(lst, "potl", docstrings=False)

        elif val == "grepall"    : grepall()
        elif val == "openall"    : openall()
        elif val == "open_switch": openfile()
        elif val == "open"       : openfile(run=False, switch_to=False)
        elif val == "open_run"   : openfile(run=True)
        elif val == "unload_all" : unload_all()
        elif val == "addall"     : addall()
        elif val == "getcwd"     : getcwd()
        elif val == "copy"       : fileop("copy")
        elif val == "rename"     : fileop("rename")
        elif val == "delete"     : fileop("delete")
        elif val == "togglewin"  : togglewin()
# }}}
""" Vimp3 Player. """

import os
from time import sleep, time
from os.path import join as pjoin
from string import join
import socket
import commands
from vim import *

HOST, PORT = '', 12347


def play_curline():
    """Play track in current line."""
    if current.line.endswith(']'):
        clear_ind()
        cmd("play_lnum %d" % (current.window.cursor[0] - 1))
        let("mode", "play")
        info()

def make_playlist():
    """Send current playlist to server and play current line's track."""
    b = current.buffer
    lnum = orig = current.window.cursor[0] - 1
    root = eval("s:root")
    files = []
    ind = 0
    let("bufname", b.name)

    while 1:
        l = b[lnum].strip()
        if l.startswith("---"):
            let("playlist", l.strip("- "))
            break
        lnum -= 1
    lnum += 1

    # add files; remove old markers & add current
    dirname = None
    while 1:
        if lnum >= len(b): break
        l = b[lnum].strip()
        if l.startswith("---"): break

        if l:
            if l.endswith('/'):
                dirname = l
                lnum += 1
                continue

            if l.startswith("> "):
                b[lnum] = ' ' + l[1:]

            if not dirname:
                print "Error in playlist format, dir name missing, lnum, l:", lnum, l
                lnum += 1
                return

            fn = l.lstrip('>').strip()
            if dirname != '/' and '/' not in fn:
                # if file is not a complete path and not in root
                fn = pjoin(dirname, fn)

            files.append(str(lnum) + '\n' + fn)
            if lnum == orig:
                ind = len(files) - 1
                b[lnum] = '>' + b[lnum][1:]
        lnum += 1

    cmd("make_playlist %d\n\n%s\n\n%s" % (ind, root, join(files, "\n\n")))

    random(eval("s:random"), True)
    repeat(eval("s:repeat"), True)

def clear_ind():
    """Clear old indicator before jumping to new track."""
    oldlnum = int(eval("s:cur_lnum"))
    if oldlnum >= 0:
        bname = eval("s:bufname")
        vimp3buf = None

        # find vimp3 buffer
        for b in buffers:
            if b.name == bname:
                vimp3buf = b
                break

        if not vimp3buf: return
        vimp3buf[oldlnum] = ' ' + vimp3buf[oldlnum][1:]

def prev():
    """Previous track."""
    clear_ind()
    cmd("prev")
    info(True)

def next():
    """Next track, decrease score of current if we skipped before 80% of track."""
    clear_ind()
    last_start = int(eval("s:last_start"))
    if last_start:
        # let("last_track", eval("s:current"))
        elapsed = time() - last_start
        length = int(eval("s:length_sec"))
        if float(elapsed) / length < 0.8:
            command("call add(s:decr_score, s:cur_lnum)")
    cmd("next")
    info(True)
    print "cur_lnum", eval("s:cur_lnum")

def jump_current():
    """Jump to current track."""
    cur = current.window.cursor[0]
    lnum = int(eval("s:cur_lnum"))
    if lnum >= 0 and abs(cur - lnum) > 3:
        current.window.cursor = (lnum+1, 2)
        command("normal zz")

def update_current(oldlnum, lnum, incr_score):
    """Update current file in playlist buffer."""
    root = eval("s:root")
    bname = eval("s:bufname")
    vimp3buf = None

    # find vimp3 buffer
    for b in buffers:
        if b.name == bname:
            vimp3buf = b
            break

    if not vimp3buf: return

    l = vimp3buf[oldlnum]
    vimp3buf[oldlnum] = ' ' + l[1:]

    l = vimp3buf[lnum]
    vimp3buf[lnum] = '>' + l[1:]

    decr_score = eval("s:decr_score")
    change_score = int(eval("s:change_score"))
    for mod, lst in ((change_score, incr_score), (-change_score, decr_score)):
        for ln in lst:
            l = vimp3buf[int(ln)].rstrip()
            s = l[-5:].strip(" []")
            try:
                s = int(s)
            except:
                print "No score found in line: ", l
                continue
            new = s + mod
            if new < 0: new = 0
            elif new > 100: new = 100
            vimp3buf[int(ln)] = l[:-5].rstrip() + "  [%s]" % new

    command("let s:decr_score = []")
    let("cur_lnum", lnum)
    if int(eval("s:follow_current")) and current.buffer == vimp3buf:
        jump_current()

def cur_score(incr):
    """Add or subtract score for track on current line. (Not currently playing track!)"""
    l = current.line.rstrip()
    if l.endswith(']'):
        change_score = int(eval("s:change_score"))
        mod = -change_score
        if incr: mod = change_score

        s = int(l[-5:].strip(" []"))
        new = s + mod
        if new < 0: new = 0
        elif new > 100: new = 100

        current.line = l[:-5].rstrip() + "  [%s]" % new

def toggle_random():
    """Random on/off."""
    modes = ["off", "on"]
    if eval("s:random") == modes[0]: random(modes[1])
    else: random(modes[0])

def toggle_repeat():
    """Repeat on/off."""
    modes = ["off", "track", "playlist"]
    m = eval("s:repeat")
    if   m == modes[0]: repeat(modes[1])
    elif m == modes[1]: repeat(modes[2])
    else:               repeat(modes[0])

def repeat(mode, quiet=False):
    """Set repeat mode, by default print mode in command line."""
    cmd("repeat " + mode)
    let("repeat", mode)
    if not quiet: print "repeat " + mode

def random(mode, quiet=False):
    """Set random mode, by default print mode in command line."""
    cmd("random " + mode)
    let("random", mode)
    if not quiet: print "random " + mode

def pause():
    """Toggle pause."""
    if eval("s:mode") == "pause": let("mode", "play")
    else: let("mode", "pause")
    cmd("pause")

def quit():
    """Make server quit, same as ctrl-c in server terminal."""
    cmd("quit")

def toggle_play():
    """Toggle between play and stop, this is different from pause!"""
    if eval("s:mode") == "play": let("mode", "stop")
    else: let("mode", "play")
    cmd("toggle_play")

def btpause():
    """ Pause between tracks, server returns elapsed pause time instead of elapsed track time while the
        pause is on.
    """
    btp = eval("input('Between tracks pause (sec): ')")
    try:
        cmd("btpause %d" % int(btp))
        let("btpause", btp)
    except:
        print "btpause(): invalid input", btp

def add_dir(ask=False):
    """Add tracks from current dir, recursively."""
    lnum = current.window.cursor[0]
    lst = []
    root = eval("s:root")
    if ask: scanroot = eval("input('Full path: ')")
    else: scanroot = os.getcwd()

    if not scanroot.startswith(root.rstrip('/')):
        print "Error: run 'add dir' command in music root directory:", root
        return

    for (dirpath, dirnames, filenames) in os.walk(scanroot):
        added = False
        filenames.sort()
        tracks = []
        for fn in filenames:
            if fn.endswith(".mp3") or fn.endswith(".ogg") or fn.endswith(".flac") or fn.endswith(".wma"):
                tracks.append("  %s  [35]" % fn)
                added = True
        if added:
            lst.append(dirpath.replace(root, '') + '/')
            lst.extend(tracks)
            lst.append('')          # empty line after each dir

    current.buffer[lnum:lnum] = lst

def info(force_upd_current=False):
    """ Get status from server. `force_upd_current` is used when doing next() on last file, next() clears
        indicator and we need update_current() to run to recreate indicator on that line."""
    val = None
    s = connect()
    if s:
        for x in range(20):
            try: s.settimeout(1); s.send("info"); val = s.recv(1024); s.close()
            except: pass
        if val:
            last_start, length, index, current, lnum, incr_score = val.split(";;")
            oldlnum = eval("s:cur_lnum")
            lnum = lnum
            if oldlnum != lnum or force_upd_current:
                update_current(int(oldlnum), int(lnum), eval(incr_score))

            length = int(length)
            let("length_sec", length)
            let("length", "%d:%02d" % (length/60, length%60))
            let("last_start", int(last_start))
            let("current", current)

def status():
    """Print current settings."""
    print "mode [%s] repeat [%s] random [%s] btpause [%s]" % (eval("s:mode"),
        eval("s:repeat"), eval("s:random"), eval("s:btpause"))

#==- Utility functions -=========================================================================


def let(var, val):
    command('let s:%s = "%s"' % (var, str(val)))

def cmd(c):
    s = connect(); s.send(c); s.close()

def iexists(var):
    """If var exists => 1, otherwise 0."""
    return int(eval("exists('%s')" % var))

def exist_eval(var):
    if iexists(var): return eval(var)
    else: return None

def search(pat, d=1):
    """Search for pattern. d=-1 to search backwards, returns 0 if not found."""
    if d == 1: return int(eval("search('%s')" % pat))
    else:      return int(eval("search('%s', 'b')" % pat))

def connect():
    """Connect to server, print error if can't."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except socket.error, e:
        print "Error connecting to the server", e
        return None
    return s


if __name__ == '__main__':
    arg = exist_eval("a:1")
    if arg:
        if   arg == "play_current": play_curline()
        elif arg == "toggle_play": toggle_play()
        elif arg == "next": next()
        elif arg == "prev": prev()
        elif arg == "stop": cmd("stop")
        elif arg == "quit": quit()
        elif arg == "pause": pause()
        elif arg == "add_dir": add_dir()
        elif arg == "add_dir_ask": add_dir(1)
        elif arg == "info": info()
        elif arg == "update_info": update_info()
        elif arg == "repeat_off": repeat("off")
        elif arg == "repeat_track": repeat("track")
        elif arg == "repeat_playlist": repeat("playlist")
        elif arg == "random_off": random("off")
        elif arg == "random_on": random("on")
        elif arg == "toggle_repeat": toggle_repeat()
        elif arg == "toggle_random": toggle_random()
        elif arg == "btpause": btpause()
        elif arg == "jump_current": jump_current()
        elif arg == "score incr": cur_score(1)
        elif arg == "score decr": cur_score(0)
        elif arg == "status": status()
        elif arg == "make_playlist": make_playlist()
        elif arg == "seek 10":
            ls = int(exist_eval("s:last_start"))
            if ls: let("last_start", ls-10)
            cmd("seek 10")
        elif arg == "seek -10":
            ls = int(exist_eval("s:last_start"))
            if ls: let("last_start", ls+10)
            cmd("seek -10")
        elif arg == "vol +":
            os.system("aumix -v+"+eval("s:vol_incr"))
            print commands.getoutput("aumix -vq")
        elif arg == "vol -":
            os.system("aumix -v-"+eval("s:vol_incr"))
            print commands.getoutput("aumix -vq")
        else:
            print "Unknown arg:", arg
#!/usr/bin/env python
import os, sys
import socket
from subprocess import PIPE, Popen
from threading import Thread
from time import sleep, time
from random import randint, choice
from string import join
from signal import *

HOST, PORT = '', 12347
mode = "stop"
repeat_mode = random_mode = "off"
last_start = index = btpause = length = 0
current = ''
waiting = False
loop_int = 0.1
seek = 0
scorelist = []
incr_score = []
for x in range(10):
    scorelist.extend(range(x*10, (x+1)*10)*(x+1))


def read_len(p):
    global length
    while 1:
        l = p.stdout.readline().strip()
        if l.startswith("ANS_LENGTH"):
            length = int(float(l.split('=')[1]))
            return

def start_mp(fn):
    """Create mplayer pipe."""
    # fn = fn.replace('&', '\&').replace('[', '\[').replace(']', '\]')
    p = Popen(["mplayer", "-slave", "-quiet", fn], stdin=PIPE, stdout=PIPE)
    p.stdin.write("get_time_length\n")
    Thread(target=read_len, args=(p,)).start()
    return p

def play(playlist, force_ind=False):
    """ Thread that plays the tracks. `force_ind` is to play the specified file when random mode
        is on, e.g. by clicking on it vs. using next command."""
    global mode, last_start, current, index, waiting, length, seek
    btwait = 0
    waiting = False
    if index >= len(playlist): return

    if random_mode == "on" and not force_ind:   # see docstring
        for x in range(1000):
            index = randint(0, len(playlist) - 1)
            track = playlist[index]
            if track[1] >= choice(scorelist):
                break
    else:
        track = playlist[index]

    last_start, current = time(), track[0]
    p = start_mp(track[0])

    while 1:
        if mode == "stop":
            last_start = 0
            p.kill()
            return
        elif mode == "pause":
            print "writing 'pause' to stdin"
            p.stdin.write("pause\n")
            mode = "paused"
        elif mode == "resume":
            p.stdin.write("pause\n")
            mode = "play"
        elif seek:
            p.stdin.write("seek %d\n" % seek)
            seek = 0
        elif p.poll() != None:
            # finished playing file
            lnum = playlist[index][2]
            if lnum not in incr_score:
                incr_score.append(lnum)

            # start btpause
            if mode == "play" and btpause and not waiting:
                btwait = btpause
                waiting = True
                last_start = time()
                current = "<btpause>"
                length = btpause
                continue

            # wait for btpause to end
            if btwait > 0:
                btwait -= loop_int
                sleep(loop_int)
                continue
            elif waiting:
                waiting = False


            if repeat_mode != "track":
                if random_mode == "on":
                    for x in range(1000):
                        index = randint(0, len(playlist) - 1)
                        track = playlist[index]
                        if track[1] >= choice(scorelist):
                            break
                else:
                    index += 1
                    track = playlist[index]

                    if index >= len(playlist):
                        if repeat_mode == "playlist":
                            index = 0
                        else:
                            mode = "stop"
                            return

            last_start, current = time(), track[0]

            if mode == "play": p = start_mp(track[0])
        if mode == "paused": last_start += loop_int
        sleep(loop_int)

class Player:
    def __init__(self):
        self.playlist = []

    def main(self):
        """Bind to port and start main loop for getting one command at a time."""
        rc = None
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        while 1:
            conn = None
            s.listen(1)
            try:
                conn, addr = s.accept()
                rc = self.player(conn, addr)
            except KeyboardInterrupt:
                rc = 1
            except Exception, e:
                print "e: ", e

            if conn: conn.close()

            if rc == 1:
                s.shutdown(socket.SHUT_RDWR); s.close(); del s
                self.quit()

    def player(self, conn, addr):
        """Command loop."""
        global mode
        mkplst_cmd = ''
        while 1:
            cmd = conn.recv(1000000)
            # if cmd: print "cmd: ", cmd
            if cmd.startswith("play_lnum"): self.play_lnum(cmd); break
            elif cmd.startswith("repeat"):  self.repeat_mode(cmd); break
            elif cmd.startswith("random"):  self.random_mode(cmd); break
            elif cmd.startswith("btpause"): self.btpause(cmd); break
            elif cmd.startswith("seek"):    self.seek(cmd); break
            elif cmd == "toggle_play":      self.toggle_play(); break
            elif cmd == "next":             self.next(); break
            elif cmd == "prev":             self.prev(); break
            elif cmd == "pause":            self.toggle_pause(); break
            elif cmd == "info":             self.info(conn); break
            elif cmd == "quit":             return 1
            elif cmd.startswith("make_playlist") or mkplst_cmd:
                if cmd:
                    mkplst_cmd += cmd
                else:
                    self.make_playlist(mkplst_cmd)
                    break

            sleep(0.1)

    def info(self, conn):
        global incr_score
        txt = "%d;;%s;;%s;;%s;;%s;;%s" % (last_start, length, index, current, self.playlist[index][2],
                 incr_score)
        conn.send(txt)
        incr_score = []
        sleep(0.1)

    def quit(self):
        """Stop thread & quit."""
        self.stop()
        sleep(0.02)
        sys.exit()

    def toggle_pause(self):
        """Toggle pause."""
        global mode
        if mode == "paused": mode = "resume"
        else: mode = "pause"

    def prev(self):
        """Prev track. random is handled in play thread."""
        global index
        index -= 1
        if index < 0: index = len(self.playlist)
        self.play()

    def next(self):
        """Next track. random is handled in play thread."""
        global index
        index += 1
        if index >= len(self.playlist):
            if repeat_mode == "playlist":
                index = 0
            else:
                index = len(self.playlist) - 1
                self.stop()
                return
        self.play()

    def stop(self):
        global mode
        mode = "stop"
        sleep(loop_int + 0.01)

    def play(self, force_ind=False):
        """Force_ind overrides random mode to play current index."""
        global mode
        self.stop()
        mode = "play"
        Thread(target=play, args=(self.playlist, force_ind)).start()

    def seek(self, cmd):
        """Seek ahead or back."""
        global seek, last_start
        seek = int(cmd.split()[1])
        if last_start:
            last_start -= seek

    def btpause(self, cmd):
        """Pause between tracks for N seconds."""
        global btpause
        btpause = int(cmd.split()[1])

    def random_mode(self, cmd):
        """On/off."""
        global random_mode
        random_mode = cmd.split()[1]

    def repeat_mode(self, cmd):
        """Off/track/playlist."""
        global repeat_mode
        repeat_mode = cmd.split()[1]

    def toggle_play(self):
        """Play / Stop."""
        if mode == "play": self.stop()
        else: self.play()

    def make_playlist(self, data):
        """Add specified tracks to playlist & play."""
        global index
        data = data[14:].split("\n\n")
        index, root, fns = int(data[0]), data[1], data[2:]
        # plst = [root + fn for fn in fns]
        self.playlist = []
        self.lnums = {}
        for n, fn in enumerate(fns):
            lnum, fn = fn.split('\n')
            fn = fn.split()
            self.lnums[lnum] = n
            self.playlist.append( (root + join(fn[:-1]), int(fn[-1].strip("[]")), lnum) )

    def play_lnum(self, cmd):
        global index
        index = self.lnums[cmd.split()[1]]
        self.play(True)


if __name__ == '__main__':
    Player().main()
import os
import socket

def stop():
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((HOST, PORT))
    # s.send("stop")
    command("let g:vimp3_mode = 'stop'")
    os.system("killall mplayer")

if __name__ == '__main__':
    stop()
#!/usr/bin/env python2.6

# Imports {{{


"""vimtobu filter

Usage: vtobu_filter.py

Written by AK <ak@lightbird.net>
"""

import sys
from optparse import OptionParser
from string import join
from os.path import expanduser, join as pjoin
from time import sleep
flush = sys.stdout.flush
vimpython_dir = expanduser("~/.vim/python/")

from avkutil import Term

from django.conf import settings
try:
    settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,
                       DATABASE_ENGINE="django.db.backends.sqlite3",
                       DATABASE_NAME=pjoin(vimpython_dir, "vimtobu.db"),
                       INSTALLED_APPS=["vimtobu"])
except RuntimeError:
    pass

from vimtobu.models import *

sep = '='*78
max_matches = 80    # don't process over this many matches as they won't fit on the screen
min_pattern = 2     # start filtering when pattern is at least so many characters
menu_size = 40
choicefn = pjoin(vimpython_dir, "vimtobu_choice.tmp")
# }}}

class VTobuFilter:
    def __init__(self):
        self.matched = ''

    def main(self, ftype):
        """Main function."""
        self.t = Term()
        self.matches = []
        self.mdict = {}
        self.pat = ''
        self.i = None
        self.ftype = ftype
        while 1: self.ui()

    def process_key(self, c):
        """Process command key."""
        self.matched = ''

        # Enter
        if c == '\n':
            if self.ftype and self.pat:
                # not search, last viewed/edited/created
                if self.pat in self.mdict:
                    print "i in self.mdict"
                    self.write_choice(self.mdict[self.pat])
                else:
                    print "self.mdict", self.mdict
                sleep(0.7)

            elif self.i and self.i in self.mdict:
                self.write_choice(self.mdict[self.i])
            sys.exit()

        # Tab
        elif c == '\t':
            if self.pat:
                lw = self.pat.split()[-1]
                t = Tag.objects.filter(name__startswith=lw)
                if t and t.count() == 1:
                    self.pat = self.pat + t[0].name[len(lw):]
                elif t.count() > 1:
                    more = " .. (%d more)" % (t.count()-10) if t.count()>10 else ''
                    t = [unicode(tag) for tag in t]
                    add = ''
                    minlen = min([len(tag) for tag in t])

                    # expand pattern to longest common sequence in matches
                    for n in range(len(self.pat), 50):
                        if n >= minlen:
                            break
                        l = t[0][n]
                        if all([tag[n]==l for tag in t]):
                            add += l
                        else:
                            break

                    self.pat += add
                    self.matched = join(t, ", ") + more

        # Esc
        elif c == '\x1b':
            self.write_choice(0)
            sys.exit()

        # backspace in vim, konsole
        elif c in '\x08\x7f':
            self.pat = self.pat[:-1]
            self.matches = []

        # Ctrl-U
        elif c == '\x15':
            self.pat = ''
            self.matches = []
        else:
            self.pat += c

    def write_choice(self, choice):
        with open(choicefn, 'w') as fp:
            fp.write(str(choice))
        sys.exit()

    def get_min_pat(self):
        """ Loop until we have at least `min_pattern` characters in `self.pat`.

            (or we have a numeric choice that's in self.mdict).
        """
        while 1:
            prompt = ">" if self.ftype else "tags:"
            prompt = "\r%s %s" % (prompt, self.pat)

            # when BS key is pressed, we need to first overwrite the old character with a space,
            # then write just the prompt again to have cursor in the right place.
            print prompt + ' ',
            print prompt,
            flush()
            self.process_key(self.t.getch())

            if self.ftype:
                # not search, last viewed/edited/created
                try:
                    pat = self.pat.strip()
                    i = int(pat)
                    if (i > 10 or i and (len(self.mdict) < i*10)) and self.mdict and (pat in self.mdict):
                        self.write_choice(self.mdict[pat])
                except ValueError:
                    pass
            elif len(self.pat) >= min_pattern:
                break

    def make_menu(self, matches):
        menu = [(n+1, unicode(m)) for n, m in enumerate(matches)]
        return ["%2s)  %s" % tup for tup in menu]

    def ui(self):
        """UI."""
        placeholder   = "vtobu-blank-placeholder"
        matches = self.matches
        if self.ftype:
            # not search, last viewed/edited/created
            matches = Item.objects.all().exclude(title__startswith=placeholder, body='')
            matches = matches.order_by('-' + self.ftype)[:menu_size]
            print '\r' + join(self.make_menu(matches), '\n')
            for n, item in enumerate(matches):
                self.mdict[str(n+1)] = item.pk
        else:
            print "\n%s\n%s\n%s\n" % (sep, sep, self.matched),
            flush()

        self.matched = ''
        self.get_min_pat()

        # make a listing of matches and print it
        if self.pat:
            words = self.pat.split()
            tags = []
            i = None

            # parse num selection, parse tags and filter matches
            if words[-1].isdigit():
                i, words = int(words[-1]), words[:-1]
            for w in words:
                try: tags.append(Tag.objects.get(name=w))
                except Tag.DoesNotExist: pass
            if tags:
                matches = Item.objects.filter(tags__in=tags)

            if matches:
                n = matches.count()
                size = "  ----%s matches----" % n if n>menu_size else ''
                matches = matches[:max_matches]
                for n, m in enumerate(matches):
                    self.mdict[n+1] = m.pk

                if (i > 10 or i and (len(matches) < i*10)) and self.mdict and (i in self.mdict):
                    # e.g. #3 out of 8 items or #4 out of 35 items
                    self.write_choice(self.mdict[i])
                elif len(matches) == 1:
                    self.write_choice(matches[0].pk)
                self.i = i
                print "\r%s\n%s\n" % ( join(self.make_menu(matches), '\n'), size)
            else:
                print "\r\n----no matches found----"

# __main__: {{{
if __name__ == "__main__":
    parser = OptionParser()
    (options, args) = parser.parse_args()
    tf = VTobuFilter()
    arg = None
    if args:
        arg = args[0]
    if arg and arg not in "viewed created edited":
        print "arg should be: viewed or created or edited"
        sys.exit()
    try: tf.main(arg)
    except KeyboardInterrupt: sys.exit()
    except Exception, e:
        print e
        sleep(1.5)
        sys.exit()
# }}}
#!/usr/bin/env python
# Imports {{{
"""VimTobu by <andrei.avk@gmail.com>"""

import os
import sys
import re
import sqlite3
from time import sleep
from string import join
from os.path import expanduser, join as pjoin, exists as pexists
from tempfile import NamedTemporaryFile
vimpython_dir = expanduser("~/.vim/python/")
db_fname = pjoin(vimpython_dir, "vimtobu.db")

from django.conf import settings
try:
    if not "vtobu_conf_done" in globals():
        settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,
                           DATABASE_ENGINE="django.db.backends.sqlite3",
                           DATABASE_NAME=pjoin(vimpython_dir, "vimtobu.db"),
                           INSTALLED_APPS=["vimtobu"])
    vtobu_conf_done = True
except RuntimeError:
    pass
sys.path.append(vimpython_dir)
from vimtobu.models import *
from vim import *
from util import *

choicefn = pjoin(vimpython_dir, "vimtobu_choice.tmp")
addr = '', 12347
# }}}

class VimTobu:
    def create_db(self):
        """Not used."""
        if not pexists(db_fname):
            conn = sqlite3.connect(db_fname)
            self.cur = conn.cursor()
            self.cur.execute("""
                 CREATE TABLE "vimtobu_item" ("id" integer PRIMARY KEY  NOT NULL ,
                              "body" text NOT NULL ,"created" datetime NOT NULL ,
                              "viewed" datetime NOT NULL ,
                              "edited" datetime NOT NULL ,
                              "title" VARCHAR(40) NOT NULL  DEFAULT '' )""")

    def new(self):
        new = True if eval("&filetype") != "vimtobu" else False
        if new:
            command("new")
        else:
            self.save()
            bname = current.buffer.name

        edit(NamedTemporaryFile().name)
        command("set filetype=vimtobu")
        item = self.new_blank()
        current.buffer[:] = ["[%d] Title: " % item.pk, "Tags: "]
        self.mappings()
        let("b:vt_mode", "new")
        normal('$')
        if not new:
            command("bdelete " + fnescape(bname))

    def new_blank(self):
        """Create a new blank item with unique placeholder title."""
        placeholder   = "vtobu-blank-placeholder"
        blanks        = Item.objects.filter(title__startswith=placeholder)
        title_numbers = sorted([int(b.title[len(placeholder):]) for b in blanks])
        num           = title_numbers[-1] if title_numbers else 1
        return Item.objects.create(title="%s%d" % (placeholder, num), body='')

    def mappings(self):
        command("nnoremap <buffer> <c-s>      :call VimTobu('save')<CR>")
        command("nnoremap <buffer> <F4>       :call VimTobu('close')<CR>")
        command("inoremap <buffer> <m-5>      <esc>:call VimTobu('save')<CR>")
        command("command! Save                :call VimTobu('save')")
        command("nnoremap <buffer> <Leader>l  :call VimTobu('list')<CR>")
        command("nnoremap <buffer> <Leader>a  :call Potl('new_header')<CR>")
        command("nnoremap <buffer> <Leader>n  :Save<CR>:call VimTobu('new')<CR>")
        command("nnoremap <buffer> <Leader>f  :Save<CR>:call VimTobu('filter')<CR><CR>")
        command("nnoremap <buffer> <Leader>d  :Save<CR>:call VimTobu('duplicate')<CR>R")
        command("nnoremap <buffer> <Leader>D  :Save<CR>:call VimTobu('delete')<CR>")
        command("nnoremap <buffer> <Leader>v  :Save<CR>:call VimTobu('last_viewed')<CR><CR>")
        command("nnoremap <buffer> <Leader>c  :Save<CR>:call VimTobu('last_created')<CR><CR>")
        command("nnoremap <buffer> <Leader>e  :Save<CR>:call VimTobu('last_edited')<CR><CR>")
        command("nnoremap <buffer> <Leader>h  :call VimTobu('help')<CR>")

    def close(self):
        self.save()
        remains = ieval("&lines") - current.window.height
        # each window at least 2: wintab, above/below; +2 for ruler and cmdline
        if remains >= 6 : command("bdelete!")
        else            : command("call DelBuffer()")

    def last(self, fld):
        """View list of last items: `fld` = viewed | created | edited."""
        items = Item.objects.all().exclude(title='', body='').order_by('-' + fld)
        d = {}
        for n, i in enumerate(items[:40]):
            d[n+1] = i
            print "%2s) %s" % (n+1, i)
        num = input('>')
        if num and num.isdigit():
            if int(num) in d:
                self.save()
                self.edit( d[int(num)].pk )
        elif num == '':
            # Enter, load first item
            self.save()
            self.edit(d[1].pk)

    def edit(self, pk=None):
        title = ''
        if not pk:
            title = input("Title:")
            if not title: return
        try:
            kwargs = dict(pk=pk) if pk else dict(title=title)
            item = Item.objects.get(**kwargs)
        except Item.DoesNotExist:
            print "Item '%s' does not exist" % (title or pk)
            return
        buf = current.buffer

        taglst = [unicode(t) for t in item.tags.all()]
        if any([' ' in t for t in taglst]): j = ", "
        else: j = ' '

        l = [
             "[%d] Title: %s" % (item.pk, item.title),
             "Tags: " + join(taglst, j), ''
            ] + item.body.split('\n')
        buf[:] = [x.encode("utf-8") for x in l]
        let("b:vt_mode", "edit")
        let("b:vt_title", item.title)

        self.saveas(item.title + ".vtobu")
        command("nnoremap <buffer> <c-s>      :call VimTobu('save')<CR>")

    def saveas(self, title):
        """Save to temp filename `title`.vtobu"""
        bname = current.buffer.name
        if not title.startswith('/'): title = "/tmp/" + title
        command("silent saveas! " + fnescape(title))

        if current.buffer.name != bname:
            command("bdelete " + fnescape(bname))

    def delete(self):
        """Delete current item from database."""
        if input("Confirm delete item from database? [y/n]") in "Yy":
            buf = current.buffer
            itemid = self.parse_head(buf)[0]
            item = get_or_none(pk=itemid)
            if item:
                item.delete()
                item = self.new_blank()
                let("b:vt_mode", "new")
                self.saveas(NamedTemporaryFile().name)
                current.buffer[:] = ["[%d] Title: " % item.pk, "Tags: "]
                bcursor(0,6)
            else:
                print "Error: current item is not in db"

    def parse_head(self, buf):
        """Parse id, title and tags from buffer `buf`."""
        l = buf[0].split(' ', 1)
        itemid = l[0].strip("[]")
        title = l[1][7:].strip()

        tags = buf[1][6:].strip()
        tags = tags.split(", ") if ',' in tags else tags.split()
        tags = [Tag.objects.get_or_create(name=t)[0] for t in tags if t.strip()]
        return int(itemid), title, tags

    def save(self):
        if ieval("&modified") == 0:
            print "vimtobu: no changes in buffer"
            return

        buf = current.buffer
        if len(buf) < 4: return
        mode = exist_eval("b:vt_mode")

        error = None
        if not re.match(r"\[\d+\] Title: .*", buf[0]):
            error = "Error: first line should be of format '[id] Title: ..'"
        if not buf[1].startswith("Tag"):
            error = "Error: second line should start with 'Tag: '"
        if not mode:
            error = "Error: b:vt_mode is not set!"

        if buf[2].strip():
            error = "Error: 3rd line must be empty"
        if error:
            print error; return

        itemid, title, tags = self.parse_head(buf)
        body = join(buf[3:], '\n')
        otitle = exist_eval("b:vt_title")

        item = get_or_none(title=title)
        if item and item.pk != itemid:
            print "Item with this title already exists"
            return

        item = get_or_none(pk=itemid)
        item.title, item.body, item.tags = title, body, tags
        item.save()
        self.saveas(item.title + ".vtobu")
        print "'%s' %s" % (title, "saved" if mode=="new" else "updated")
        let("b:vt_title", title)

    def duplicate(self):
        # let("b:vt_mode", "new")
        item = self.new_blank()
        buf = current.buffer
        title = buf[0].split(' ', 1)[1]
        buf[0] = "[%d] %s" % (item.pk, title)
        self.saveas(NamedTemporaryFile().name)
        cursor(1, 10 + len(str(item.pk)))

    def list(self):
        for i in Item.objects.all()[:100]:
            t = i.title
            t = t[:35] + "..." if len(t)>35 else t
            print "%-38s :: %s" % (t, join([t.name for t in i.tags.all()], ", "))

    def filter(self, ftype=''):
        """ filter items and pick one to edit

            If ftype is not set, it's a normal filter, otherwise it's last
            viewed | created | edited  items.
        """
        # command("redir => s:rc")
        command("!%s %s" % (expanduser("~/.vim/python/vtobu_filter.py"), ftype))
        # command("redir END")
        # pk = eval("s:rc").strip().split()[-1]
        with open(choicefn) as fp:
            pk = fp.read()
        if pk.isdigit() and pk != '0': self.edit(pk)

    def help(self):
        print """
            VimTobu
            -------

        List                            ,l
        New                             ,n
        Edit                             Alt-v
        Save                             <C-S>
        Duplicate item                  ,d
        Filter                          ,f
        --------------------------------------
        Last viewed                     ,v
        Last created                    ,c
        Last edited                     ,e
        Delete from database            ,D
        Close / Open VimTobu buffer      <F4>
        Help                            ,h
        """

    def last_viewed(self)  : self.filter("viewed")
    def last_created(self) : self.filter("created")
    def last_edited(self)  : self.filter("edited")

def get_or_none(**kwargs):
    try                      : return Item.objects.get(**kwargs)
    except Item.DoesNotExist : return None

if __name__ == "__main__":
    val = exist_eval("a:1")
    if val:
        vt = VimTobu()
        getattr(vt, val)()
#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Imports {{{
"""VimTobu by <andrei.avk@gmail.com>"""

from __future__ import print_function, unicode_literals, division
import os
import sys
import re
import sqlite3
from json import dumps
from time import sleep
from string import join
from os.path import expanduser, join as pjoin, exists as pexists
from tempfile import NamedTemporaryFile
vimpython_dir = expanduser("~/.vim/python/")
db_fname = pjoin(vimpython_dir, "vimtobu.db")

from django.conf import settings
try:
    settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,
                       DATABASE_ENGINE="django.db.backends.sqlite3",
                       DATABASE_NAME=pjoin(vimpython_dir, "vimtobu.db"),
                       INSTALLED_APPS=["vimtobu"])
except RuntimeError:
    pass
sys.path.append(vimpython_dir)
from vimtobu.models import *
import vimtobu.models
reload(vimtobu.models)
from vim import *

from util import *
import util
reload(util) # if there is an error in a module, it's not auto-reloaded after the error is fixed..

choicefn = pjoin(vimpython_dir, "vimtobu_choice.tmp")
ADDR = '', 12347
# }}}

class VimTobu:
    def main(self):
        """Bind to port and start main loop for getting one command at a time."""
        rc = None
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(ADDR)
        while 1:
            conn = None
            s.listen(1)
            try:
                conn, addr = s.accept()
                rc = self.player(conn, addr)
            except KeyboardInterrupt:
                rc = 1
            except Exception, e:
                print "e: ", e

            if conn: conn.close()

            if rc == 1:
                s.shutdown(socket.SHUT_RDWR); s.close(); del s
                sys.exit()

    def player(self, conn, addr):
        """Command loop."""
        while 1:
            cmd = conn.recv(1000000)
            if   cmd.startswith("last")      : self.last(cmd.split()[1]); break
            elif cmd.startswith("get_pk")    : self.get(pk=cmd.split()[1]); break
            elif cmd.startswith("get_title") : self.get(title=cmd.split()[1]); break
            elif cmd.startswith("delete")    : self.delete(cmd.split()[1]); break
            elif cmd.startswith("save")      : self.save(cmd); break

    def last(self, fld):
        """View list of last items: `fld` = viewed | created | edited."""
        items = Item.objects.all().exclude(title='', body='').order_by('-' + fld)
        # d = {}
        # for i in items[:40]:
            # d[i.pk] = str(i)
        d = {i.pk: str(i) for i in items[:40]}
        return dumps(d)

    def get(self, pk=None, title=None):
        try:
            kwargs = dict(pk=pk) if pk else dict(title=title)
            i = Item.objects.get(**kwargs)
            return dumps((i.pk, i.title, i.tags, i.body))
        except Item.DoesNotExist:
            return dumps(None)

    def delete(self, pk):
        """Delete item from database."""
        item = get_or_none(pk=pk)
        if item: item.delete()

    def save(self, pk, title, body, tags):
    def save(self, cmd):
        item = get_or_none(pk=pk)
        item.title, item.body, item.tags = title, body, tags
        item.save()


def get_or_none(**kwargs):
    try:
        return Item.objects.get(**kwargs)
    except:
        return None

if __name__ == "__main__":
    val = exist_eval("a:1")
    if val:
        vt = VimTobu()
        getattr(vt, val)()
import re
from time import *
from string import join
from copy import deepcopy
from os.path import expanduser
from vim import *

sys.path.append(expanduser("~/.vim/python/"))
from util import *
import util
reload(util) # if there is an error in a module, it's not auto-reloaded after the error is fixed..

leftmargin = 1


class Sort:
    """ Sort todo item list. By default, sorting is by priority, to sort by a different header,
        cursor should be positioned on the header and sort command activated.
    """
    def cmp1(self, a, b):
        """Compare two items, used by sort, can compare numbers, alphanumeric or dates."""
        a, b = a[self.index], b[self.index]
        if self.index in (2,3,4):
            a, b = int(a), int(b)
        elif self.index == 6:
            try:
                a = strptime(a, "%a %b %d")
                b = strptime(b, "%a %b %d")
            except:
                pass
        return cmp(a, b)

    def sort(self):
        # find out what to sort by
        headers = tuple(eval("s:headers").split())
        self.index = 2                        # header to sort by
        cword = eval("expand('<cword>')")     # word under cursor
        pos = cursor()
        b = current.buffer
        if cword in headers:
            self.index = headers.index(cword)

        # parse the task list
        tasks = []
        maxl1 = 4    # task and project name max widths
        maxl2 = 7
        for l in b[2:]:
            if l.strip():
                flds = [fld.strip() for fld in re.split("\s\s+", l)]
                if len(flds) not in (6,7):
                    print "Error: wrong number of fields in line: %s" % l
                    return
                if len(flds) == 6:
                    flds.insert(1, '')   # no project
                maxl1 = max(maxl1, len(flds[0]))
                maxl2 = max(maxl2, len(flds[1]))
                tasks.append(flds)
        maxl1 += 3
        maxl2 += 2

        # separate Done, OnHold and sort the rest
        done   = [t for t in tasks if t[4] == "100"]
        onhold = [t for t in tasks if  (t[5].lower() == "yes")  and  (t[4] != "100")]
        tasks  = [t for t in tasks if  (t[4] != "100")  and  (t[5].lower() != "yes")]

        # sort in asc order; if was sorted, sort in desc order
        was_sorted = True
        for t in (done, onhold, tasks):
            original = deepcopy(t)
            t.sort(cmp=self.cmp1)
            if t != original: was_sorted = False

        if was_sorted:
            for t in (done, onhold, tasks):
                t.sort(cmp=self.cmp1, reverse=True)

        # make line template, insert headers, tasks, OnHold and Done
        divlen = maxl1 + maxl2 + 40 + leftmargin     # divider line
        fldtpl = ' '* leftmargin + "%%-%ds%%-%ds" % (maxl1, maxl2) + "%-10s%-6s%-6s%-8s%s"
        b[:] = ([fldtpl % headers, '-'*divlen] +
                [fldtpl % tuple(t) for t in tasks] + [''] +
                [fldtpl % tuple(t) for t in onhold] + [''] +
                [fldtpl % tuple(t) for t in done])

        # save line template to use when adding new tasks (to keep alignment)
        let("s:fldtpl", fldtpl)
        cursor(pos)

def newtodo():
    """Add a new todo item."""
    buf = current.buffer

    # default line template or reuse one from sort(), to keep alignment
    fldtpl = exist_eval("s:fldtpl") or " %-25s%-10s%-10s%-6s%-6s%-8s%s"

    # insert header and divider
    flds = tuple(eval("s:headers").split())
    if not buf[0].startswith(' ' + flds[0]):
        buf[0:0] = [fldtpl % flds, '-'*76]

    # insert new task with default values
    ln = lnum() - 1
    if ln < 2: ln = 2
    start = asctime().split()[:3]
    flds = ("Task", '', '1', '1', '0', "No", join(start))
    buf.append([fldtpl % flds], ln)

    cursor(ln+1, 0)
    change_name()

def opentodo():
    """Open todo window."""
    sb = ieval("&splitbelow")
    let("&splitbelow", '1')
    command("split")
    wincmd('j')
    edit(expanduser("~/docs/lst.todo"))
    let("&splitbelow", sb)
    current.window.height = 6
    normal("gg")
    return

    for b in buffers:
        if b.name and b.name.endswith(".todo"):
            bnr = bufnr(b.name)
            if ieval("buflisted(%s)" % bnr):
                command("split %s" % b.name)
                # show_active()
                edit(expanduser("~/docs/lst.todo"))
                break
    let("&splitbelow", sb)

def toggle_onhold():
    """Toggle on/off hold."""
    normal("$F BBB")

    val = eval("expand('<cword>')").lower()
    if   val == "no": normal("RYes")
    elif val == "yes": normal("RNo ")
    normal('0')

def show_active():
    """Resize win to show only active tasks."""
    for n, l in enumerate(current.buffer):
        if not l.strip():
            n += 2
            if n < 6: n = 6
            current.window.height = n
            normal("gg")
            break

def change_name():
    """Change name of task. ('R' cmd is run from mapping)."""
    l = current.line
    if "  " in l:
        i = l.index("  ")
        l = ' '*i + l[i:]


if __name__ == "__main__":
    val = exist_eval("a:1")
    if val:
        if   val == "open": opentodo()
        elif val == "new": newtodo()
        elif val == "toggle_onhold": toggle_onhold()
        elif val == "show_active": show_active()
        elif val == "change_name": change_name()
        elif val == "sort": Sort().sort()
