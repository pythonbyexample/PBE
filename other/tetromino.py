#!/usr/bin/env python

# Imports {{{
# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
import random, time, pygame, sys
from pygame.locals import *

FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5
# }}}

# Templates {{{
S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}
# }}}


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK    = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT   = pygame.font.Font("freesansbold.ttf", 18)
    BIGFONT     = pygame.font.Font("freesansbold.ttf", 100)
    pygame.display.set_caption("Tetromino")

    show_text_screen("Tetromino")
    while True: # game loop
        # if random.randint(0, 1) == 0:
        #     pygame.mixer.music.load('tetrisb.mid')
        # else:
        #     pygame.mixer.music.load('tetrisc.mid')
        # pygame.mixer.music.play(-1, 0.0)

        run_game()
        # pygame.mixer.music.stop()
        show_text_screen("Game Over")


def run_game():
    # setup variables for the start of the game
    board                   = get_blank_board()
    last_move_down_time     = time.time()
    last_move_sideways_time = time.time()
    last_fall_time          = time.time()
    moving_down             = False # note: there is no moving_up variable
    moving_left             = False
    moving_right            = False
    score                   = 0
    level, fall_freq        = calculate_level_and_fall_freq(score)

    falling_piece           = get_new_piece()
    next_piece              = get_new_piece()

    while True:
        if falling_piece == None:
            # No falling piece in play, so start a new piece at the top
            falling_piece  = next_piece
            next_piece     = get_new_piece()
            last_fall_time = time.time()

            if not is_valid_position(board, falling_piece):
                return

        check_for_quit()
        for event in pygame.event.get(): # event handling loop
            if event.type == KEYUP:
                if (event.key == K_p):
                    # Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.stop()
                    show_text_screen("Paused")
                    pygame.mixer.music.play(-1, 0.0)
                    last_fall_time          = time.time()
                    last_move_down_time     = time.time()
                    last_move_sideways_time = time.time()
                elif (event.key == K_LEFT or event.key == K_a):
                    moving_left = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    moving_right = False
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = False

            elif event.type == KEYDOWN:
                # moving the piece sideways
                if (event.key == K_LEFT or event.key == K_a) and is_valid_position(board, falling_piece, adj_x=-1):
                    falling_piece['x'] -= 1
                    moving_left = True
                    moving_right = False
                    last_move_sideways_time = time.time()

                elif (event.key == K_RIGHT or event.key == K_d) and is_valid_position(board, falling_piece, adj_x=1):
                    falling_piece['x'] += 1
                    moving_right = True
                    moving_left = False
                    last_move_sideways_time = time.time()

                # rotating the piece (if there is room to rotate)
                elif (event.key == K_UP or event.key == K_w):
                    falling_piece["rotation"] = (falling_piece["rotation"] + 1) % len(PIECES[falling_piece["shape"]])
                    if not is_valid_position(board, falling_piece):
                        falling_piece["rotation"] = (falling_piece["rotation"] - 1) % len(PIECES[falling_piece["shape"]])
                elif (event.key == K_q): # rotate the other direction
                    falling_piece["rotation"] = (falling_piece["rotation"] - 1) % len(PIECES[falling_piece["shape"]])
                    if not is_valid_position(board, falling_piece):
                        falling_piece["rotation"] = (falling_piece["rotation"] + 1) % len(PIECES[falling_piece["shape"]])

                # making the piece fall faster with the down key
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = True
                    if is_valid_position(board, falling_piece, adj_y=1):
                        falling_piece['y'] += 1
                    last_move_down_time = time.time()

                # move the current piece all the way down
                elif event.key == K_SPACE:
                    moving_down = False
                    moving_left = False
                    moving_right = False
                    for i in range(1, BOARDHEIGHT):
                        if not is_valid_position(board, falling_piece, adj_y=i):
                            break
                    falling_piece["y"] += i - 1

        # handle moving the piece because of user input
        if (moving_left or moving_right) and time.time() - last_move_sideways_time > MOVESIDEWAYSFREQ:
            if moving_left and is_valid_position(board, falling_piece, adj_x=-1):
                falling_piece["x"] -= 1
            elif moving_right and is_valid_position(board, falling_piece, adj_x=1):
                falling_piece["x"] += 1
            last_move_sideways_time = time.time()

        if moving_down and time.time() - last_move_down_time > MOVEDOWNFREQ and is_valid_position(board, falling_piece, adj_y=1):
            falling_piece["y"] += 1
            last_move_down_time = time.time()

        # let the piece fall if it is time to fall
        if time.time() - last_fall_time > fall_freq:
            # see if the piece has landed
            if not is_valid_position(board, falling_piece, adj_y=1):
                # falling piece has landed, set it on the board
                add_to_board(board, falling_piece)
                score += remove_complete_lines(board)
                level, fall_freq = calculate_level_and_fall_freq(score)
                falling_piece = None
            else:
                # piece did not land, just move the piece down
                falling_piece["y"] += 1
                last_fall_time = time.time()

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_status(score, level)
        draw_next_piece(next_piece)
        if falling_piece != None:
            draw_piece(falling_piece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def check_for_key_press():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    check_for_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def show_text_screen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the text
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the additional "Press a key to play." text.
    press_key_surf, press_key_rect = make_text_objs('Press a key to play.', BASICFONT, TEXTCOLOR)
    press_key_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(press_key_surf, press_key_rect)

    while check_for_key_press() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def check_for_quit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calculate_level_and_fall_freq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fall_freq = 0.27 - (level * 0.02)
    return level, fall_freq


def get_new_piece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    new_piece = {"shape": shape,
                "rotation": random.randint(0, len(PIECES[shape]) - 1),
                "x": int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                "y": -2, # start it above the board (i.e. less than 0)
                "color": random.randint(0, len(COLORS)-1)}
    return new_piece


def add_to_board(board, piece):
    # fill in the board based on piece"s location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece["shape"]][piece["rotation"]][y][x] != BLANK:
                board[x + piece["x"]][y + piece["y"]] = piece["color"]


def get_blank_board():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def is_on_board(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def is_valid_position(board, piece, adj_x=0, adj_y=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            is_above_board = y + piece["y"] + adj_y < 0
            if is_above_board or PIECES[piece["shape"]][piece["rotation"]][y][x] == BLANK:
                continue
            if not is_on_board(x + piece["x"] + adj_x, y + piece["y"] + adj_y):
                return False
            if board[x + piece["x"] + adj_x][y + piece["y"] + adj_y] != BLANK:
                return False
    return True


def is_complete_line(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def remove_complete_lines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    num_lines_removed = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if is_complete_line(board, y):
            # Remove the line and pull boxes down by one line.
            for pull_down_y in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pull_down_y] = board[x][pull_down_y-1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            num_lines_removed += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return num_lines_removed


def convert_to_pixel_coords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def draw_box(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convert_to_pixel_coords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def draw_board(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            draw_box(x, y, board[x][y])


def draw_status(score, level):
    # draw the score text
    score_surf = BASICFONT.render("Score: %s" % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(score_surf, score_rect)

    # draw the level text
    level_surf = BASICFONT.render("Level: %s" % level, True, TEXTCOLOR)
    level_rect = level_surf.get_rect()
    level_rect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(level_surf, level_rect)


def draw_piece(piece, pixelx=None, pixely=None):
    shape_to_draw = PIECES[piece["shape"]][piece["rotation"]]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn"t been specified, use the location stored in the piece data structure
        pixelx, pixely = convert_to_pixel_coords(piece["x"], piece["y"])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shape_to_draw[y][x] != BLANK:
                draw_box(None, None, piece["color"], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def draw_next_piece(piece):
    # draw the "next" text
    next_surf = BASICFONT.render("Next:", True, TEXTCOLOR)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(next_surf, next_rect)
    # draw the "next" piece
    draw_piece(piece, pixelx=WINDOWWIDTH-120, pixely=100)


if __name__ == '__main__':
    main()
