#!/usr/bin/env python

# Imports {{{
# Inspired by Flippy game By Al Sweigart http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

from __future__ import division

import sys
import random
import pygame
import logging

from time import time
from logging import debug

from pygame.locals import *

import board as board_module
from board import Board, Piece, Loc, render_text
from settings import *

logging.basicConfig(filename="out.log", level=logging.DEBUG, format="%(message)s")
# }}}


class PlayerAI(object):
    """Parent class for live and computer players."""
    def __init__(self, piece):
        self.piece = piece

    def make_move(self, loc):
        """Place new piece at `loc`, return list of captured locations."""
        captured = board.get_captured(self.piece, loc)
        piece = Piece(self.piece.colour, board, loc)
        board.animate_move(captured, piece)

        for loc in captured: board[loc].flip()
        board.draw()
        reversi.draw_info()
        return captured


class Player(PlayerAI):
    newgame = hints = None      # buttons

    def turn(self):
        """Get player's move, return Location to move OR return `newgame_code` to start a new game."""
        reversi.check_for_quit()

        # get button click or move click on a tile
        button = reversi.get_button_click(self.newgame, self.hints)
        if not button:
            pass    # click outside of tiles / buttons
        elif button == self.newgame:
            board.reset()
            return newgame_code
        elif button == self.hints:
            board.toggle_hints(self.piece)
        else:
            move_to = board.get_clicked_tile( Loc(button) )
            if move_to and board.is_valid_move(self.piece, move_to):
                return move_to

        self.newgame, self.hints = board.buttons()
        reversi.mainclock_tick()

class Computer(PlayerAI):
    def turn(self):
        """Return Location of best move."""
        reversi.draw_info()
        board.buttons()
        possible_moves = board.get_valid_moves(self.piece)
        random.shuffle(possible_moves)

        # Make it look like the computer is thinking by pausing a bit.
        resume = time() + random.randint(5, 15) * 0.1
        while time() < resume: pygame.display.update()

        # always go for a corner if available
        for loc in possible_moves:
            if board.is_corner(loc): return loc

        # go through possible moves and remember the best scoring move
        score = -1
        for loc in possible_moves:
            captured = board.get_captured(self.piece, loc)
            if len(captured) > score:
                score = len(captured)
                best_move = loc
        return best_move


class Reversi(object):
    def __init__(self):
        """Initialize pygame, fonts, load images."""
        pygame.init()
        self.mainclock = pygame.time.Clock()
        self.display   = pygame.display.set_mode((width, height))
        self.font      = pygame.font.Font("freesansbold.ttf", 16)
        self.bigfont   = pygame.font.Font("freesansbold.ttf", 32)
        pygame.display.set_caption("Reversi")

        # load images
        size           = tilesize - 4
        self.piece_img = dict(white = load_image(white_fn, scale=(size, size)),
                              black = load_image(black_fn, scale=(size, size)) )

        self.tileimg = load_image(tile_fn, scale=(tilesize, tilesize))
        self.bgimage = pygame.image.load(bg_fn)
        self.bgimage = pygame.transform.smoothscale(self.bgimage, (width, height))

    def main(self):
        while True:
            if not reversi.run_game(): break

    def run_game(self):
        """Display board, start the game, process moves; return True to start a new game, False to exit."""
        board.draw()
        valid_moves    = board.get_valid_moves
        self.turn      = random.choice(["computer", "player"])
        ppiece, cpiece = self.enter_player_piece()
        player         = self.player    = Player(ppiece)
        computer       = self.computer  = Computer(cpiece)

        while True:
            board.draw()
            if self.turn == "player":

                # player turn: display hints, get player move, make the move
                reversi.draw_info()
                board.add_hints(player.piece)
                while True:
                    move_to = player.turn()
                    if move_to: break
                board.remove_hints()

                if move_to == newgame_code:
                    return newgame_code
                player.make_move(move_to)


                # give next turn to computer OR keep the turn OR end game if no turns left
                if   valid_moves(computer.piece)   : self.turn = "computer"
                elif not valid_moves(player.piece) : break

            elif self.turn == "computer":
                computer.make_move( computer.turn() )

                # give next turn to player OR keep the turn OR end game if no turns left
                if   valid_moves(player.piece)       : self.turn = "player"
                elif not valid_moves(computer.piece) : break

        board.draw()
        self.results_message()
        return self.new_game()

    def new_game(self):
        """Ask if playing a new game or not."""
        render_text("Play again?", colours.text, colours.bg1, center=(centerx, centery + 50), font=self.bigfont)
        yes = render_text("Yes", colours.text, colours.bg1, center=(centerx-60, centery+90), font=self.bigfont, border=4)
        no  = render_text("No", colours.text, colours.bg1, center=(centerx+60, centery+90), font=self.bigfont, border=4)

        while True:
            self.check_for_quit()
            button = self.get_button_click(yes, no)
            if button == yes  : return True
            elif button == no : return False
            self.mainclock_tick()

    def mainclock_tick(self):
        pygame.display.update()
        self.mainclock.tick(FPS)

    def enter_player_piece(self):
        """Show selection buttons and return [player_piece, ai_piece]."""
        render_text("Do you want to be white or black?", colours.text, colours.bg1,
                    center=(centerx, int(height / 2)), border=2, bcolour=colours.bg1)
        whitebtn = render_text("White", colours.text, colours.bg1, center=(centerx-60, centery+40), border=4)
        blackbtn = render_text("Black", colours.text, colours.bg1, center=(centerx+60, centery+40), border=4)

        while True:
            self.check_for_quit()
            button = self.get_button_click(whitebtn, blackbtn)
            if   button == whitebtn: return [Piece(white), Piece(black)]
            elif button == blackbtn: return [Piece(black), Piece(white)]
            self.mainclock_tick()

    def get_button_click(self, *buttons):
        """If button is clicked, return it; if click is not over any button, return position; if no clicks, return None."""
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                for button in buttons:
                    if button and button[1].collidepoint(event.pos):
                        return button
                return event.pos

    def draw_info(self):
        """Draws scores and whose turn it is at the bottom of the screen."""
        scores = board.get_score(self.player, self.computer)
        tpl    = "Player Score: %s    Computer Score: %s    %s's Turn"
        render_text(tpl % (scores[0], scores[1], self.turn.title()), colours.bg1, bottomleft=(10, height-5))

    def results_message(self):
        """Display win/lose results message."""
        pscore, cscore = board.get_score(self.player, self.computer)
        if pscore > cscore:
            text = "You beat the computer by %s points! Congratulations!" % (pscore-cscore)
        elif pscore < cscore:
            text = "You lost. The computer beat you by %s points." % (cscore-pscore)
        else:
            text = "The game was a tie!"
        render_text(text, colours.text, colours.bg1, center=(centerx, centery))

    def check_for_quit(self):
        for event in pygame.event.get((QUIT, KEYUP)):
            if event.type==QUIT or (event.key==K_ESCAPE and event.type==KEYUP):
                pygame.quit()
                sys.exit()


def load_image(fn, scale=None):
    """Load image from `fn`, scale it to dimension tuple `scale`."""
    image = pygame.image.load(fn)
    if scale:
        image = pygame.transform.smoothscale(image, scale)
    rect = image.get_rect()
    return image, rect


if __name__ == "__main__":
    reversi = Reversi()
    board   = Board()
    board_module.reversi = reversi  # make reversi object available to board module for convenience
    board.reset()
    reversi.main()
