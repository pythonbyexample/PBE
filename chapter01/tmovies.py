#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, sys
import re
from time import sleep

from utils import TextInput, BufferedIterator, getitem, iround, enumerate1, range1, sjoin, nl, first, space


tut_dir      = "t-movies"
screensep    = 25
cmdpat       = "(:sleep ?\d*|:clear|:type)"
stat_tpl     = " %s   %s"
resetchar    = '\r'
update_speed = 8        # for progress bar

# for x in range(5): print(TextInput().menu("abcdefgabcdefgab"))


class Tutorial(object):
    typeline = False

    def __init__(self, fn):
        with open(os.path.join(tut_dir, fn)) as fp:
            self.sections = re.split(cmdpat, fp.read())

    def play(self):
        for section_num, section in enumerate1(self.sections):

            if re.match(cmdpat, section):
                section  = section.split()
                cmd, arg = section[0], getitem(section, 1)

                if   cmd == ":sleep" : self.sleep(int(arg), section_num)
                elif cmd == ":clear" : print(nl * screensep)
                elif cmd == ":type"  : self.typeline = True

            else:
                self.display(section)

        print(nl*2, '-'*5, "END", '-'*5, nl*2)

    def sleep(self, seconds, section_num):
        for n in range(seconds * update_speed):
            self.progress(section_num, n/update_speed, seconds)
            sys.stdout.flush()
            sleep(1 / update_speed)
            print(resetchar + space*78 + resetchar, end='')

    def display(self, section):
        for line in section.split(nl):
            line = space + line
            if line.strip() and self.typeline:
                for c in line:
                    print(c, end='')
                    sys.stdout.flush()
                    sleep(0.03)
                self.typeline = False
            else:
                print(space + line)
                sleep(0.3)

    def progress(self, section_num, n, total):
        sprogress = progress_bar(len(self.sections), section_num, 45)
        print( stat_tpl % (progress_bar(total, n, 20), sprogress), end='' )


class TutorialMovies(object):
    def run(self):
        inp     = TextInput()
        mfiles  = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        choices = [first(f.split('.')) for f in mfiles]

        while True:
            i = inp.menu(choices)
            Tutorial(mfiles[i]).play()


def progress_bar(total, value, size=78, char='∘'):
    size = size - 2
    tpl  = "|%%-%ds|" % size
    return tpl % (char * iround(size * value/total))


if __name__ == "__main__":
    try                      : TutorialMovies().run()
    except KeyboardInterrupt : pass
