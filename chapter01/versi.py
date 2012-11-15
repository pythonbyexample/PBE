#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division
import sys
from random import choice as rndchoice
from random import randint
from time import sleep

from utils import enumerate1, range1, parse_hnuminput, ujoin, Loop
from board import Board, Loc, Dir

size          = 8
player_chars  = 'XO'
human_players = 'X'

pause_time    = 0.2

nl            = '\n'
space         = ' '
blankchar     = '.'
prompt        = '> '
quit_key      = 'q'
tiletpl       = "%5s"


class CompareChar(object):
    def __eq__(self, other):
        return bool(self.char==other.char)

    def __ne__(self, other):
        return not self.__eq__(other)


class Blank(CompareChar):
    blank = True
    char  = blankchar

    def __init__(self, loc):
        self.loc = loc

    def __repr__(self):
        return self.char


class Piece(Blank):
    def __init__(self, loc=None, char=None):
        self.loc = loc
        if char:
            self.char = char
            self.blank = False
        if loc: board[loc] = self

    def flip(self):
        pc = player_chars
        self.char = pc[0] if self.char==pc[1] else pc[1]

    def is_opposite_of(self, other):
        return bool( self.char and other.char and self.char != other.char)


class VersiBoard(Board):
    def __init__(self, size, def_tile):
        super(VersiBoard, self).__init__(size, def_tile)

    def get_valid_moves(self, player):
        return [loc for loc in self if self.is_valid_move(player, loc)]

    def is_valid_move(self, player, loc):
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
        return captured

    def get_scores(self, players):
        """Return a tuple of (player1, score), (player2, score)."""
        p = players
        return (sum( tile == p[0] for tile in self ), p[0]), \
               (sum( tile == p[1] for tile in self ), p[1])

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
        self.char  = char
        self.human = char in human_players

    def make_move(self, loc):
        """Place new piece at `loc`, return list of captured locations."""
        captured = board.get_captured(self, loc)
        Piece(loc, self.char)
        for loc in captured: board[loc].flip()
        return captured

    def get_random_move(self):
        """Return Location of best move."""
        moves = board.get_valid_moves(self)
        random.shuffle(moves)

        for loc in moves:
            if board.is_corner(loc): return loc

        # go through possible moves and remember the best scoring move
        score = -1
        for loc in moves:
            captured = len(board.get_captured(self, loc))
            if captured > score:
                score = captured
                best_move = loc
        return best_move

    def enemy(self):
        return players[0] if self==players[1] else players[1]


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
        scores = sorted(board.get_scores(players))
        if scores[0] == scores[2] : print(nl, self.tiemsg)
        else                      : print(nl, self.winmsg % scores[0][1])
        sys.exit()

    def status(self):
        s = board.get_scores(players)
        print(self.scores_msg % (s[1], s[0], s[3], s[2]))


class Test(object):
    def run(self):
        """Display board, start the game, process moves; return True to start a new game, False to exit."""
        valid_moves = board.get_valid_moves
        player      = rndchoice(players)

        while True:
            board.draw()
            if player.human:
                player.make_move(self.get_move())
                if   valid_moves(player.enemy()) : player = player.enemy()
                elif not valid_moves(player)     : break

            else:
                player.make_move(player.get_random_move())

                # give next turn to player OR keep the turn OR end game if no turns left
                if   valid_moves(player.enemy()) : player = player.enemy()
                elif not valid_moves(player)     : break


if __name__ == "__main__":
    board   = VersiBoard(size, Blank)
    versi   = Versi()
    players = Player(player_chars[0]), Player(player_chars[1])

    try: Test().run()
    except KeyboardInterrupt: sys.exit()
