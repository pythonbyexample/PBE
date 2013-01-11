#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, sys
import re
from time import sleep

from utils import TextInput, BufferedIterator, getitem, enumerate1, first, nl, space
from utils import progress_bar


cmdpat           = "(:pause ?\d*|:clear|:type)"
tut_dir          = "t-movies"

update_speed     = 8        # for progress bar
default_pause    = 4
screensep        = 25
screen_width     = 78
line_pause       = 0.3
char_pause       = 0.03
pause_progress   = False
section_progress = True


class Tutorial(object):
    typeblock = False

    def __init__(self, fn):
        self.commands = []

        with open(os.path.join(tut_dir, fn)) as fp:
            self.sections = re.split(cmdpat, fp.read())

    def run(self):
        add = self.add_text
        add(nl * 2)

        for section_num, section in enumerate1(self.sections):

            if re.match(cmdpat, section):
                section  = section.split()
                cmd, arg = section[0][1:], getitem(section, 1)
                if cmd == "pause":
                    arg = arg or default_pause
                self.commands.append((cmd, arg))
            else:
                add(section.lstrip(nl))

        add(nl*2, "----- END -----", nl*2)

    def add_text(self, *args):
        text = ''.join(args)
        for line in text.split(nl):
            self.commands.append(("text", space + line))


class TutorialMovies(object):
    def run(self):
        mfiles  = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        choices = [ (first(f.split('.')), f) for f in mfiles ]

        for fn in mfiles:
            Tutorial(fn).run()


if __name__ == "__main__":
    try                      : TutorialMovies().run()
    except KeyboardInterrupt : pass
