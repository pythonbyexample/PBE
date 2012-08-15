#!/usr/bin/env python

# Imports {{{
# Flippy (an Othello or Reversi clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# Based on the "reversi.py" code that originally appeared in "Invent
# Your Own Computer Games with Python", chapter 15:
#   http://inventwithpython.com/chapter15.html

import random, sys, pygame, time, copy
from pygame.locals import *

FPS            = 10
WINDOWWIDTH    = 640
WINDOWHEIGHT   = 480
SPACESIZE      = 50 # width & height of each space on the board, in pixels
BOARDWIDTH     = 8
BOARDHEIGHT    = 8
white_tile     = "white_tile"
black_tile     = "black_tile"
EMPTY_SPACE    = "EMPTY_SPACE"
HINT_TILE      = "HINT_TILE"
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation

XMARGIN        = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN        = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

WHITE          = (255, 255, 255)
BLACK          = (  0,   0,   0)
GREEN          = (  0, 155,   0)
BRIGHTBLUE     = (  0,  50, 255)
BROWN          = (174,  94,   0)

TEXTBGCOLOR1   = BRIGHTBLUE
TEXTBGCOLOR2   = GREEN
GRIDLINECOLOR  = BLACK
TEXTCOLOR      = WHITE
HINTCOLOR      = BROWN
# }}}


def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Flippy")
    FONT = pygame.font.Font("freesansbold.ttf", 16)
    BIGFONT = pygame.font.Font("freesansbold.ttf", 32)

    # Set up the background image.
    board_image = pygame.image.load("flippyboard.png")
    # Use smoothscale() to stretch the board image to fit the entire board:
    board_image = pygame.transform.smoothscale(board_image, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
    board_image_rect = board_image.get_rect()
    board_image_rect.topleft = (XMARGIN, YMARGIN)
    BGIMAGE = pygame.image.load("flippybackground.png")
    # Use smoothscale() to stretch the background image to fit the entire window:
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    BGIMAGE.blit(board_image, board_image_rect)

    # Run the main game.
    while True:
        if not run_game(): break

def render_text(text, colour, bg=None, topright=None, center=None, bottomleft=None, font=FONT):
    args = [text, True, colour]
    if bg: args.append(bg)
    surf = font.render(*args)
    rect = surf.get_rect()
    if topright     : rect.topright = topright
    elif center     : rect.center = center
    elif bottomleft : rect.bottomleft = bottomleft
    return surf, rect

def run_game():
    main_board = get_new_board()
    reset_board(main_board)
    show_hints = False
    turn = random.choice(["computer", "player"])

    draw_board(main_board)
    player_tile, computer_tile = enter_player_tile()

    # "New Game" and "Hints" buttons
    ngsurf, ngrect = render_text("New Game", TEXTCOLOR, TEXTBGCOLOR2, topright=(WINDOWWIDTH-8,10))
    hsurf, hrect = render_text("Hints", TEXTCOLOR, TEXTBGCOLOR2, topright=(WINDOWWIDTH-8,40))

    while True:
        if turn == "player":
            # Player's turn:
            if get_valid_moves(main_board, player_tile) == []:
                break

            movexy = None
            while not movexy:
                # Determine which board data structure to use for display.
                board_to_draw = get_board_with_valid_moves(main_board, player_tile) if show_hints else main_board

                check_for_quit()
                for event in pygame.event.get(): # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        if ngrect.collidepoint(event.pos):
                            return True
                        elif hrect.collidepoint(event.pos):
                            show_hints = not show_hints

                        movexy = get_space_clicked(event.pos)
                        if movexy and not is_valid_move(main_board, player_tile, movexy[0], movexy[1]):
                            movexy = None

                draw_board(board_to_draw)
                draw_info(board_to_draw, player_tile, computer_tile, turn)
                DISPLAYSURF.blit(ngsurf, ngrect)
                DISPLAYSURF.blit(hsurf, hrect)
                MAINCLOCK.tick(FPS)
                pygame.display.update()

            # Make the move and end the turn.
            make_move(main_board, player_tile, movexy[0], movexy[1], True)
            if get_valid_moves(main_board, computer_tile) != []:
                # Only set for the computer's turn if it can make a move.
                turn = "computer"

        else:
            # Computer's turn:
            if get_valid_moves(main_board, computer_tile) == []:
                # If it was set to be the computer's turn but
                # they can't move, then end the game.
                break

            # Draw the board.
            draw_board(main_board)
            draw_info(main_board, player_tile, computer_tile, turn)

            # Draw the "New Game" and "Hints" buttons.
            DISPLAYSURF.blit(ngsurf, ngrect)
            DISPLAYSURF.blit(hsurf, hrect)

            # Make it look like the computer is thinking by pausing a bit.
            pause_until = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pause_until:
                pygame.display.update()

            # Make the move and end the turn.
            x, y = get_computer_move(main_board, computer_tile)
            make_move(main_board, computer_tile, x, y, True)
            if get_valid_moves(main_board, player_tile):
                turn = "player"

    draw_board(main_board)
    scores = get_score_of_board(main_board)

    # Determine the text of the message to display.
    pscore, cscore = scores[player_tile], scores[computer_tile]
    if pscore > cscore:
        text = "You beat the computer by %s points! Congratulations!" % (pscore-cscore)
    elif pscore < cscore:
        text = "You lost. The computer beat you by %s points." % (cscore-pscore)
    else:
        text = "The game was a tie!"

    msg = render_text(text, TEXTCOLOR, TEXTBGCOLOR1, center=(int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)))
    DISPLAYSURF.blit(*msg)

    msg = render_text("Play again?", TEXTCOLOR, TEXTBGCOLOR1, center=(int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50), font=BIGFONT)
    DISPLAYSURF.blit(*msg)

    # yes/no buttons
    yes = render_text("Yes", TEXTCOLOR, TEXTBGCOLOR1, center=(int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90), font=BIGFONT)
    DISPLAYSURF.blit(*yes)
    no = render_text("No", TEXTCOLOR, TEXTBGCOLOR1, center=(int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90), font=BIGFONT)
    DISPLAYSURF.blit(*no)

    while True:
        # Process events until the user clicks on Yes or No.
        check_for_quit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                if yes[1].collidepoint(event.pos):
                    return True
                elif no[1].collidepoint(event.pos):
                    return False
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def tile_center(x, y):
    return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)

