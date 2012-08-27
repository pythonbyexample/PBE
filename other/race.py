#!/usr/bin/env python
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
WHITE_TILE     = "WHITE_TILE"
BLACK_TILE     = "BLACK_TILE"
EMPTY_SPACE    = "EMPTY_SPACE"
HINT_TILE      = "HINT_TILE"
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation

XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN


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
        if run_game() == False:
            break


def run_game():
    # Plays a single game of reversi each time this function is called.

    # Reset the board and game.
    main_board = get_new_board()
    reset_board(main_board)
    show_hints = False
    turn = random.choice(["computer", "player"])

    # Draw the starting board and ask the player what color they want.
    draw_board(main_board)
    player_tile, computer_tile = enter_player_tile()

    # Make the Surface and Rect objects for the "New Game" and "Hints" buttons
    new_game_surf = FONT.render("New Game", True, TEXTCOLOR, TEXTBGCOLOR2)
    new_game_rect = new_game_surf.get_rect()
    new_game_rect.topright = (WINDOWWIDTH - 8, 10)
    hints_surf = FONT.render("Hints", True, TEXTCOLOR, TEXTBGCOLOR2)
    hints_rect = hints_surf.get_rect()
    hints_rect.topright = (WINDOWWIDTH - 8, 40)

    while True: # main game loop
        # Keep looping for player and computer's turns.
        if turn == 'player':
            # Player's turn:
            if get_valid_moves(main_board, player_tile) == []:
                # If it's the player's turn but they
                # can't move, then end the game.
                break
            movexy = None
            while movexy == None:
                # Keep looping until the player clicks on a valid space.

                # Determine which board data structure to use for display.
                if show_hints:
                    board_to_draw = get_board_with_valid_moves(main_board, player_tile)
                else:
                    board_to_draw = main_board

                check_for_quit()
                for event in pygame.event.get(): # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        # Handle mouse click events
                        mousex, mousey = event.pos
                        if new_game_rect.collidepoint( (mousex, mousey) ):
                            # Start a new game
                            return True
                        elif hints_rect.collidepoint( (mousex, mousey) ):
                            # Toggle hints mode
                            show_hints = not show_hints
                        # movexy is set to a two-item tuple XY coordinate, or None value
                        movexy = get_space_clicked(mousex, mousey)
                        if movexy != None and not is_valid_move(main_board, player_tile, movexy[0], movexy[1]):
                            movexy = None

                # Draw the game board.
                draw_board(board_to_draw)
                draw_info(board_to_draw, player_tile, computer_tile, turn)

                # Draw the "New Game" and "Hints" buttons.
                DISPLAYSURF.blit(new_game_surf, new_game_rect)
                DISPLAYSURF.blit(hints_surf, hints_rect)

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
            DISPLAYSURF.blit(new_game_surf, new_game_rect)
            DISPLAYSURF.blit(hints_surf, hints_rect)

            # Make it look like the computer is thinking by pausing a bit.
            pause_until = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pause_until:
                pygame.display.update()

            # Make the move and end the turn.
            x, y = get_computer_move(main_board, computer_tile)
            make_move(main_board, computer_tile, x, y, True)
            if get_valid_moves(main_board, player_tile) != []:
                # Only set for the player's turn if they can make a move.
                turn = 'player'

    # Display the final score.
    draw_board(main_board)
    scores = get_score_of_board(main_board)

    # Determine the text of the message to display.
    if scores[player_tile] > scores[computer_tile]:
        text = "You beat the computer by %s points! Congratulations!" % \
               (scores[player_tile] - scores[computer_tile])
    elif scores[player_tile] < scores[computer_tile]:
        text = "You lost. The computer beat you by %s points." % \
               (scores[computer_tile] - scores[player_tile])
    else:
        text = "The game was a tie!"

    text_surf = FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(text_surf, text_rect)

    # Display the "Play again?" text with Yes and No buttons.
    text2Surf = BIGFONT.render("Play again?", True, TEXTCOLOR, TEXTBGCOLOR1)
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)

    # Make "Yes" button.
    yes_surf = BIGFONT.render("Yes", True, TEXTCOLOR, TEXTBGCOLOR1)
    yes_rect = yes_surf.get_rect()
    yes_rect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)

    # Make "No" button.
    no_surf = BIGFONT.render("No", True, TEXTCOLOR, TEXTBGCOLOR1)
    no_rect = no_surf.get_rect()
    no_rect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)

    while True:
        # Process events until the user clicks on Yes or No.
        check_for_quit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if yes_rect.collidepoint( (mousex, mousey) ):
                    return True
                elif no_rect.collidepoint( (mousex, mousey) ):
                    return False
        DISPLAYSURF.blit(text_surf, text_rect)
        DISPLAYSURF.blit(text2Surf, text2Rect)
        DISPLAYSURF.blit(yes_surf, yes_rect)
        DISPLAYSURF.blit(no_surf, no_rect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def translate_board_to_pixel_coord(x, y):
    return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)


