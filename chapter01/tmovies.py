#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, sys
import re
from time import sleep

from utils import TextInput, BufferedIterator, getitem, iround, enumerate1, range1, sjoin, nl, first, space
from utils import progress_bar


tut_dir          = "t-movies"
cmdpat           = "(:sleep ?\d*\n|:clear\n|:type\n)"
stat_tpl         = " %s   %s"
resetchar        = '\r'

update_speed     = 8        # for progress bar
default_slp      = 4
screensep        = 25
screen_width     = 78
line_pause       = 0.3
char_pause       = 0.03
pause_progress   = False
section_progress = True

# for x in range(5): print(TextInput().menu("abcdefgabcdefgab"))

class Tutorial(object):
    typeblock = False

    def __init__(self, fn):
        with open(os.path.join(tut_dir, fn)) as fp:
            self.sections = re.split(cmdpat, fp.read())

    def play(self):
        for section_num, section in enumerate1(self.sections):

            if re.match(cmdpat, section):
                section  = section.split()
                cmd, arg = section[0], getitem(section, 1, default_slp)

                if   cmd == ":sleep" : self.sleep(int(arg), section_num)
                elif cmd == ":clear" : print(nl * screensep)
                elif cmd == ":type"  : self.typeblock = True

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
            line = space + line

            if line.strip() and self.typeblock:
                for c in line:
                    print(c, end='')
                    sys.stdout.flush()
                    sleep(char_pause)
                print()
            else:
                print(space + line)
                sleep(line_pause)

            if not line.strip() and self.typeblock:
                self.typeblock = False

    def progress(self, section_num, n, total):
        sprogress = pprogress = ''

        if section_progress:
            sprogress = progress_bar(section_num, len(self.sections), 45)
        if pause_progress:
            pprogress = progress_bar(n, total, 20)
        print(stat_tpl % (pprogress, sprogress), end='')


class TutorialMovies(object):
    def run(self):
        inp     = TextInput()
        mfiles  = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        choices = [first(f.split('.')) for f in mfiles]

        while True:
            i = inp.menu(choices)
            Tutorial(mfiles[i]).play()


if __name__ == "__main__":
    try                      : TutorialMovies().run()
    except KeyboardInterrupt : pass
