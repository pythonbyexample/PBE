#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, sys
import re
from time import sleep

from utils import TextInput, BufferedIterator, getitem, enumerate1, first, nl, space
from utils import progress_bar


cmdpat           = "(:pause ?\d*|:clear|:type)"
tut_dir          = "t-movies"
stat_tpl         = " %s   %s"
resetchar        = '\r'

update_speed     = 8        # for progress bar
default_pause    = 4
screensep        = 25
screen_width     = 78
line_pause       = 0.3
char_pause       = 0.03
pause_progress   = False
section_progress = True

# for x in range(5): print(TextInput().menu("abcdefgabcdefgab"))

def printne(val):
    """Print with no end arg (no newline)."""
    print(val, end='')

class Tutorial(object):
    typeblock = False

    def __init__(self, fn):
        with open(os.path.join(tut_dir, fn)) as fp:
            self.sections = re.split(cmdpat, fp.read())

    def play(self):
        print(nl * 2)
        for section_num, section in enumerate1(self.sections):

            if re.match(cmdpat, section):
                section  = section.split()
                cmd, arg = section[0], getitem(section, 1)

                if   cmd == ":pause" : self.pause(arg, section_num)
                elif cmd == ":clear" : print(nl * screensep)
                elif cmd == ":type"  : self.typeblock = True

            else:
                self.display(section.lstrip())

        print(nl*2, "----- END -----", nl*2)

    def pause(self, seconds, section_num):
        seconds = int(seconds) if seconds else default_pause

        for n in range(seconds * update_speed):
            self.progress(section_num, n/update_speed, seconds)

            sys.stdout.flush()
            sleep(1 / update_speed)
            printne(resetchar + space*screen_width + resetchar)

    def display(self, section):
        for line in section.split(nl):
            line = space + line

            if line.strip() and self.typeblock:
                for c in line:
                    printne(c)
                    sys.stdout.flush()
                    sleep(char_pause)
                print()
            else:
                print(line)
                sleep(line_pause)

            if not line.strip() and self.typeblock:
                self.typeblock = False

    def progress(self, section_num, n, total):
        sprog = pprog = ''

        if section_progress:
            sprog = progress_bar(section_num, len(self.sections), 45)
        if pause_progress:
            pprog = progress_bar(n, total, 20)
        printne(stat_tpl % (pprog, sprog))


class TutorialMovies(object):
    def run(self):
        inp     = TextInput()
        mfiles  = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        choices = [ (first(f.split('.')), f) for f in mfiles ]

        while True:
            Tutorial(inp.menu(choices)).play()


if __name__ == "__main__":
    try                      : TutorialMovies().run()
    except KeyboardInterrupt : pass
