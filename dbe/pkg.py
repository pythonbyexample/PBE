#!/usr/bin/env python3

from shutil import copy, copytree
from os import rename
from os.path import join, expanduser

akdjango = expanduser("~/win-projects/akdjango/")

def main():
    # apps = "blog bombquiz forum issues portfolio questionnaire".split()
    apps = "blog bombquiz forum".split()
    totpl = apps + "index.html paginator.html".split()
    todbe = apps + "mcbv shared".split()

    for d in todbe:
        copytree(d, "dbe/")
    for d in totpl:
        copytree(d, "dbe/templates/")

    copytree("dbe", akdjango)
