import socket
import os
import sys
import time

try:
    import msvcrt
    OS = "WINDOWS"
except ImportError:
    import termios 
    OS = "UNIX"

IP = sys.argv[1]

CONTRACTS = ["80", "90", "100", "110", "120", "130", "140", "150", "160", "170", "180", "capot", "generale"]

COLORS = ["coeur", "pique", "carreau", "trefle", "tout-atout", "sans-atout"]

TRAD = {"♤" : "pique", "♡" : "coeur", "♢" : "carreau", "♧" : "trefle",
        "pique" : "♤", "coeur" : "♡", "carreau" : "♢", "trefle" : "♧" }
ATOUT = ["J", "9", "AS", "10", "K", "Q", "8", "7"]
NORMAL = ["AS", "10", "K", "Q", "J", "9", "8", "7"]

class Client():
    def __init__(self):
        self.stream = self.init_connection()
        self.hand = []
        self.actions = {
            "make_annonce" : self.make_annonce,
            "play" : self.play,
            "name" : self.name
        }
        self.infos = {
            "get_cards" : self.get_cards,
            "annonce" : self.get_annonce,
            "card" : self.get_card,
            "annonce_begin" : self.annonce_begin,
            "annonce_finale" : self.get_contract,
            "score" : self.get_score,
            "print" : self.echo,
        }
        self.queue = []
        self.pli_courant = []
        self.highest_annonce = 0
        self.wait_for_server()

    def get_input(self, msg):
        if OS == "WINDOWS":
            while msvcrt.kbhit():
                msvcrt.getch()
        else:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)

        return input(msg)
        

    def init_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((IP, 4242))
        sock.settimeout(None)
        return sock
    
    def _read_server(self):
        msg = self.stream.recv(1024).decode()
        msg = msg.split("|")
        for elem in msg:
            self.queue.append(elem)

    def _send_server(self, msg):
        self.stream.send(msg.encode())

    def decrypt_msg(self):
        msg = self.queue.pop(0).split(" ")
        if msg[0] == "info":
            self.infos[msg[1]](msg[2:])
        if msg[0] == "action":
            self.actions[msg[1]]()

    def wait_for_server(self):
        print('goes to waiting mode')
        while True:
            msg = self._read_server()
            while len(self.queue) != 0:
                self.decrypt_msg()

    def parse_annonce(self, ann):
        if ann == "passe" or ann == "0":
            return "0"
        splited = ann.split(" ")
        if len(splited) != 2:
            return False
        if splited[0] not in CONTRACTS:
            return False
        if splited[1] not in COLORS:
            return False
        if int(splited[0]) <= self.highest_annonce:
            return False
        return ann

    def make_annonce(self):
        print("voici ta main : {}".format(self.hand))
        ann = self.get_input("Fais ton annonce \n")
        ann = self.parse_annonce(ann)
        while ann == False:
            print("erreur, annonce invalide")
            print("voici ta main : {}".format(self.hand))
            ann = self.get_input("Fais ton annonce \n")
            ann = self.parse_annonce(ann)
        self._send_server(ann)

    def get_same_colors(self, card):
        color = card[-1]
        ret = []
        for elem in self.hand:
            if elem[-1] == color:
                ret.append(elem)
        return ret

    def get_atouts(self):
        ret = []
        for card in self.hand:
            if card[-1] == TRAD[self.atout]:
                ret.append(card)
        return ret

    def is_atout(self, card):
        if TRAD[card[-1]] == self.atout:
            return True
        return False

    def is_better(self, card1, card2, first):
        if card1 == card2:
            return False
        if card1[-1] == card2[-1]:
            if card1[-1] == TRAD[self.atout]:
                if ATOUT.index(card2[:-1]) < ATOUT.index(card1[:-1]):
                    return True
                else:
                    return False
            else:
                if NORMAL.index(card2[:-1]) < NORMAL.index(card1[:-1]):
                    return True
                else:
                    return False
        else:
            if card2[-1] == TRAD[self.atout]:
                return True
            return False

    def get_best_card(self):
        best = self.pli_courant[0]
        for card in self.pli_courant:
            if self.is_better(best, card, self.pli_courant) == True:
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
            if card[-1] == TRAD[self.atout]:
                if best == None:
                    best = card
                elif ATOUT.index(best[:-1]) > ATOUT.index(card[:-1]):
                    best = card
        if best == None:
            return lst
        ret = []
        for card in lst:
            if ATOUT.index(best[:-1]) > ATOUT.index(card[:-1]):
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

    def transform_card(self, card):
        ret = ""
        mots = card.split(" ")
        if len(mots) != 2:
            return "wrong"
        ret = mots[0]
        ret += TRAD[mots[1]]
        return ret

    def parse_card(self, card, playables):
        card = self.transform_card(card)
        if card not in self.hand:
            return False
        if card not in playables:
            return False
        self.hand.remove(card)
        return card

    def play(self):
        self.hand.sort(key=self.custom_key)
        print("voici ta main : {}".format(self.hand))
        playables = self.get_playables()
        print("cartes jouables :", playables)
        card = self.get_input("Joue une carte \n")
        card = self.parse_card(card, playables)
        while card == False:
            print("erreur, carte invalide")
            print("voici ta main : {}".format(self.hand))
            print("cartes jouables :", playables)
            card = self.get_input("Joue une carte \n")
            card = self.parse_card(card, playables)
        self._send_server(card)

    def custom_key(self, card):
        order = []
        colors = ["♤", "♡", "♧", "♢"]
        if self.atout == None:
            for color in colors:
                for val in NORMAL:
                    order.append(val + color)
        else:
            for val in ATOUT:
                order.append(val + TRAD[self.atout])
            colors.remove(TRAD[self.atout])
            for color in colors:
                for val in NORMAL:
                    order.append(val + color)
        return order.index(card)
        

    def get_cards(self, args):
        self.hand = []
        self.highest_annonce = 0
        self.pli_courant = []
        self.atout = None
        for card in args:
            if card != '':
                self.hand.append(card)
        self.hand.sort(key=self.custom_key)
        print("Ta main : {}".format(self.hand))

    def update_annonce(self, val):
        if val == "passe" or val == "0":
            return
        mots = val.split(" ")
        self.highest_annonce = int(mots[0])
        self.atout = mots[1]

    def get_annonce(self, args):
        joueur = args.pop(0)
        val = ""
        for elem in args:
           val += elem + " "
        val = val[:-1]
        self.update_annonce(val)
        print("{} annonce : {}".format(joueur, val))

    def get_card(self, args):
        joueur = args.pop(0)
        card = ""
        for elem in args:
            card += elem + " "
        card = card[:-1]
        self.pli_courant.append(card)
        if len(self.pli_courant) == 4:
            self.pli_courant = []
        print("{} joue : {}".format(joueur, card))

    def echo(self, args):
        msg = ""
        for elem in args:
            msg += elem + " "
        print(msg)

    def name(self):
        name = self.get_input("Hi, welcome to my amazing coinche game, made by Arobion with Love.\nPlease enter your name\n=> ")
        print("Thanks, we are waiting to other players")
        self._send_server(name)
    
    def annonce_begin(self):
        pass

    def get_contract(self):
        pass

    def get_score(self):
        pass

client = Client()
