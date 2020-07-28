# -*- coding: utf-8 -*-
import os
import pygame

from defines import NORMAL, ATOUT


class Card(pygame.sprite.Sprite):
    def __init__(self, value, color, client, translate=False):
        ## Coinche part
        if translate == True:
            name = self.translate_name(name)
        self.name = value + " " + color
        self.color = color
        self.value = value
        self.is_atout = False
        self.order = NORMAL
        self.client = client
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
        val = self.value
        color = self.color
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
        if color == "pique":
            path += "pique.png"
        elif color == "coeur":
            path += "coeur.png"
        elif color == "carreau":
            path += "carreau.png"
        elif color == "trefle":
            path += "trefle.png"

        return path

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
        elif self.color == atout:
            self.is_atout = True
            self.order = ATOUT
        else:
            self.is_atout = False
            self.order = NORMAL

    # used to sort
    def __lt__(self, other):
        if self.client.atout == "coeur":
            colors = ["coeur", "pique", "carreau", "trefle"]
        elif self.client.atout == "trefle":
            colors = ["trefle", "coeur", "pique", "carreau"]
        elif self.client.atout == "carreau":
            colors = ["carreau", "pique", "coeur", "trefle"]
        else:
            colors = ["pique", "coeur", "trefle", "carreau"]
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
        return self.name

    def __repr__(self):
        return self.name
