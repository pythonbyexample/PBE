#!/usr/bin/env python3

import sys
from random import choice as rndchoice
from random import shuffle

from utils import TextInput, nextval, nl, first, cmp
from board import Board, Loc, BaseTile

size         = 8
player_chars = '⎔▇'
# ai_players   = '⎔▇'
ai_players   = '⎔'
blank        = '.'
padding      = 4, 2
pause_time   = 0.3


class CompareChar(object):
    def __eq__(self, other): return bool(self.char == other.char)
    def __ne__(self, other): return bool(self.char != other.char)


class Tile(BaseTile, CompareChar):
    blank = piece = False

    def __repr__(self): return self.char


class Blank(Tile): char = blank


class Piece(Tile):
    def __init__(self, loc=None, char=None):
        super(Piece, self).__init__(loc)
        self.char = char
        if loc: board[loc] = self

    def flip(self):
        self.char = nextval(player_chars, self.char)


class VersiBoard(Board):
    scores_msg = "%s  score: %3s    %s  score: %3s"

    def get_valid_moves(self, player):
        return [loc for loc in self.locations() if self.valid_move(player, loc)]

    def valid_move(self, player, loc):
        return bool(self.get_captured(player, loc))

    def get_captured(self, player, start_loc):
        """If `start_loc` is a valid move, returns a list of locations of captured pieces."""
        captured = []
        if not self[start_loc].blank:
            return []

        # check each of the eight directions
        for dir in self.dirlist2:
            templist = []
            tile     = self.next_tile(start_loc, dir)

            # keep adding locations as long as it's an enemy piece
            while tile and tile == player.enemy():
                templist.append(tile)
                tile = self.next_tile(tile, dir)

            # if reached end of board or next tile is not our piece, skip to next direction
            if not tile or player != tile:
                continue
            captured.extend(templist)

        return captured

    def is_corner(self, loc):
        return loc.x in (0, self.width-1) and loc.y in (0, self.height-1)

    def status(self):
        print(self.scores_msg % (player1, player1.score(), player2, player2.score()))


class Player(CompareChar):
    def __init__(self, char):
        self.char = char
        self.ai   = char in ai_players

    def __repr__(self) : return self.char

    def score(self)    : return sum(tile==self for tile in board)
    def enemy(self)    : return nextval(players, self)


    def make_move(self, loc):
        for tile in board.get_captured(self, loc):
            tile.flip()
        Piece(loc, self.char)

    def get_random_move(self):
        """Return location of best move."""
        def by_corner_score(loc):
            return ( not board.is_corner(loc), len(board.get_captured(self, loc)) )

        moves = board.get_valid_moves(self)
        shuffle(moves)
        return first( sorted(moves, key=by_corner_score, reverse=True) )


class Versi(object):
    winmsg     = "%s wins!"
    tiemsg     = "The game was a tie!"

    def __init__(self):
        Piece(Loc(3,3), player1.char)
        Piece(Loc(4,4), player1.char)
        Piece(Loc(3,4), player2.char)
        Piece(Loc(4,3), player2.char)

    def check_end(self):
        if all(t.piece for t in board): self.game_end()

    def game_end(self):
        board.draw()
        winner = cmp(player1.score(), player2.score())
        if not winner : print(nl, self.tiemsg)
        else          : print(nl, self.winmsg % (player1 if winner>0 else player2))
        sys.exit()

class BasicInterface(object):
    def run(self):
        """Display board, start the game, process moves; return True to start a new game, False to exit."""
        moves          = board.get_valid_moves
        player         = rndchoice(players)
        self.textinput = TextInput(board=board)

        while True:
            board.draw()
            move = player.get_random_move() if player.ai else self.get_move(player)
            player.make_move(move)

            # give next turn to enemy OR end game if no turns left, FALLTHRU: current player keeps the turn
            if moves(player.enemy()) : player = player.enemy()
            else                     : versi.check_end()

    def get_move(self, player):
        while True:
            loc = self.textinput.getloc()
            if board.valid_move(player, loc) : return loc
            else                             : print(self.textinput.invalid_move)


if __name__ == "__main__":
    board            = VersiBoard(size, Blank, num_grid=True, padding=padding, pause_time=pause_time)
    players          = [Player(c) for c in player_chars]
    player1, player2 = players
    versi            = Versi()

    try: BasicInterface().run()
    except KeyboardInterrupt: sys.exit()
