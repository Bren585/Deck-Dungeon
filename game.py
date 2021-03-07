from actor   import Actor, Card
from arcade  import SpriteList, Sprite, draw_text
from globals import RACK_HEIGHT, CARD_HEIGHT, CARD_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT, NAME_LIST, BOSS_NAME_LIST, ROOT, BUTTON_GAP, BUTTON_WIDTH
from math    import ceil
import random

random.seed()

def addArray(foo, bar):
    if len(foo) != len(bar) : return
    hold = []
    for i in range(0, len(foo)):
        hold.append(foo[i] + bar[i])
    return hold

class Game:

    def __init__(self, animator, engine):
        self.animator      = animator
        self.animator.game = self
        self.engine        = engine

        self.player = Actor(self.animator, "Player", 0)
        self.player.deck.back.center_x = 10 + (CARD_WIDTH / 2)
        self.player.deck.back.center_y = RACK_HEIGHT + (CARD_HEIGHT / 2)
        self.player.disc.back.center_x = SCREEN_WIDTH - 10 - (CARD_WIDTH / 2)
        self.player.disc.back.center_y = RACK_HEIGHT + (CARD_HEIGHT / 2)
        self.player.shuffle()

        self.floor       = 0
        self.floorBonus  = [0, 0, 0, 0]
        self.buffPlayer  = False
        self.numMonsters = 0
        self.actors      = []

        self.buttons   = []
        self.backboard = None

        self.result = None
        self.attack = None
        self.defend = None
        self.target = None

        self.phase       = "startup"
        self.turn        = 0
        self.combatPhase = "target"

    def update(self):
        if len(self.player.deck) <= 30: self.player.shuffle()
        {
            "wait"     : lambda : None,
            "startup"  : self.startup,
            "newfloor" : self.generateFloor,
            "battle"   : self.battle,
            "levelup"  : self.levelUp,
            "lose"     : self.lose,
            "win"      : self.win
        }[self.phase]()

    def calcBonus(self, actor):
        stats = actor.stats()
        if ((actor == self.player and     self.buffPlayer) or 
            (actor != self.player and not self.buffPlayer)):
            stats = addArray(stats, self.floorBonus)
        return stats

    def drawInfoSheet(self, actor, x, y):
        stats = self.calcBonus(actor)
        background = Sprite(f'{ROOT}infoSheet.png')
        background.center_x = x + 90
        background.center_y = y + 75
        background.draw()
        draw_text(actor.name   , x + 12 , y + 100, (0, 0, 0, 255), 21, 155, 'center')
        draw_text(str(stats[0]), x + 12 , y + 33 , (0, 0, 0, 255), 21, 36 , 'center')
        draw_text(str(stats[1]), x + 52 , y + 33 , (0, 0, 0, 255), 21, 36 , 'center')
        draw_text(str(stats[2]), x + 93 , y + 33 , (0, 0, 0, 255), 21, 36 , 'center')
        draw_text(str(stats[3]), x + 131, y + 33 , (0, 0, 0, 255), 21, 36 , 'center')
        return background

    def menu(self, buttons, backboard):
        self.phase              = "wait"
        self.backboard          = Sprite(backboard)
        self.backboard.center_x = SCREEN_WIDTH / 2
        self.backboard.center_y = SCREEN_HEIGHT / 2
        size                    = len(buttons)
        isEven                  = int(size % 2 == 0) / 2
        xPos                    = isEven * 2
        for i in range(0, size):
            newButton           = Sprite(buttons[i][0])
            offset              = (BUTTON_WIDTH + BUTTON_GAP) * (xPos + (isEven * ((-1)**int(xPos >= 0))))
            xPos               *= -1
            if xPos >= 0: xPos += 1 
            newButton.center_x  = SCREEN_WIDTH / 2 + offset
            newButton.center_y  = SCREEN_HEIGHT / 2 - 25
            self.buttons.append((newButton, buttons[i][1]))

    def clearButtons(self):
        self.buttons   = []
        self.backboard = None

    def button(self):
        self.engine.wlog("Button pressed")
        self.clearButtons()
    
    def buttonArmorer(self):
        self.player.DEF      += 3
        self.player.healBonus = 1
        self.clearButtons()
        self.phase = "newfloor"

    def buttonMonk(self):
        self.player.DEF += 2
        self.player.HP  += 5
        self.clearButtons()
        self.phase = "newfloor"

    def buttonGambler(self):
        self.player.HP  -= 5
        self.player.ATK += 1
        self.player.LCK += 2
        self.player.modLCK = 2
        self.clearButtons()
        self.phase = "newfloor"

    def buttonPriest(self):
        self.player.LCK      += 2
        self.player.DEF      -= 2
        self.player.healBonus = 1
        self.clearButtons()
        self.phase = "newfloor"

    def buttonWarrior(self):
        self.player.ATK += 2
        self.player.DEF += 1
        self.clearButtons()
        self.phase = "newfloor"

    def buttonShaman(self):
        self.player.HP  += 5
        self.player.LCK += 1
        self.player.ATK -= 2
        self.clearButtons()
        self.phase = "newfloor"

    def buttonHealth(self):
        self.player.HP += 5
        self.clearButtons()
        self.phase = "levelup"
    
    def buttonAttack(self):
        self.player.ATK += 1
        self.clearButtons()
        self.phase = "levelup"
    
    def buttonDefense(self):
        self.player.DEF += 1
        self.clearButtons()
        self.phase = "levelup"
    
    def buttonLuck(self):
        self.player.LCK += 1
        self.clearButtons()
        self.phase = "levelup"

    def startup(self):
        # TODO
        # character creation stuff
        self.menu(
            (
                (f"{ROOT}buttonArmorer.png",    self.buttonArmorer  ),
                (f"{ROOT}buttonMonk.png",       self.buttonMonk     ),
                (f"{ROOT}buttonGambler.png",    self.buttonGambler  ),
                (f"{ROOT}buttonPriest.png",     self.buttonPriest   ),
                (f"{ROOT}buttonWarrior.png",    self.buttonWarrior  ),
                (f"{ROOT}buttonShaman.png",     self.buttonShaman   )
            ),
            f"{ROOT}backboardClass.png"
        )

    def generateFloor(self):
        self.player.draw(5)
        self.floor += 1
        self.floorBonus  = [0, 0, 0, 0]
        self.buffPlayer  = False
        self.numMonsters = 0
        self.actors      = []
        self.turn        = 0
        self.result = self.player.flop()
        self.phase = "wait"
        self.animator.show(self.result, self.generateFloor_F)

    def generateFloor_F(self):
        # Resolve generation
        self.actors.append(self.player)
        self.numMonsters = (1,1,1,1,1,2,2,2,2,2,2,3,3)[self.result.value]
        if self.numMonsters == 1:
            name = NAME_LIST[random.randint(0, len(NAME_LIST) - 1)]
            self.actors.append(Actor(self.animator, name, -1, True, self.floor))
        elif self.numMonsters == 2:
            name = NAME_LIST[random.randint(0, len(NAME_LIST) - 1)]
            self.actors.append(Actor(self.animator, name, -1, True, self.floor))
            name = NAME_LIST[random.randint(0, len(NAME_LIST) - 1)]
            self.actors.append(Actor(self.animator, name, -1, True, self.floor))
        else:
            name = BOSS_NAME_LIST[random.randint(0, len(BOSS_NAME_LIST) - 1)]
            self.actors.append(Actor(self.animator, name, -1, True, self.floor, True))

        self.theme()

    def theme(self):
        if self.result.suit == 3:       ## Diamonds
            self.buffPlayer = not self.buffPlayer
            self.player.disc.append(self.result)
            self.result = self.player.flop()
            self.animator.show(self.result, self.theme)
            return
        elif self.result.suit == 1:     ## Hearts
            if self.buffPlayer:
                self.player.HP += ceil(self.floor / 2)
            else: 
                for i in range(0, len(self.actors)):
                    if self.actors[i] != self.player:
                        self.actors[i].HP += ceil(self.floor / 2)
        elif self.result.suit == 0:     ## Spades
            self.floorBonus[1]  = ceil(self.floor / 2)
        elif self.result.suit == 2:     ## Clubs
            self.floorBonus[2]  = ceil(self.floor / 2)
        
        self.player.disc.append(self.result)
        self.result = None
        self.phase  = "battle"

    def battle(self):
        if   self.animator.pause: return
        if   self.combatPhase == "target": 
            if   self.target: 
                self.combatPhase = "attack"
                if self.turn: self.engine.wlog(f"{self.actors[self.turn].name} gets ready to attack.")
            elif self.turn  : self.target      = self.player
        elif self.combatPhase == "attack" and self.attack: 
            self.combatPhase = "defend"
            self.result      = None
        elif self.combatPhase == "defend" and self.defend: 
            self.combatPhase = "evaluate"
            self.result      = None
        elif self.combatPhase == "evaluate":
            self.target.HP            += self.defend[0]
            self.actors[self.turn].HP += self.attack[0]
            damage = self.attack[1] - self.defend[2]
            if self.attack[0]: 
                self.engine.wlog(f"{self.actors[self.turn].name} healed {self.attack[0]}.")
            if self.defend[0]:
                self.engine.wlog(f"{self.target.name} healed {self.defend[0]}.")
            if damage > 0:
                self.engine.wlog(f"{self.target.name} took {damage} damage.")
            else:
                self.engine.wlog(f"{self.target.name} took no damage.")

            if damage > 0: self.target.HP -= damage

            self.result = None
            self.attack = None
            self.defend = None
            self.target = None
            self.turn += 1
            if self.turn >= len(self.actors): self.turn = 0
            self.combatPhase = "target"

            if self.player.HP <= 0: 
                self.phase == "lose"
                self.engine.wlog(f"You lost! You absolute fool, you cretin. Weep.")
                return
            i = 1
            while i < len(self.actors):
                if self.actors[i].HP <= 0: self.engine.wlog(f"{self.actors.pop(i).name} was slain.")
                else                     : i += 1
            if len(self.actors) == 1:
                self.phase = "levelup"
        else:
            if self.turn and self.combatPhase == "attack":
                card = self.actors[self.turn].flop()
                self.animator.show(card)
                self.action(card)
                self.actors[self.turn].disc.append(card)
                self.actors[self.turn].shuffle()
            elif not self.turn and self.combatPhase == "defend":
                card = self.target.flop()
                self.animator.show(card)
                self.action(card)
                self.target.disc.append(card)
                self.target.shuffle()

    def action(self, card):
        bonus = 0
        if self.combatPhase == "attack": actor = self.actors[self.turn]
        else                           : actor = self.target
        if card.suit == 3:
            self.engine.wlog(f"{actor.name} got lucky with a {card}.")
            if self.result:
                if self.result.value < card.value: self.result = card
            else: self.result = card
            return
        message = ("in defense", "to attack")[int(self.combatPhase == "attack")]
        self.engine.wlog(f"{actor.name} used a {card} {message}.")
        if self.result: bonus = actor.resolve(self.result)[3]
        action = actor.resolve(card, bonus)
        if ((actor == self.player and     self.buffPlayer) or 
            (actor != self.player and not self.buffPlayer)):
            action = addArray(action, self.floorBonus)
        if   self.combatPhase == "attack": self.attack = action
        elif self.combatPhase == "defend": self.defend = action

    def levelUp(self):
        if self.numMonsters:
            self.menu(
                (
                    (f"{ROOT}buttonDefense.png", self.buttonDefense),
                    (f"{ROOT}buttonAttack.png",  self.buttonAttack ),
                    (f"{ROOT}buttonHealth.png",  self.buttonHealth ),
                    (f"{ROOT}buttonLuck.png",    self.buttonLuck   )
                ),
                f"{ROOT}backboardLevel.png"
            )
            self.numMonsters -= 1
        elif self.floor == 4:
            self.phase = "win"
        else:
            self.phase = "newfloor"

    def lose(self):
        # handle game over
        self.phase = "lose"

    def win(self):
        # handle victory
        self.engine.wlog("A winner is you!")
        