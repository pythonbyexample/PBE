import pygame
pygame.init()

FPS          = 60
width        = 640
height       = 480
centerx      = int(width / 2)
centery      = int(height / 2)
tilesize     = 50     # width & height of each space on the board, in pixels
dimensions   = 8, 8
newgame_code = True     # return code to start a new game

bg_fn        = "bg.png"
white_fn     = "white.png"
black_fn     = "black.png"
tile_fn      = "tile.png"

white        = "white"
black        = "black"

xmargin      = int( (width - (dimensions[0] * tilesize)) / 2)
ymargin      = int( (height - (dimensions[1] * tilesize)) / 2)

cwhite       = (255, 255, 255)
cblue        = (  0,  30,  90)
cblack       = (  0,   0,   0)
cgreen       = (  0, 155,   0)
cbrightblue  = (  0,  50, 255)
cbrown       = (174,  94,   0)

def load_image(fn, scale=None):
    image = pygame.image.load(fn)
    if scale:
        image = pygame.transform.smoothscale(image, scale)
    rect = image.get_rect()
    return image, rect

class Container(object):
    def __init__(self, **kwds)  : self.__dict__.update(kwds)
    def __setitem__(self, k, v) : self.__dict__[k] = v
    def __getitem__(self, k)    : return self.__dict__[k]

colours = Container(bg1=cbrightblue, bg2=cgreen, grid=cblack, text=cwhite, hint=cbrown, white=cwhite, black=cblack, border=cblue)
