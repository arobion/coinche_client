# -*- coding: utf-8 -*-
import random
import sys
import time
import pygame
from pygame.locals import KEYDOWN, K_BACKSPACE, K_RETURN

from pygame_utils import (
        TextSprite, InputSprite, ButtonSprite, PlayerSpriteHandler,
        calc_buttonValue_pos, calc_buttonColor_pos,
    )
from card import Card
from defines import GREEN, WHITE, BLACK, FRAMERATE, TIME_SCORE
from server_com import Client


class GuiHandler():
    def __init__(self):
        # gui_vars
        self.state = None
        self.screen = None
        self.clock = None
        self.ip = None
        self.name = None
        self.sprites = []

        # pointer to diplay_function
        self.display_func = None

        self.actions = {
            "name" : self.create_name_screen,
            "make_annonce" : self.make_annonce_screen,
            "play" : self.play,
        }
        self.infos = {
            "get_cards" : self.get_cards,
            "annonce" : self.get_annonce,
            "annonce_finale" : self.get_contract,
            "card" : self.get_card,
            "score" : self.get_score,
            "print" : self.echo,
        }

        # server_vars
        self.client = Client()

        # coinche_vars
        self.hand = [] # contains sprites
        self.pli_courant = []
        self.highest_annonce = 0
        self.atout = None
        self.players = {}

        # tmp_vars
        self.tmp_val = None
        self.tmp_color = None
        self.playables = []

    def init(self):
        self.screen.fill(GREEN)
        self.state += 1

    def quit(self):
        print('quit on exit')
        sys.exit(0)

    def wait_players(self):
        text = pygame.font.Font(None, 40).render("Waiting for 4 players, don't worry", 1, BLACK)
        self.screen.blit(text, (200,50))

    def nothing(self):
        pass

    def construct_table(self, args):
        player1 = args[1]
        player2 = args[3]
        player3 = args[5]
        player4 = args[7]
        self.players = {}
        if player1 == self.name:
            self.players[player2] = PlayerSpriteHandler(player2, "Ouest")
            self.players[player3] = PlayerSpriteHandler(player3, "Nord")
            self.players[player4] = PlayerSpriteHandler(player4, "Est")
        elif player2 == self.name:
            self.players[player3] = PlayerSpriteHandler(player3, "Ouest")
            self.players[player4] = PlayerSpriteHandler(player4, "Nord")
            self.players[player1] = PlayerSpriteHandler(player1, "Est")
        elif player3 == self.name:
            self.players[player4] = PlayerSpriteHandler(player4, "Ouest")
            self.players[player1] = PlayerSpriteHandler(player1, "Nord")
            self.players[player2] = PlayerSpriteHandler(player2, "Est")
        elif player4 == self.name:
            self.players[player1] = PlayerSpriteHandler(player1, "Ouest")
            self.players[player2] = PlayerSpriteHandler(player2, "Nord")
            self.players[player3] = PlayerSpriteHandler(player3, "Est")
        self.players[self.name] = PlayerSpriteHandler(self.name, "Sud")

    def echo(self, args):
        if args[0] == "1" and args[2] == "2":
            self.construct_table(args)
        elif args[1] == "remporte":
            self.players[args[0]].annonce("win")

    def get_score(self, args):
        msg = " ".join(args)
        self.sprites.append(TextSprite(msg, (30, 450), 28))
        timer = time.time() + TIME_SCORE
        while time.time() < timer:
            self.listen_pygame_event()
            self.screen.fill(GREEN)
            for player in self.players.values():
                player.draw(self.screen)
            for sprite in self.sprites:
                sprite.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FRAMERATE)
        for player in self.players.values():
            player.card = None

    def display_annonce(self):
