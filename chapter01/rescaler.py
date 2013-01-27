#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

""" Rescaler

copyright 2013 msirenef@lightbird.net
license: (see LICENSE file)
"""

import os, sys
from copy import copy
from utils import Container, nl


sizes = [
         (1, "ant", 0.01),
         (2, "doorway", 1),
         (3, "baseball bat", 1),
         (5, "whale", 10),
         (6, "city block", 100),
         (7, "Eiffel tower", 300),
         (8, "English channel (narrowest)", 35000),
         (9, "AU (Earth to Sun)", 1.5e11),
         (10, "Light Year", 9.5e15),

         (21, "thickness of sunglasses", 0.001),
         (22, "Staphilococcus bacterium", 1e-6),
         (23, "Poliovirus", 3e-8),
         (24, "Hydrogen atom diameter", 1e-10),
         (25, "Hydrogen nucleus", 2.4e-15),
     ]

sizes = {s[0]: Container(name=s[1], size=s[2]) for s in sizes}


class Rescaler(object):
    tpl = "%-28s %s"
    msg = "If %s was the size of %s" + nl*2

    def rescale(self, i1, i2):
        i1, i2 = sizes[i1], sizes[i2]
        scaled = copy(sizes)
        ratio  = i1.size / i2.size
        print(self.msg % (i1.name, i2.name))

        for item in scaled.values():
            item.size /= ratio
            print(self.tpl % (item.name, self.format(item.size)))

    def format(self, val):
        def fmt(val):
            plural = '' if val==1 else 's'
            return ("%.2f" % val).rstrip('0').rstrip('.'), plural

        if val < 1e-9:
            return "less than a nanometer"
        elif 1e-9 <= val < 1e-6:
            return "%s nanometer%s" % fmt(val * 1e9)
        elif 1e-6 <= val < .001:
            return "%s micrometer%s" % fmt(val * 1e6)
        elif .001 <= val < .01:
            return "%s millimeter%s" % fmt(val * 1000)
        elif .01 <= val < 1:
            return "%s centimeter%s" % fmt(val * 100)
        elif 1 <= val < 1000:
            return "%s meter%s" % fmt(val)
        elif val >= 1000:
            return "%s kilometer%s" % fmt(val / 1000)



if __name__ == "__main__":
    try                      : Rescaler().rescale(5, 1)
    except KeyboardInterrupt : pass
