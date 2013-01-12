#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, sys
import re
from time import sleep
from json import dumps
from os.path import join as pjoin

from utils import TextInput, BufferedIterator, getitem, enumerate1, first, nl, space
from utils import progress_bar


cmdpat  = "(:pause ?\d*|:clear|:type)"
tut_dir = "t-movies"
outdir  = "jstmovies"
tplfn   = "page.html"
nbsp    = "&nbsp;"

class Tutorial(object):
    typeblock = False

    def __init__(self, fn, tpl):
        self.commands = []
        self.name     = first(fn.split('.'))
        self.tpl      = tpl

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

        self.write_html()

    def write_html(self):
        # cmds = dumps(self.commands)
        cmds = dumps(self.commands, indent=4, separators=(',', ':'))
        html = self.tpl % dict(commands=cmds)
        with open(pjoin(outdir, self.name + ".html"), 'w') as fp:
            fp.write(html)

    def add_text(self, *args):
        text = ''.join(args)
        if text.endswith('\n'): text = text[:-1]
        text = text.replace(space*4, nbsp*4).split(nl)
        self.commands.extend( [("text", space+l) for l in text] )


class TutorialMovies(object):
    def run(self):
        mfiles = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        tpl    = open(pjoin(outdir, tplfn)).read()

        for fn in mfiles:
            Tutorial(fn, tpl).run()


if __name__ == "__main__":
    try                      : TutorialMovies().run()
    except KeyboardInterrupt : pass