def animate_tile_change(tiles_to_flip, tile_color, additional_tile):
    # Draw the additional tile that was just laid down. (Otherwise we'd
    # have to completely redraw the board & the board info.)
    if tile_color == WHITE_TILE:
        additional_tile_color = WHITE
    else:
        additional_tile_color = BLACK
    additional_tile_x, additional_tile_y = translate_board_to_pixel_coord(additional_tile[0], additional_tile[1])
    pygame.draw.circle(DISPLAYSURF, additional_tile_color, (additional_tile_x, additional_tile_y), int(SPACESIZE / 2) - 4)
    pygame.display.update()

    for rgb_values in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        if rgb_values > 255:
            rgb_values = 255
        elif rgb_values < 0:
            rgb_values = 0

        if tile_color == WHITE_TILE:
            color = tuple([rgb_values] * 3) # rgb_values goes from 0 to 255
        elif tile_color == BLACK_TILE:
            color = tuple([255 - rgb_values] * 3) # rgb_values goes from 255 to 0

        for x, y in tiles_to_flip:
            centerx, centery = translate_board_to_pixel_coord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        check_for_quit()


def draw_board(board):
    # Draw background of board.
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    # Draw grid lines of the board.
    for x in range(BOARDWIDTH + 1):
        # Draw the horizontal lines.
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx = (x * SPACESIZE) + XMARGIN
        endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
        # Draw the vertical lines.
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
        endy = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    # Draw the black & white tiles or hint spots.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translate_board_to_pixel_coord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tile_color = WHITE
                else:
                    tile_color = BLACK
                pygame.draw.circle(DISPLAYSURF, tile_color, (centerx, centery), int(SPACESIZE / 2) - 4)
            if board[x][y] == HINT_TILE:
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))


def get_space_clicked(mousex, mousey):
    # Return a tuple of two integers of the board space coordinates where
    # the mouse was clicked. (Or returns None not in any space.)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex > x * SPACESIZE + XMARGIN and \
               mousex < (x + 1) * SPACESIZE + XMARGIN and \
               mousey > y * SPACESIZE + YMARGIN and \
               mousey < (y + 1) * SPACESIZE + YMARGIN:
                return (x, y)
    return None


def draw_info(board, player_tile, computer_tile, turn):
    # Draws scores and whose turn it is at the bottom of the screen.
    scores = get_score_of_board(board)
    score_surf = FONT.render("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[player_tile]), str(scores[computer_tile]), turn.title()), True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.bottomleft = (10, WINDOWHEIGHT - 5)
    DISPLAYSURF.blit(score_surf, score_rect)


def reset_board(board):
    # Blanks out the board it is passed, and sets up starting tiles.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE

    # Add starting pieces to the center
    board[3][3] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    board[4][4] = WHITE_TILE


def get_new_board():
    # Creates a brand new, empty board data structure.
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)

    return board


