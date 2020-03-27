ATOUT = ["J", "9", "AS", "10", "K", "Q", "8", "7"]
NORMAL = ["AS", "10", "K", "Q", "J", "9", "8", "7"]
TRAD = {"♤" : "pique", "♡" : "coeur", "♢" : "carreau", "♧" : "trefle",
        "pique" : "♤", "coeur" : "♡", "carreau" : "♢", "trefle" : "♧",}

class Card():
    def __init__(self, name, client, translate=False):
        if translate == True:
            name = self.translate_name(name)
        self.name = name
        self.color = name[-1]
        self.value = name[:-1]
        self.is_atout = False
        self.order = NORMAL
        self.client = client
        self.str = self.strize(name)

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
            return mots[0] + TRAD[mots[1]]
        except KeyError as e:
            return "wrong"

    def position(self):
        return self.order.index(self.value)

    def set_atout(self, atout):
        if self.color == TRAD[atout]:
            self.is_atout = True
            self.order = ATOUT
        else:
            self.is_atout = False
            self.order = NORMAL
    
    # used to sort
    def __lt__(self, other):
        colors = ["♤", "♡", "♧", "♢"]
        if self.client.atout != None:
            colors.remove(TRAD[self.client.atout])
            colors.insert(0, TRAD[self.client.atout])
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
