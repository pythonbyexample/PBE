#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, sys
import re
from time import sleep

from utils import TextInput, BufferedIterator, getitem, iround, enumerate1, range1, sjoin, nl, first, space
from utils import progress_bar


tut_dir      = "t-movies"
cmdpat       = "(:sleep ?\d*|:clear)"
stat_tpl     = " %s   %s"
resetchar    = '\r'
update_speed = 8        # for progress bar
default_slp  = 4
screensep    = 25
screen_width = 78
line_pause   = 0.3

# for x in range(5): print(TextInput().menu("abcdefgabcdefgab"))

class Tutorial(object):
    def __init__(self, fn):
        with open(os.path.join(tut_dir, fn)) as fp:
            self.sections = re.split(cmdpat, fp.read())

    def play(self):
        for section_num, section in enumerate1(self.sections):

            if re.match(cmdpat, section):
                section  = section.split()
                cmd, arg = section[0], getitem(section, 1, default_slp)

                if   cmd == ":sleep": self.sleep(int(arg), section_num)
                elif cmd == ":clear": print(nl * screensep)

            else:
                self.display(section)

        print(nl*2, "----- END -----", nl*2)

    def sleep(self, seconds, section_num):
        for n in range(seconds * update_speed):
            self.progress(section_num, n/update_speed, seconds)
            sys.stdout.flush()
            sleep(1 / update_speed)
            print(resetchar + space*screen_width + resetchar, end='')

    def display(self, section):
        for line in section.split(nl):
            print(space + line)
            sleep(line_pause)

    def progress(self, section_num, n, total):
        sprogress = progress_bar(section_num, len(self.sections), 45)
        print( stat_tpl % (progress_bar(n, total, 20), sprogress), end='' )


class TutorialMovies(object):
    def run(self):
        inp     = TextInput()
        mfiles  = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        choices = [first(f.split('.')) for f in mfiles]

        while True:
            i = inp.menu(choices)
            Tutorial(mfiles[i]).play()


if __name__ == "__main__":
    # pass
    try                      : TutorialMovies().run()
    except KeyboardInterrupt : pass
