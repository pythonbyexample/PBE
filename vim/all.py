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
