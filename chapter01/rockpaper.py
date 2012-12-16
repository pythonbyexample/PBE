#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from random import choice as rndchoice
from time import sleep
from itertools import cycle

players          = 'XY'
player1, player2 = players
ai_players       = 'Y'
moves            = "rps"
wins             = ("rp", "sr", "ps")   # right choice wins
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
                win = int(choice1+choice2 in wins)
                scores[win] += 1
            print(self.status % (player1, scores[0], player2, scores[1]))
            sleep(pause_time)

    def get_move(self, player):
        return self.ai_move() if player in ai_players else self.player_move()

    def ai_move(self):
        return rndchoice("rps")

    def player_move(self):
        while True:
            inp = input(self.prompt)
            if inp == quit_key : sys.exit()
            if inp in moves    : return inp
            else               : print(self.inv_move)

if __name__ == "__main__":
    RockPaperScissors().run()
