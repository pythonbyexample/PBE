#!/usr/bin/env python
from pygame import *
from random import sample,randint
font.init()
police = font.Font(None,50)

def make_rect(x, y):
    scr.fill(-1, (x, y, 100, 100)).inflate(-25,-25)

def find_index(player):
    for i in range(9):
        if grid[i] == '':
            grid[i] = player
            if [player]*3 in combi():
                grid[i] = ''
                return i
            grid[i] = ''
    return None

def play():
    if player:
        while True:
            ev = event.wait()
            if ev.type == MOUSEBUTTONDOWN:
                index = ev.pos[0]/101*3+ev.pos[1]/101
                if grid[index] == '':
                    grid[index] = player
                    display.update(draw.ellipse(scr,0xa00000,rects[index],10))
                    break
    else:
        index = find_index(player)
        if index == None: index = find_index(~player)
        if index == None:
            while grid[ai[-1]] != '': ai.pop()
            index = ai.pop()
        grid[index] = player
        draw.line(scr,0x0000a0,rects[index].topright,rects[index].bottomleft,10)
        display.update(draw.line(scr,0x0000a0,rects[index].topleft,rects[index].bottomright,10))

def game():
    scr = display.set_mode((302,302))
    rects = [make_rect(x, y) for x in 0,101,202 for y in 0,101,202]
    display.flip()

    grid = ['']*9
    combi = lambda: (grid[0:3],grid[3:6],grid[6:9],grid[0:7:3],grid[1:8:3],grid[2:9:3],grid[0:9:4],grid[2:7:2])
    ai = sample(range(9),9)
    player = randint(-1,0)

    play()
    for coup in range(9):
        if coup == 8:
            txt = police.render("nobody wins",1,(0,0,0),(240,240,255))
            break
        player = ~player
        play()
        if [player]*3 in combi():
            txt = police.render(("pc","human")[player]+" wins",1,(0,0,0),(240,240,255))
            break
    rect = txt.get_rect()
    rect.center = 156,156
    display.update(scr.blit(txt,rect))

game()
while True:
    ev = event.wait()
    if ev.type == QUIT: break
    elif ev.type == MOUSEBUTTONDOWN: game()
