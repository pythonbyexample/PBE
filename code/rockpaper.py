#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as rndchoice
from time import sleep

players          = 'XY'
ai_players       = 'XY'
moves            = "rps"
wins             = ("rp", "sr", "ps")   # choice on the right side wins
quit_key         = 'q'
pause_time       = 0.3


class RockPaperScissors(object):
    prompt   = "> "
    inv_move = "Invalid move"
    status   = "%5s %3d %5s %3d"

    def run(self):
        scores = [0, 0]
        while True:
            choice1, choice2 = (self.get_move(player) for player in players)

            if choice1 != choice2:
                winplayer = 1 if choice1+choice2 in wins else 0
                scores[winplayer] += 1
            print(self.status % (players[0], scores[0], players[1], scores[1]))
            sleep(pause_time)

    def get_move(self, player):
        return self.ai_move() if player in ai_players else self.player_move()

    def ai_move(self):
        return rndchoice(moves)

    def player_move(self):
        while True:
            inp = input(self.prompt)
            if inp == quit_key : sys.exit()
            elif inp in moves  : return inp
            else               : print(self.inv_move)

if __name__ == "__main__":
    try                      : RockPaperScissors().run()
    except KeyboardInterrupt : pass
