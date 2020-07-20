import pygame
from pygame.locals import *

def getKey():
    while 1:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            return event.key
        else:
            pass

def popup(screen, message, width, height, x , y, bgColor, textColor):
    fontobject = pygame.font.Font(None,25)
    pygame.draw.rect(screen, bgColor, (x, y, width, height), 0)
    pygame.draw.rect(screen, (255, 255, 255), (x, y - 5, width, height), 1)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, textColor), (x + 5, y))
    pygame.display.flip()

def get_input(screen, width, height, x, y, bgcolor, textcolor):
    input = []
    popup(screen, "", width, height, x, y, bgcolor, textcolor)
    upperCase = False
    while 1:
        inkey = getKey()
        if inkey == K_BACKSPACE:
            input = input[0:-1]
        elif inkey == K_RETURN:
            return "".join(input)
        elif inkey == K_LSHIFT or inkey == K_RSHIFT:
            upperCase = not upperCase
        elif inkey <= 255:
            if (inkey>=97 and inkey<=122) and upperCase==True:
                inkey-=32
            input.append(chr(inkey))
        popup(screen, "".join(input), width, height, x, y, bgcolor, textcolor)

def calc_buttonValue_pos(start, pos):
    y = 150
    total = int((180 - start) / 10)
    spacing = 60
    total_size = total * spacing
    padding = 800 - total_size
    x_dep = padding / 2 
    num = int((pos - start) / 10)
    x = x_dep + (spacing * num) + 10
    return (x, y)

def calc_buttonColor_pos(name):
    y = 200
    start_x = 200
    spacing = 120
    x = {"pique": start_x, "coeur" : start_x + (spacing), "trefle" : start_x + (2 * spacing), "carreau" : start_x + (3 * spacing)}[name]
    return (x, y)