def animate_tile_change(tiles_to_flip, tile_color, additional_tile):
    # Draw the additional tile that was just laid down. (Otherwise we'd
    # have to completely redraw the board & the board info.)
    additional_tile_color = WHITE if tile_color==white_tile else BLACK
    additional_tile_x, additional_tile_y = tile_center(additional_tile[0], additional_tile[1])
    pygame.draw.circle(DISPLAYSURF, additional_tile_color, (additional_tile_x, additional_tile_y), int(SPACESIZE / 2) - 4)
    pygame.display.update()

    for rgb_values in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        if rgb_values > 255:
            rgb_values = 255
        elif rgb_values < 0:
            rgb_values = 0

        if tile_color == white_tile:
            color = tuple([rgb_values] * 3) # rgb_values goes from 0 to 255
        elif tile_color == black_tile:
            color = tuple([255 - rgb_values] * 3) # rgb_values goes from 255 to 0

        for x, y in tiles_to_flip:
            centerx, centery = tile_center(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        check_for_quit()

def draw_board(board):
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    for x in range(BOARDWIDTH + 1):
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx   = (x * SPACESIZE) + XMARGIN
        endy   = YMARGIN + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx   = XMARGIN + (BOARDWIDTH * SPACESIZE)
        endy   = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    # Draw the black & white tiles or hint spots.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            tile = board[x][y]
            tx, ty = tile_center(x, y)
            if tile in (white_tile, black_tile):
                tile_color = WHITE if tile==white_tile else BLACK
                pygame.draw.circle(DISPLAYSURF, tile_color, (tx, ty), int(SPACESIZE / 2) - 4)
            if tile == HINT_TILE:
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (tx - 4, ty - 4, 8, 8))

def get_space_clicked(position):
    """If user clicked a tile, return it."""
    mx, my = position
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mx > x * SPACESIZE + XMARGIN and mx < (x + 1) * SPACESIZE + XMARGIN and \
               my > y * SPACESIZE + YMARGIN and my < (y + 1) * SPACESIZE + YMARGIN:
                return (x, y)
    return None

def draw_info(board, player_tile, computer_tile, turn):
    """Draws scores and whose turn it is at the bottom of the screen."""
    scores = get_score_of_board(board)
    tpl = "Player Score: %s    Computer Score: %s    %s's Turn"
    surf, rect = render_text(tpl % (scores[player_tile], scores[computer_tile], turn.title()), TEXTBGCOLOR1, bottomleft=(10, WINDOWHEIGHT-5))
    DISPLAYSURF.blit(surf, rect)

