# -*- coding: utf-8 -*-
import os
import pygame

from defines import NORMAL, TRAD, ATOUT


class Card(pygame.sprite.Sprite):
    def __init__(self, name, client, translate=False):
        ## Coinche part
        if translate == True:
            name = self.translate_name(name)
        self.name = name
        self.color = name[-1]
        self.value = name[:-1]
        self.is_atout = False
        self.order = NORMAL
        self.client = client
        self.str = self.strize(name)
        self.up = False

        ## Sprite part
        super().__init__()
        # load sprite
        self.image = pygame.image.load(self.get_path_sprite())
        self.image = pygame.transform.scale(self.image, (80, 120))
        self.image = self.image.convert()
        self.rect = self.image.get_rect()

        # positionne sprite
        self.move = 15
        self.positionne(0)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def moveUp(self):
        self.rect.y -= self.move
        self.up = True

    def moveDown(self):
        if self.up == True:
            self.rect.y += self.move
            self.up = False

    def positionne(self, num):
        self.rect.x =  50 + (num * 85)
        self.rect.y = 400

    def get_path_sprite(self):
        path = os.getcwd()
        path += "/card_images/"
        val = self.name[:-1]
        color = self.name[-1]
        if val == "AS":
            path += "as"
        elif val == "K":
            path += "roi"
        elif val == "Q":
            path += "dame"
        elif val == "J":
            path += "valet"
        else:
            path += val
        path += "_"
        if color == "♤":
            path += "pique.png"
        elif color == "♡":
            path += "coeur.png"
        elif color == "♢":
            path += "carreau.png"
        elif color == "♧":
            path += "trefle.png"

        return path

    def strize(self, s):
        if self.color == "♡": # red
            return '\033[91m' + s + '\033[0m'
        elif self.color == "♢": # blue
            return '\033[94m' + s + '\033[0m'
        if self.color == "♧": # green
            return '\033[92m' + s + '\033[0m'
        else:
            return s

    def translate_name(self, name):
        mots = name.split(" ")
        if len(mots) != 2:
            return "wrong"
        try:
            mots[0] = mots[0].upper()
            mots[1] = mots[1].lower()
            return mots[0] + TRAD[mots[1]]
        except KeyError:
            return "wrong"

    def position(self):
        return self.order.index(self.value)

    def set_atout(self, atout):
        if atout == "s_a":
            self.is_atout = False
            self.order = NORMAL
        elif atout == "t_a":
            self.is_atout = True
            self.order = ATOUT
        elif self.color == TRAD[atout]:
            self.is_atout = True
            self.order = ATOUT
        else:
            self.is_atout = False
            self.order = NORMAL

    # used to sort
    def __lt__(self, other):
        if self.client.atout == "coeur":
             colors = ["♡", "♤","♢", "♧"]
        elif self.client.atout == "trefle":
            colors = ["♧", "♡", "♤", "♢"]
        elif self.client.atout == "carreau":
            colors = ["♢", "♤","♡", "♧"]
        else:
            colors = ["♤", "♡", "♧", "♢"]
        if self.color == other.color:
            return self.position() < other.position()
        else:
            return colors.index(self.color) < colors.index(other.color)

    # used to get best card
    def __gt__(self, other):
        if self.color == other.color:
            return self.position() < other.position()
        else:
            if self.is_atout:
                return True
            elif other.is_atout:
                return False
            else:
                if self.color == self.client.current_color:
                    return True
                else:
                    return False

    def __eq__(self, other):
        try:
            if self.name == other.name:
                return True
            return False
        except AttributeError:
            return False

    def __str__(self):
        return self.str

    def __repr__(self):
        return self.str
