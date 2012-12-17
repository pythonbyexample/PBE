#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as randchoice
from time import sleep

from utils import TextInput

players    = 'XY'
ai_players = 'Y'
moves      = "rps"
wins       = ("rp", "sr", "ps")   # choice on the right side wins
status     = "%5s %3d %5s %3d     moves: %s %s"
pause_time = 0.3


class RockPaperScissors(object):
    def run(self):
        self.textinput = TextInput("(r|p|s)")
        scores         = [0, 0]

        while True:
            choice1, choice2 = (self.get_move(p) for p in players)

            if choice1 != choice2:
                winplayer = 1 if (choice1+choice2 in wins) else 0
                scores[winplayer] += 1

            print(status % (players[0], scores[0], players[1], scores[1], choice1, choice2))
            sleep(pause_time)

    def get_move(self, player):
        if player in ai_players : return randchoice(moves)
        else                    : return self.textinput.getval()


if __name__ == "__main__":
    try                      : RockPaperScissors().run()
    except KeyboardInterrupt : pass
