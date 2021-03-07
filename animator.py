from arcade  import SpriteList
from globals import SCREEN_HEIGHT, SCREEN_WIDTH, CARD_ASPECT, CARD_HEIGHT, CARD_WIDTH, RACK_HEIGHT

class Animator:

    def __init__(self):
        self.game       = None
        self.animation  = None
        self.scene      = SpriteList()
        self.card       = None
        self.pause      = False
        self.wait       = 0
        self.finish     = lambda : None
    
    def show(self, card, end = lambda : None):
        if self.wait: return
        self.animation  = "show"
        self.pause      = True
        self.wait       = 50
        self.card       = card
        self.scene.append(card.sprite(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, False))
        self.finish     = end

    def message(self, spriteList, end = lambda : None):
        if self.wait: return
        self.animation  = "message"
        self.scene      = spriteList
        self.wait       = 10
        self.pause      = True
        self.finsh      = end

    def update(self):         
        if not self.wait: return
        if self.game.phase == "lose": return
        self.wait -= 1
        if self.wait < 0: self.wait = 0
        
        if self.animation == "show":
            if self.wait >= 45:
                self.scene[0].scale = (CARD_ASPECT + ((self.wait - 45) * 2 / 100))
            if self.wait == 5:
                self.scene[0] = self.card.sprite(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, True)
            if self.wait <= 5:
                self.scene[0].scale = (CARD_ASPECT + (self.wait * 2 / 100))
    
    def clear(self):
        self.card       = None
        while len(self.scene): self.scene.pop()
        self.animation  = None
        self.pause      = False
        end = self.finish
        self.finish     = lambda : None
        end()