#        for card in self.hand:
#            card.draw(self.screen)
        for button in self.buttons_value:
            button.draw(self.screen)
        for button in self.buttons_color:
            button.draw(self.screen)

    def gui_sort(self):
        i = 0
        for elem in self.hand:
            elem.positionne(i)
            i += 1

    def get_contract(self, args):
        self.hand.sort()
        self.gui_sort()
        for player in self.players.values():
            player.annonce("")
        self.sprites.append(TextSprite("contrat : {} {}".format(self.highest_annonce, self.atout), (640, 580), 20))
        self.state = 1

    def get_card(self, args):
        joueur = args.pop(0)
        card = ""
        for elem in args:
            card += elem + " "
        card = card[:-1]
        card = Card(card, self)
        self.pli_courant.append(card)
        if len(self.pli_courant) == 4:
            self.pli_courant = []
        if len(self.pli_courant) == 1:
            self.current_color = card.color
            for elem in self.players.values():
                elem.card = None
                elem.annonce("")
        card.set_atout(self.atout)
        self.players[joueur].play(Card(card.name, self))

    def get_cards(self, args):
        self.hand = []
        self.sprites = []
        self.highest_annonce = 0
        self.pli_courant = []
        self.atout = None
        for card in args:
            if card != '':
                self.hand.append(Card(card, self))
        self.hand.sort()
        self.gui_sort()
        self.display_func = self.nothing
        self.state = 1

    def update_annonce(self, val):
        if val == "passe" or val == "0":
            return
        mots = val.split(" ")
        self.highest_annonce = int(mots[0])
        self.atout = mots[1]
        for card in self.hand:
            card.set_atout(self.atout)

    def get_annonce(self, args):
        joueur = args.pop(0)
        val = ""
        for elem in args:
            val += elem + " "
        val = val[:-1]
        self.update_annonce(val)
        if val == "0":
            val = "passe"
        self.players[joueur].annonce(val)

    def get_same_colors(self, card):
        return [elem for elem in self.hand if elem.color == card.color]

    def get_atouts(self):
        return [elem for elem in self.hand if elem.is_atout == True]

    def get_best_card(self):
        best = self.pli_courant[0]
        for card in self.pli_courant:
            if card > best:
                best = card
        return best

    def partenaire_win(self):
        if len(self.pli_courant) == 1:
            return False
        best_card = self.get_best_card()
        if best_card == self.pli_courant[-2]:
            return True
        return False

    def get_atout_above(self, lst):
        best = None
        for card in self.pli_courant:
            if card.is_atout == True:
                if best == None:
                    best = card
                elif best.position() > card.position():
                    best = card
        if best == None:
            return lst
        ret = []
        for card in lst:
            if best.position() > card.position():
                ret.append(card)
        if ret == []:
            return lst
        return ret

    def get_playables(self):
        if len(self.pli_courant) == 0:
            return self.hand
        same_colors = self.get_same_colors(self.pli_courant[0])
        check_atout = 0
        if same_colors != []:
            playables = same_colors
            if playables[0].is_atout:
                check_atout = 1
        else:
            if self.partenaire_win() == True:
                playables = self.hand
                check_atout = 0
            else:
                atouts = self.get_atouts()
                if atouts == []:
                    playables = self.hand
                    check_atout = 0
                else:
                    playables = atouts
                    check_atout = 1
        if check_atout == 1:
            playables = self.get_atout_above(playables)
        return playables

    def play(self):
        self.playables = self.get_playables()
        if len(self.playables) != len(self.hand):
            for card in self.playables:
                card.moveUp()
        self.state = 3

    def make_annonce_screen(self):
        self.tmp_val = None
        self.tmp_color = None
        self.buttons_value = []
        self.buttons_color = []
        if self.highest_annonce != 0:
            dep = self.highest_annonce + 10
        else:
            dep = 80
        for val in range(dep, 181, 10):
            self.buttons_value.append(ButtonSprite(val, calc_buttonValue_pos(dep, val)))
        self.buttons_value.append(ButtonSprite("passe", [350, 280], size=(100, 30)))
        for color in ["coeur", "pique", "carreau", "trefle"]:
            self.buttons_color.append(ButtonSprite(color, calc_buttonColor_pos(color), size=(100, 30)))
        self.display_func = self.display_annonce
        self.state = 2

    def get_from_server(self):
        if len(self.client.queue) != 0:
            msg = self.client.queue.pop(0).split(" ")
            if msg[0] == "info":
                self.infos[msg[1]](msg[2:])
            if msg[0] == "action":
                self.actions[msg[1]]()

    def check_values(self, pos):
        for button in self.buttons_value:
            if button.rect.collidepoint(pos):
                self.tmp_val = button.call_back()
            else:
                button.color = WHITE

    def check_color(self, pos):
        for button in self.buttons_color:
            if button.rect.collidepoint(pos):
                self.tmp_color = button.call_back()
            else:
                button.color = WHITE

    def parse_annonce(self):
        pos = pygame.mouse.get_pos()
        self.check_values(pos)
        self.check_color(pos)
        if self.tmp_val == "passe":
            self.client.send_server("annonce passe")
            self.state = 1
            self.display_func = self.nothing
            return
        if self.tmp_val and self.tmp_color:
            self.client.send_server("annonce " + self.tmp_val + " " + self.tmp_color)
            self.state = 1
            self.display_func = self.nothing
            return

    def parse_card(self):
        pos = pygame.mouse.get_pos()
        for card in self.hand:
            if card.rect.collidepoint(pos) and card in self.playables:
                self.client.send_server("play " + card.name)
                self.hand.remove(card)
                for elem in self.playables:
                    elem.moveDown()
                self.state = 1
                return

    def check_click(self):
        if self.state == 2:
            self.parse_annonce()
        elif self.state == 3:
            self.parse_card()

    def listen_pygame_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.check_click()
            elif event.type == KEYDOWN:
                self.update_input(event.key)

    def display(self):
        self.screen.fill(GREEN)
        self.display_func()
        for card in self.hand:
            card.draw(self.screen)
        for player in self.players.values():
            player.draw(self.screen)
        for sprite in self.sprites:
            sprite.draw(self.screen)

    def main_loop(self):
        self.listen_pygame_event()

        self.get_from_server()
        self.display()
        pygame.display.flip()
        self.clock.tick(FRAMERATE)
        return True

    def update_input(self, key):
        if key == K_BACKSPACE:
            self.inputSprite.remove_ch()
        elif key == K_RETURN:
            self.inputSprite.end()
        elif key <= 255:
            self.inputSprite.add_ch(key)

    def wait_ip(self):
        pygame.draw.rect(self.screen, WHITE, (240, 145, 200, 30), 1)
        if self.inputSprite.returned == True:
            ip = self.inputSprite.msg
            if ip == '':
                ip = 'localhost'
            self.client.start(ip)
            self.display_func = self.nothing
            self.inputSprite.msg = ""
            self.sprites = []

    def wait_name(self):
        pygame.draw.rect(self.screen, WHITE, (202, 195, 200, 30), 1)
        if self.inputSprite.returned == True:
            self.name = self.inputSprite.msg
            if self.name == '':
                self.name = "player_{}".format(random.randint(0, 10000))
            self.client.send_server(self.name)
            self.display_func = self.wait_players
            self.inputSprite.msg = ""
            self.sprites = []

    def create_ip_screen(self):
        self.sprites.append(TextSprite("Welcome", (280,50), 40))
        self.sprites.append(TextSprite("Entrer l'IP du serveur : ", (50,150), 25))
        self.inputSprite = InputSprite("", (245, 150), 25)
        self.sprites.append(self.inputSprite)
        self.display_func = self.wait_ip

    def create_name_screen(self):
        self.sprites.append(TextSprite("Successfully connected to the server", (100, 50), 40))
        self.sprites.append(TextSprite("Waiting for other players", (160, 100), 40))
        self.sprites.append(TextSprite("Enter your name : ", (50, 200), 25))

        self.inputSprite.reset()
        self.inputSprite.position = (207, 200)
        self.sprites.append(self.inputSprite)
        self.display_func = self.wait_name

    def start(self):
        ### initializing GUI
        pygame.init()
        pygame.display.set_icon(pygame.image.load("card_images/valet_pique.png"))
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Pycoinche")
        self.display_func = self.create_ip_screen # first screen

        while self.main_loop() == True:
            pass
        print("exit with false")

gui = GuiHandler()
gui.start()
