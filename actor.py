from arcade  import SpriteList, Sprite
from globals import CARD_ASPECT, CARD_HEIGHT, CARD_WIDTH, ROOT, SUIT_NAME, BACK_NAME, SCREEN_WIDTH, RACK_HEIGHT, MOD, VALUE_NAME
from math    import ceil
import random

random.seed()

class Card:

    def __init__(self, suit, value, back):
        self.suit   = suit
        self.value  = value
        self.faceUp = True

        self.face = Sprite(f"{ROOT}{SUIT_NAME[suit]} {value + 1}.png", CARD_ASPECT)
        self.back = Sprite(f"{ROOT}Back {BACK_NAME[back]}.png"       , CARD_ASPECT)
    
    def __str__(self):
        return f"{VALUE_NAME[self.value]} of {SUIT_NAME[self.suit]}"
    
    def flip(self, up = -1):
        if up == -1: self.faceUp = not self.faceUp
        else       : self.faceUp = up 
    
    def sprite(self, x = -1, y = -1, up = -1):
        if x != -1 and y != -1:
            self.face.center_x = x
            self.face.center_y = y
            self.back.center_x = x
            self.back.center_y = y
        if up == -1:
            if self.faceUp: return self.face
            else          : return self.back
        else:
            if up         : return self.face
            else          : return self.back

class Pile:

    def __init__(self, back, isDeck = False):
        self.cards = []
        if isDeck:
            for i in range(0, 52):
                self.cards.append(Card(int(i / 13), i % 13, back))
        self.back = Sprite(f"{ROOT}/Back {BACK_NAME[back]}.png", CARD_ASPECT)
    
    def __str__(self):
        out = ""
        for card in self.cards:
            out += str(card)
            out += '\n'
        return out
    
    def __getitem__(self, key):
        return self.cards[key]
    
    def __len__(self):
        return len(self.cards)

    def pop(self, i = -1):
        return self.cards.pop(i)
    
    def append(self, card):
        self.cards.append(card)
    
    def insert(self, i, card):
        self.cards.insert(i, card)

    def shuffle(self):
        hold = []
        while len(self.cards) > 0:
            hold.append(self.cards.pop(random.randint(0, len(self.cards) - 1)))
        self.cards = hold
    
    def spriteList(self):
        out = SpriteList()
        for card in self.cards:
            out.append(card.sprite())

class Actor:
    
    def __init__(self, animator, name, back = -1, isMonster = False, floor = 0, isBoss = False):
        self.animator = animator
        self.name     = name

        if back == -1: back = random.randint(0, 5)
        self.deck = Pile(back, True)
        self.hand = Pile(back)
        self.disc = Pile(back)

        if not isMonster:
            self.HP     = 15
            self.ATK    = 4
            self.DEF    = 2
            self.LCK    = 1
        elif not isBoss:
            self.HP     = 10 + (2 * floor)
            self.ATK    = 2 + floor
            self.DEF    = 0 + floor
            self.LCK    = 0
        else:
            self.HP     = 10 + (3 * floor)
            self.ATK    = 5 + floor
            self.DEF    = 2 + floor
            self.LCK    = 4
        self.modLCK    = 3
        self.healBonus = 0

    def __str__(self):
        return f"{self.name} | {self.HP} | {self.ATK} | {self.DEF} | {self.LCK} |"

    # CARD MANAGEMENT        
    def flop(self, animate = False):
        result = self.deck.pop()
        if animate: self.animator.show(result, lambda : self.disc.append(result))
        return result

    def draw(self, num = 1):
        if num > len(self.deck): num = len(self.deck)
        for i in range(0, num):
            if len(self.hand) < 5:
                self.hand.append(self.deck.pop())
    
    def play(self, i, animate = False):
        result = self.hand.pop(i)
        if animate: self.animator.show(result, lambda : self.disc.append(result))
        return result
    
    def shuffle(self):
        while len(self.disc) > 0:
            self.deck.append(self.disc.pop())
        self.deck.shuffle()
    
    # STAT MANAGEMENT
    def stats(self):
        return (self.HP,
                self.ATK,
                self.DEF,
                self.LCK)

    def resolve(self, card, bonus = 0):
        bonus = bonus + MOD[card.value]
        return ((bonus + self.healBonus) * int(card.suit == 1),
                (bonus                   * int(card.suit == 0)) +      self.ATK,
                (bonus                   * int(card.suit == 2)) +      self.DEF,
                (bonus                   * int(card.suit == 3)) + ceil(self.LCK / self.modLCK))