def is_valid_move(board, tile, xstart, ystart):
    # Returns False if the player's move is invalid. If it is a valid
    # move, returns a list of spaces of the captured pieces.
    if board[xstart][ystart] != EMPTY_SPACE or not is_on_board(xstart, ystart):
        return False

    board[xstart][ystart] = tile # temporarily set the tile on the board.

    if tile == WHITE_TILE:
        other_tile = BLACK_TILE
    else:
        other_tile = WHITE_TILE

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
                    break # break out of while loop, continue in for loop
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

    board[xstart][ystart] = EMPTY_SPACE # make space empty
    if len(tiles_to_flip) == 0: # If no tiles flipped, this move is invalid
        return False
    return tiles_to_flip


def is_on_board(x, y):
    # Returns True if the coordinates are located on the board.
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT


def get_board_with_valid_moves(board, tile):
    # Returns a new board with hint markings.
    dupe_board = copy.deepcopy(board)

    for x, y in get_valid_moves(dupe_board, tile):
        dupe_board[x][y] = HINT_TILE
    return dupe_board


def get_valid_moves(board, tile):
    # Returns a list of (x,y) tuples of all valid moves.
    valid_moves = []

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if is_valid_move(board, tile, x, y) != False:
                valid_moves.append((x, y))
    return valid_moves


def get_score_of_board(board):
    # Determine the score by counting the tiles.
    xscore = 0
    oscore = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == WHITE_TILE:
                xscore += 1
            if board[x][y] == BLACK_TILE:
                oscore += 1
    return {WHITE_TILE:xscore, BLACK_TILE:oscore}


def enter_player_tile():
    # Draws the text and handles the mouse click events for letting
    # the player choose which color they want to be.  Returns
    # [WHITE_TILE, BLACK_TILE] if the player chooses to be White,
    # [BLACK_TILE, WHITE_TILE] if Black.

    # Create the text.
    text_surf = FONT.render("Do you want to be white or black?", True, TEXTCOLOR, TEXTBGCOLOR1)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    x_surf = BIGFONT.render("White", True, TEXTCOLOR, TEXTBGCOLOR1)
    x_rect = x_surf.get_rect()
    x_rect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 40)

    o_surf = BIGFONT.render("Black", True, TEXTCOLOR, TEXTBGCOLOR1)
    o_rect = o_surf.get_rect()
    o_rect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 40)

    while True:
        # Keep looping until the player has clicked on a color.
        check_for_quit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if x_rect.collidepoint( (mousex, mousey) ):
                    return [WHITE_TILE, BLACK_TILE]
                elif o_rect.collidepoint( (mousex, mousey) ):
                    return [BLACK_TILE, WHITE_TILE]

        # Draw the screen.
        DISPLAYSURF.blit(text_surf, text_rect)
        DISPLAYSURF.blit(x_surf, x_rect)
        DISPLAYSURF.blit(o_surf, o_rect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def make_move(board, tile, xstart, ystart, real_move=False):
    # Place the tile on the board at xstart, ystart, and flip tiles
    # Returns False if this is an invalid move, True if it is valid.
    tiles_to_flip = is_valid_move(board, tile, xstart, ystart)

    if tiles_to_flip == False:
        return False

    board[xstart][ystart] = tile

    if real_move:
        animate_tile_change(tiles_to_flip, tile, (xstart, ystart))

    for x, y in tiles_to_flip:
        board[x][y] = tile
    return True


def is_on_corner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or \
           (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or \
           (x == BOARDWIDTH and y == BOARDHEIGHT)


def get_computer_move(board, computer_tile):
    # Given a board and the computer's tile, determine where to
    # move and return that move as a [x, y] list.
    possible_moves = get_valid_moves(board, computer_tile)

    # randomize the order of the possible moves
    random.shuffle(possible_moves)

    # always go for a corner if available.
    for x, y in possible_moves:
        if is_on_corner(x, y):
            return [x, y]

    # Go through all possible moves and remember the best scoring move
    best_score = -1
    for x, y in possible_moves:
        dupe_board = copy.deepcopy(board)
        make_move(dupe_board, computer_tile, x, y)
        score = get_score_of_board(dupe_board)[computer_tile]
        if score > best_score:
            best_move = [x, y]
            best_score = score
    return best_move


def check_for_quit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
