#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, sys
import re
from time import sleep

from utils import TextInput, enumerate1, range1, sjoin, nl, first


tut_dir   = "t-movies"
screensep = 25


class MInput(TextInput):
    choice_tpl = "%2d) %s"

    def menu(self, choices):
        self.choices = choices
        for c in enumerate1(choices):
            print(self.choice_tpl % c)

        fmt = "(%s)" % sjoin( range1(len(choices)), '|' )
        self.formats = [fmt]
        return int(self.getval()) - 1

# for x in range(5): print(MInput().menu("abcdefgabcdefgab"))


class Tutorial(object):
    def __init__(self, fn):
        with open(os.path.join(tut_dir, fn)) as fp:
            self.sections = re.split("(:sleep ?\d*|:clear)", fp.read())

    def play(self):
        for section in self.sections:
            if section.startswith(":sleep"):
                sleep(int( section.strip().split()[1] ))
            elif section == ":clear":
                print(nl*screensep)
            else:
                print(section)


class TutorialMovies(object):
    def run(self):
        inp = MInput()
        mfiles = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        print("mfiles", mfiles)
        choices = [first(f.split('.')) for f in mfiles]
        i = inp.menu(choices)
        Tutorial(mfiles[i]).play()


if __name__ == "__main__":
    try:
        TutorialMovies().run()
    except KeyboardInterrupt:
        pass
