# -*- coding: utf-8 -*-
import sys
import pygame

from defines import BLACK, WHITE, GREY


class TextSprite():
    def __init__(self, msg, position, font_size, font_color=BLACK, font_type=None, timer=None):
        self.msg = msg
        self.position = position
        self.font_size = font_size
        self.font_color = font_color
        self.font_type = font_type
        self.font_object = pygame.font.Font(font_type, font_size)
        self.text = self.font_object.render(msg, 1, font_color)

    def update_msg(self, new_msg):
        self.msg = new_msg
        self.text = self.font_object.render(new_msg, 1, self.font_color)

    def draw(self, screen):
        if self.msg != "":
            screen.blit(self.text, self.position)


class InputSprite(TextSprite):
    def __init__(self, msg, position, font_size, font_color=BLACK, font_type=None):
        super().__init__(msg, position, font_size, font_color, font_type)
        self.returned = False
        self.uppercase = False

    def add_ch(self, ch):
        if self.returned == False:
            if (ch >= 97 and ch <= 122) and self.uppercase==True:
                ch -= 32
            msg = self.msg + chr(ch)
            self.update_msg(msg)

    def end(self):
        self.returned = True

    def remove_ch(self):
        if len(self.msg) != 0 and self.returned == False:
            msg = self.msg[:-1]
            self.update_msg(msg)

    def reset(self):
        self.msg = ""
        self.returned = False
        self.uppercase = False
        self.update_msg(self.msg)

    def uppercase(self):
        if self.returned == False:
            self.uppercase = not self.uppercase

class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, txt, pos, size=(40, 40)):
        super().__init__()
        self.color = WHITE  # the static (normal) color
        self.bg = self.color  # actual background color, can change on mouseover
        self.fg = BLACK # text color

        self.font = pygame.font.Font(None, 20)
        self.txt = str(txt)
        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[int(s//2) for s in size])

        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(center=pos)

    def draw(self, screen):
        self.mouseover()

        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surface, self.rect)

    def mouseover(self):
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = GREY


    def call_back(self):
        self.color = GREY
        return self.txt

class PlayerSpriteHandler():
    def __init__(self, name, pos):
        self.name = name
        if pos == "Ouest":
            self.x_ann = 10
            self.y_ann = 300
            self.x_card = 250
            self.y_card = 140
            self.x_name = 10
            self.y_name = 280
        elif pos == "Nord":
            self.x_ann = 350
            self.y_ann = 30
            self.x_card = 350
            self.y_card = 50
            self.x_name = 350
            self.y_name = 10
        elif pos == "Est":
            self.x_ann = 700
            self.y_ann = 300
            self.x_card = 450
            self.y_card = 140
            self.x_name = 700
            self.y_name = 280
        elif pos == "Sud":
            self.x_ann = 350
            self.y_ann = 380
            self.x_card = 350
            self.y_card = 200
            self.x_name = 350
            self.y_name = 580
        else:
            print("ERROR")
            sys.exit()

        self.pos = pos
        self.last_annonce = None
        self.nameSprite = TextSprite(self.name, [self.x_name, self.y_name], 20)
        self.annonceSprite = TextSprite("", [self.x_ann, self.y_ann], 20)
        self.card = None

    def annonce(self, val):
        self.last_annonce = val
        if val == None:
            val = ""
        self.annonceSprite.update_msg(val)

    def play(self, card):
        self.card = card
        self.card.rect.x = self.x_card
        self.card.rect.y = self.y_card

    def draw(self, screen):
        self.nameSprite.draw(screen)
        self.annonceSprite.draw(screen)
        if self.card:
            self.card.draw(screen)
#def getKey():
#    while 1:
#        event = pygame.event.poll()
#        if event.type == KEYDOWN:
#            return event.key
#        else:
#            pass
#
#def popup(screen, message, width, height, x , y, bgColor, textColor):
#    fontobject = pygame.font.Font(None,25)
#    pygame.draw.rect(screen, bgColor, (x, y, width, height), 0)
#    pygame.draw.rect(screen, (255, 255, 255), (x, y - 5, width, height), 1)
#    if len(message) != 0:
#        screen.blit(fontobject.render(message, 1, textColor), (x + 5, y))
#    pygame.display.flip()
#
#def get_input(screen, width, height, x, y, bgcolor, textcolor):
#    input = []
#    popup(screen, "", width, height, x, y, bgcolor, textcolor)
#    upperCase = False
#    while 1:
#        inkey = getKey()
#        if inkey == K_BACKSPACE:
#            input = input[0:-1]
#        elif inkey == K_RETURN:
#            return "".join(input)
#        elif inkey == K_LSHIFT or inkey == K_RSHIFT:
#            upperCase = not upperCase
#        elif inkey <= 255:
#            if (inkey>=97 and inkey<=122) and upperCase==True:
#                inkey-=32
#            input.append(chr(inkey))
#        popup(screen, "".join(input), width, height, x, y, bgcolor, textcolor)

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
