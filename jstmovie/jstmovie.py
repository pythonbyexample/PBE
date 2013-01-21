#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

""" jstmovie - convert a text movie into a javascript file

sample format:

Yadda yadda
:pause 4
This will be shown after 4s pause

:type
This text will be shown with typewriter effect

(Note that :clear command is used in console version but is ignored in javascript)

copyright 2013 lightbird.net
license: (see LICENSE file)
"""

import os, sys
import re
from os.path import join as pjoin
from json import dumps

from utils import getitem, first, nl, space


cmdpat         = "(:pause ?\d*|:clear|:type)"
tut_dir        = "tmovies/src/"
outdir         = "tmovies/out/"
tplfn          = "tmovies/template.html"
nbsp           = "&nbsp;"
interp_typecmd = True   # auto insert type effect before python interpreter lines (>>>)

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

        for section in self.sections:

            if re.match(cmdpat, section):
                section  = section.split()
                cmd, arg = section[0][1:], getitem(section, 1)
                if cmd == "pause":
                    arg = arg or default_pause
                self.commands.append((cmd, arg))
            else:
                add(section)

        add(nl*3 + "  --- THE END ---" + nl*2)
        self.write_html()

    def write_html(self):
        cmds = dumps(self.commands, indent=4, separators=(',', ':'))
        html = self.tpl.replace("%COMMANDS%", cmds)
        with open(pjoin(outdir, self.name + ".html"), 'w') as fp:
            fp.write(html)

    def add_text(self, text):
        if text.startswith(nl):
            text = text[1:]

        for line in text.split(nl):
            if interp_typecmd and line.strip().startswith(">>>"):
                self.commands.append(("type", None))
            self.commands.append( ("text", space + line.replace(space*4, nbsp*4)) )
        # self.commands.extend( [("text", space+l) for l in text] )


class TutorialMovies(object):
    def run(self):
        mfiles = [fn for fn in os.listdir(tut_dir) if not fn.startswith('.')]
        tpl    = open(tplfn).read()

        for fn in mfiles:
            Tutorial(fn, tpl).run()


if __name__ == "__main__":
    try                      : TutorialMovies().run()
    except KeyboardInterrupt : pass