def reset_board(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE
    board[3][3] = white_tile
    board[3][4] = black_tile
    board[4][3] = black_tile
    board[4][4] = white_tile

def get_new_board():
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    return board

def is_valid_move(board, tile, xstart, ystart):
    """If it is a valid move, returns a list of spaces of the captured pieces."""
    if board[xstart][ystart] != EMPTY_SPACE or not is_on_board(xstart, ystart):
        return False

    board[xstart][ystart] = tile    # temporarily set the tile on the board.
    other_tile = black_tile if tile==white_tile else white_tile

    tiles_to_flip = []
    # check each of the eight directions:
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if is_on_board(x, y) and board[x][y] == other_tile:
            # The piece belongs to the other player next to our piece.
            x += xdirection
            y += ydirection
            if not is_on_board(x, y):
                continue

            while board[x][y] == other_tile:
                x += xdirection
                y += ydirection
                if not is_on_board(x, y):
                    break
            if not is_on_board(x, y):
                continue

            if board[x][y] == tile:
                # There are pieces to flip over. Go in the reverse
                # direction until we reach the original space, noting all
                # the tiles along the way.
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tiles_to_flip.append([x, y])

    board[xstart][ystart] = EMPTY_SPACE
    return tiles_to_flip or False

def is_on_board(x, y):
    return bool(0 <= x < BOARDWIDTH and 0 <= y < BOARDHEIGHT)

def get_board_with_valid_moves(board, tile):
    # Returns a new board with hint markings.
    dupe_board = copy.deepcopy(board)

    for x, y in get_valid_moves(dupe_board, tile):
        dupe_board[x][y] = HINT_TILE
    return dupe_board

def get_valid_moves(board, tile):
    return [(x,y) for x in range(BOARDWIDTH) for y in range(BOARDHEIGHT) if is_valid_move(board, tile, x, y)]

def get_score_of_board(board):
    """Determine the score by counting the tiles."""
    xscore = oscore = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == white_tile:
                xscore += 1
            if board[x][y] == black_tile:
                oscore += 1
    return {white_tile:xscore, black_tile:oscore}

def enter_player_tile():
    """Show selection buttons and return [player_tile, ai_tile]."""
    text_surf = FONT.render("Do you want to be white or black?", True, TEXTCOLOR, TEXTBGCOLOR1)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    x_surf = BIGFONT.render("White", True, TEXTCOLOR, TEXTBGCOLOR1)
    x_rect = x_surf.get_rect()
    x_rect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 40)

    o_surf = BIGFONT.render("Black", True, TEXTCOLOR, TEXTBGCOLOR1)
    o_rect = o_surf.get_rect()
    o_rect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 40)

    DISPLAYSURF.blit(text_surf, text_rect)
    DISPLAYSURF.blit(x_surf, x_rect)
    DISPLAYSURF.blit(o_surf, o_rect)

    while True:
        # Keep looping until the player has clicked on a color.
        check_for_quit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                if x_rect.collidepoint(event.pos):
                    return [white_tile, black_tile]
                elif o_rect.collidepoint(event.pos):
                    return [black_tile, white_tile]
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def make_move(board, tile, xstart, ystart, real_move=False):
    """ Place the tile on the board at xstart, ystart, and flip tiles
        Returns False if this is an invalid move, True if it is valid.
    """
    tiles_to_flip = is_valid_move(board, tile, xstart, ystart)
    if tiles_to_flip:
        board[xstart][ystart] = tile
        if real_move:
            animate_tile_change(tiles_to_flip, tile, (xstart, ystart))

        for x, y in tiles_to_flip:
            board[x][y] = tile
        return True

def is_on_corner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or  (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or (x == BOARDWIDTH and y == BOARDHEIGHT)

def get_computer_move(board, computer_tile):
    """Performace issue: adding undo method to board would be faster than deepcopy."""
    possible_moves = get_valid_moves(board, computer_tile)
    random.shuffle(possible_moves)

    # always go for a corner if available.
    for loc in possible_moves:
        if is_on_corner(*loc): return loc

    # Go through all possible moves and remember the best scoring move
    best_score = -1
    for loc in possible_moves:
        dupe_board = copy.deepcopy(board)
        make_move(dupe_board, computer_tile, *loc)
        score = get_score_of_board(dupe_board)[computer_tile]
        if score > best_score:
            best_move = loc
            best_score = score
    return best_move

def key_up(event, key):
    return event.key==key and event.type==KEYUP

def check_for_quit():
    for event in pygame.event.get((QUIT, KEYUP)):
        if event.type==QUIT or key_up(event, K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
