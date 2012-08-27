from random import random
from things import Thing


class Rules(object):
    """Rulesets for game of life."""
    n = 1
    add = 3

    def life(self, fld, location, val, neighbours):
        if val == ' ':
            if neighbours==3:
                things.append( Thing(fld, cell, location) )
        elif not (1 < neighbours < 4):
            val.remove()

    def lifernd(self, fld, location, val, neighbours):
        """Fuzzy game of life."""
        add = 3
        rnd = random()
        if   rnd > 0.8: add = 2
        elif rnd > 0.7: add = 5
        elif rnd > 0.6: add = 4

        if val == ' ':
            if neighbours==add:
                things.append( Thing(fld, cell, location) )
        elif not val.alive:
            return
        elif not (1 < neighbours < 4) and random() > 0.5:
            val.remove()

    def lifend(self, fld, location, val, neighbours):
        """Fuzzy game of life with night/day variations."""
        add = 3
        rmv = [1, 4]
        rmv_rnd = 0.5
        rnd = random()
        if   rnd > 0.8: add = 2
        elif rnd > 0.7: add = 5
        elif rnd > 0.6: add = 4

        x = int(self.n/10)
        if int(self.n/15) % 2:
            add += 1
            rmv[0] = 2
            rmv_rnd = 0.58

        if val == ' ':
            if neighbours == add:
                things.append( Thing(fld, cell, location) )
        elif not val.alive:
            return
        elif not (rmv[0] < neighbours < rmv[1]) and random() > rmv_rnd:
            val.remove()
        self.add = add
