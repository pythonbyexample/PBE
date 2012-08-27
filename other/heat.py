"""
file: heat.py

Based on steady-state.py.

This defines not only the steady state model but also the PyGame code necessary to
visualize it using Surfarray.
"""
import sys
import math
import time
import Numeric

import pygame
from pygame.locals import *
from pygame import surfarray

def drawfield( screen, scale_surface, pixels ):
    surfarray.blit_array( scale_surface, pixels )
    temp = pygame.transform.scale(scale_surface, screen.get_size())
    screen.blit(temp, (0,0))
    return

def createPalette( ):
    r,g,b = -1,0,256
    palette = []
    for i in xrange(0,256):
        r += 1
        b -= 1
        palette.append( (r,g,b) )
    return palette    

def main( N=100, EPSILON = 0.01 ):
    # Stores Old(previous timestep) Values 
    u = Numeric.zeros( (N,N),Numeric.Float32 )
    # New(current/next timestep) Values
    w = Numeric.zeros( (N,N),Numeric.Float32 )
    pixels = Numeric.zeros( (N,N), Numeric.Int32 )
    # Set boundary values and compute mean boundary value
    mean = 0.0
    # This "magic" factor is just a scaling to get the full range of our (255.0/N)
    # color palette.
    for i in xrange(N):
        # 3 sides @ 100.0 degrees
        u[i][0] = 100.0
        pixels[i][0] = int(100 * (255.0/N))
        u[i][N-1] = 100.0
        pixels[i][N-1] = int(100 * (255.0/N))
        u[0][i]  = 100.0
        pixels[0][i] = int(100 * (255.0/N))
        # 1 side @ 0 degrees
    for i in xrange(N):
        u[N-1][i] = 0.0
        pixels[N-1][i] = 0.0
        
    mean += Numeric.sum(u[:][0])
    mean += Numeric.sum(u[:][N-1])
    mean += Numeric.sum(u[0][:])
    mean += Numeric.sum(u[N-1][:])
    mean /= (4.0 * N)

    # Initialize interior values:
    print mean
    for i in xrange(1,N-1):
        for j in xrange(1,N-1):
            u[i][j] = mean
            pixels[i][j] = int(mean * (255.0/N))
    

    WINSIZE = 640,480
    ARRAYSIZE = N,N
    
    # Initialize the Pygame Engine!
    pygame.init()
    screen = pygame.display.set_mode(WINSIZE,0,8)
    scale_screen = pygame.surface.Surface( ARRAYSIZE,0,8 )
    pygame.display.set_caption('Heat')
    black = 20,20, 40
    palette = createPalette()
    screen.fill(black)
    scale_screen.fill(black)
    screen.set_palette( palette )
    scale_screen.set_palette( palette )
    
    # Compute Steady-State solution:
    done = False # Is true when we reach steady state
    userquit = False # is true only when the user is done watching
    iterations = 0
    while not userquit:
        iterations += 1
        delta = 0.0
        if not done:
            for i in xrange(1,N-1):
                for j in xrange(1,N-1):
                    w[i][j] = u[i-1][j] + u[i+1][j] + u[i][j-1] + u[i][j+1]
                    w[i][j] = w[i][j] / 4.0
                    d = math.fabs( w[i][j] - u[i][j] ) 
                    if( d > delta ):
                        delta = d
            if( delta <= EPSILON ):
                done = True
            # Copy new interior state to old:
            for i in xrange(1,N-1):
                for j in xrange(1,N-1):
                    u[i][j] = w[i][j]
                    pixels[i][j] = int(w[i][j] * (255.0/N)) 
        # Draw
        drawfield( screen, scale_screen, pixels )
        pygame.display.update()
        # Handle Events
        events = pygame.event.get( )
        for e in events:
            if( e.type == QUIT ):
                userquit = True
                break
            elif (e.type == KEYDOWN):
                if( e.key == K_ESCAPE ):
                    userquit = True
                    break
                if( e.key == K_f ):
                    pygame.display.toggle_fullscreen()

    # Print Solution:
    print u
    return iterations
                    
if __name__=="__main__":
    print "Starting Steady State Example:"
    if( len(sys.argv) >= 2 ):
        N = int( sys.argv[1] )
    else:
        N = 100
    start = time.time()
    iterations = main(N)
    end = time.time()
    print "Finished Steady State Example in",end - start,"and",iterations,"iterations."
