#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep

from utils import enumerate1, range1, parse_hnuminput, ujoin, nextval
from board import Board, Loc

size         = 8
player_chars = 'XO'
ai_players   = 'O'

pause_time   = 0.2

nl           = '\n'
space        = ' '
blankchar    = '.'
prompt       = '> '
quit_key     = 'q'
tiletpl      = "%5s"


class CompareChar(object):
    def __eq__(self, other):
        return bool(self.char==other.char)

    def __ne__(self, other):
        return not self.__eq__(other)


class Tile(CompareChar):
    blank = True
    char  = blankchar

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return self.char


class Piece(Tile):
    blank = False

    def __init__(self, loc=None, char=None):
        self.loc  = loc
        self.char = char
        if loc: board[loc] = self

    def flip(self):
        self.char = nextval(player_chars, self.char)


class VersiBoard(Board):
    def get_valid_moves(self, player):
        return [loc for loc in self.locations() if self.valid_move(player, loc)]

    def valid_move(self, player, loc):
        return bool(self.get_captured(player, loc))

    def get_captured(self, player, start_loc):
        """If `start_loc` is a valid move, returns a list of locations of captured pieces."""
        if not self[start_loc].blank:
            return []
        captured = []

        # check each of the eight directions
        for dir in self.dirlist2:
            templist = []
            loc      = self.nextloc(start_loc, dir)

            # keep adding locations as long as it's an enemy piece
            while self.valid(loc) and player != self[loc]:
                templist.append(loc)
                loc = self.nextloc(loc, dir)

            # if reached end of board or next tile is not our piece, skip to next direction
            if not self.valid(loc) or player != self[loc]:
                continue
            captured.extend(templist)
        return [self[loc] for loc in captured]

    def is_corner(self, loc):
        return loc.x in (0, self.maxx) and loc.y in (0, self.maxy)

    def draw(self):
        print(nl*5)
        print(space*5, ujoin( range1(self.width), space, tiletpl ), nl)

        for n, row in enumerate1(self.board):
            print(tiletpl % n, ujoin(row, space, tiletpl), nl*2)
        sleep(pause_time)


class Player(CompareChar):
    def __init__(self, char):
        self.char = char
        self.ai   = char in ai_players

    def score(self):
        return sum(tile==self for tile in board)

    def make_move(self, loc):
        """Place new piece at `loc`, return list of captured locations."""
        for tile in board.get_captured(self, loc):
            tile.flip()
        Piece(loc, self.char)

    def get_random_move(self):
        """Return location of best move."""
        def by_corner_score(loc):
            return (not board.is_corner(loc), len(board.get_captured(self, loc)))
        moves = board.get_valid_moves(self)
        return sorted(moves, key=by_corner_score, reverse=True)[0]

    def enemy(self):
        return nextval(players, self)


class Versi(object):
    winmsg     = "%s has won!"
    tiemsg     = "The game was a tie!"
    scores_msg = "%s Score: %s    %s Score: %s"

    def __init__(self):
        Piece(Loc(3,3), player_chars[0])
        Piece(Loc(4,4), player_chars[0])
        Piece(Loc(3,4), player_chars[1])
        Piece(Loc(4,3), player_chars[1])

    def check_end(self):
        if not any(t.blank==True for t in board):
            self.game_end()

    def game_end(self):
        winner, loser = sorted((p.score(), p) for p in players)
        if winner[0] == loser[0]:
            print(nl, self.tiemsg)
        else:
            print(nl, self.winmsg % winner[1])
        sys.exit()

    def status(self):
        p1, p2 = players
        print(self.scores_msg % (p1, p1.score(), p2, p2.score()))


class Test(object):
    invalid_inp = "Invalid input"

    def run(self):
        """Display board, start the game, process moves; return True to start a new game, False to exit."""
        moves = board.get_valid_moves
        player      = rndchoice(players)

        while True:
            board.draw()
            get_move = player.get_random_move if player.ai else self.get_move
            player.make_move(get_move())

            # give next turn to player OR end game if no turns left OR current player keeps the turn
            if moves(player.enemy()) : player = player.enemy()
            else                     : versi.check_end()
            # elif not moves(player)     : versi.game_end()

    def get_move(self, player):
        while 1:
            try:
                inp = raw_input(prompt).strip()
                if inp == quit_key: sys.exit()

                cmd = inp.split() if space in inp else inp
                x, y = parse_hnuminput(cmd)
                loc = Loc(x, y)

                if board.valid_move(player, loc):
                    return loc
            except (IndexError, ValueError, TypeError, KeyError):
                print(self.invalid_inp)


if __name__ == "__main__":
    board   = VersiBoard(size, Tile)
    versi   = Versi()
    players = [Player(c) for c in player_chars]

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
