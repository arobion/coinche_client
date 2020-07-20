import sys
import threading
import random


import pygame
from pygame_utils import *
from pygame.locals import *

from server_com import Client
from card import Card

BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LAST_STATE = 4

class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, txt, pos, size=(40, 40)):
        super().__init__()
        self.color = WHITE  # the static (normal) color
        self.bg = self.color  # actual background color, can change on mouseover
        self.fg = BLACK # text color
#        self.size = size

        self.font = pygame.font.Font(None, 20)
        self.txt = str(txt)
        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in size])

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
        self.card = None
        self.text = pygame.font.Font(None, 20).render(self.name, 1, BLACK)

    def annonce(self, val):
        self.last_annonce = val
        return val

    def play(self, card):
        self.card = card
        self.card.rect.x = self.x_card
        self.card.rect.y = self.y_card

    def draw(self, screen):
        screen.blit(self.text, (self.x_name, self.y_name))

class GuiHandler():
    def __init__(self):
        # gui_vars
        self.state = None
        self.screen = None
        self.clock = None
        self.ip = None
        self.name = None

        # pointer_func_tabs
        self.display_func = {
            0 : self.wait,
            1 : self.display_cards,
            2 : self.display_annonce,
            3 : self.display_cards,
            }
        self.actions = {
            "name" : self.waiting_players_screen,
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
        self.client = None

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
        sys.exit()
    
    def wait(self):
        text = pygame.font.Font(None, 40).render("Waiting for 4 players, don't worry", 1, BLACK)
        self.screen.blit(text, (200,50))

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
            self.players[args[0]].last_annonce = "win"
        elif args[0] == "L'equipe":
            text = pygame.font.Font(None, 20).render("".join(args), 1, BLACK)
            self.screen.blit(text, (100,100))
            text = pygame.font.Font(None, 20).render("press any key to continue", 1, BLACK)
            self.screen.blit(text, (100,200))
            pygame.display.flip()
            inkey = getKey()

            
    def display_cards(self):
        pass

    def get_score(self):
        pass

    def display_annonce(self):
        for button in self.buttons_value:
            button.draw(self.screen)
        for button in self.buttons_color:
            button.draw(self.screen)

    def handle_state(self):
        self.state += 1
        if self.state > LAST_STATE:
            self.state = 2

    def print_state(self):
        self.screen.fill(GREEN)

    def gui_sort(self):
        i = 0
        for elem in self.hand:
            elem.positionne(i)
            i += 1

    def get_contract(self, args):
        self.hand.sort()
        self.gui_sort()
        for player in self.players.values():
            player.last_annonce = None
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
                elem.last_annonce = None
        card.set_atout(self.atout)
        self.players[joueur].play(Card(card.name, self))

    def get_cards(self, args):
        self.hand = []
        self.highest_annonce = 0
        self.pli_courant = []
        self.atout = None
        for card in args:
            if card != '':
                self.hand.append(Card(card, self))
        self.hand.sort()
        self.gui_sort()
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
#        if joueur != self.name:
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
        self.state = 2
        

    def waiting_players_screen(self):
        text = pygame.font.Font(None, 40).render("Successfully connected to the server", 1, BLACK)
        self.screen.blit(text, (100,50))
        text = pygame.font.Font(None, 40).render("Waiting for other players", 1, BLACK)
        self.screen.blit(text, (160,100))
        text = pygame.font.Font(None, 25).render("Enter your name : ", 1, BLACK)
        self.screen.blit(text, (50,200))
        self.name = get_input(self.screen, 200, 30, 202, 200, GREEN, BLACK)
        if self.name == '':
            self.name = "player_{}".format(random.randint(0, 10000))
        self.client._send_server(self.name)
        self.state = 0


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
            self.client._send_server("passe")
            self.state = 1
            return 
        if self.tmp_val and self.tmp_color:
            self.client._send_server(self.tmp_val + " " + self.tmp_color)
            self.state = 1
            return

    def parse_card(self):
        pos = pygame.mouse.get_pos()
        for card in self.hand:
            if card.rect.collidepoint(pos):
                self.client._send_server(card.name)
                self.hand.remove(card)
                if len(self.playables) != len(self.hand):
                    for elem in self.playables:
                        elem.moveDown()
                self.state = 1
                return

    def check_click(self):
        if self.state == 2:
            self.parse_annonce()
        elif self.state == 3:
            self.parse_card()

    def display_players(self):
        for player in self.players.values():
            if player.last_annonce:
                text = pygame.font.Font(None, 20).render(player.last_annonce, 1, BLACK)
                self.screen.blit(text, (player.x_ann, player.y_ann))
            if player.card:
                player.card.draw(self.screen)

    def main_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.check_click()

        self.screen.fill(GREEN)
        self.get_from_server()
        self.display_players()
        self.display_func[self.state]()
        for elem in self.hand:
            elem.draw(self.screen)
        for elem in self.players.values():
            elem.draw(self.screen)
        if self.highest_annonce != 0:
            text = pygame.font.Font(None, 15).render("{} {}".format(self.highest_annonce, self.atout), 1, BLACK)
            self.screen.blit(text, (700, 580))
        pygame.display.flip()
        self.clock.tick(60)
        return True

    def ip_screen(self):
        text = pygame.font.Font(None, 40).render("Welcome", 1, BLACK)
        self.screen.blit(text, (280,50))
        text = pygame.font.Font(None, 25).render("Entrer l'IP du serveur : ", 1, BLACK)
        self.screen.blit(text, (50, 150))
        ip = get_input(self.screen, 200, 30, 240, 150, GREEN, BLACK)
        if ip == '':
            ip = "localhost"
        self.client = Client(ip)
        self.state = 0

    def start(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load("card_images/valet_pique.png"))
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Pycoinche")
        self.state = 0

        self.screen.fill(GREEN)
        self.ip_screen()

        while self.main_loop() == True:
            pass
        print("exit")

gui = GuiHandler()
gui.start()
