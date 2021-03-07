from game     import Game
from globals  import CARD_ASPECT, CARD_HEIGHT, CARD_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, RACK_HEIGHT, ROOT
from animator import Animator
import arcade


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color((97, 75, 66, 255))

        # stuff
        self.animator = Animator()
        self.game     = Game(self.animator, self)
        self.log      = []

        ## Sprites / Sprite Lists
        self.cursor     = None
        self.board      = arcade.SpriteList()
        self.infoSheets = arcade.SpriteList()


    def setup(self):
        self.wlog("Beginning Startup...")
        self.cursor = arcade.Sprite(f"{ROOT}testSprite.png", 0.001)
        self.board.append(arcade.Sprite(f"{ROOT}shuffle.png"))
        self.board[-1].center_x = 10 + CARD_WIDTH / 2 
        self.board[-1].center_y = RACK_HEIGHT + CARD_HEIGHT + 25
        self.board.append(arcade.Sprite(f"{ROOT}rack.png"))
        self.board[-1].center_x = SCREEN_WIDTH / 2
        self.board[-1].center_y = RACK_HEIGHT / 2
        self.board.append(arcade.Sprite(f"{ROOT}log.png"))
        self.board[-1].center_x = SCREEN_WIDTH / 2
        self.board[-1].center_y = SCREEN_HEIGHT - 85
        self.board.append(arcade.Sprite(f"{ROOT}phase.png"))
        self.board[-1].center_x = SCREEN_WIDTH / 2
        self.board[-1].center_y = RACK_HEIGHT + CARD_HEIGHT + 30
        self.wlog("Startup Complete")

    def on_draw(self):
        arcade.start_render()

        self.board.draw()
        self.draw_log()

        while len(self.infoSheets): self.infoSheets.pop()
        self.infoSheets.append(self.game.drawInfoSheet(self.game.player, 10, SCREEN_HEIGHT - 160))

        drop = 1
        for monster in self.game.actors[1:]:
            self.infoSheets.append(self.game.drawInfoSheet(monster, SCREEN_WIDTH - 190, SCREEN_HEIGHT - (160 * drop)))
            drop += 1

        for player in (self.game.player,):
            player.deck.back.draw()

            if not len(player.disc): player.disc.back.draw()
            else:                    player.disc[-1].sprite(SCREEN_WIDTH - 10 - (CARD_WIDTH / 2),
                                                            RACK_HEIGHT + (CARD_HEIGHT / 2), 
                                                            True).draw()

            for i in range (0, len(player.hand)):
                player.hand[i].sprite(((10 + CARD_WIDTH) * (i + 1)) + 10 + (CARD_WIDTH / 2),
                                      RACK_HEIGHT + (CARD_HEIGHT / 2), 
                                      True).draw()
        
        if self.game.backboard != None: self.game.backboard.draw()
        for button in self.game.buttons: button[0].draw()

        self.animator.scene.draw()

    def draw_log(self):
        x = 203
        y = SCREEN_HEIGHT - 159
        i = 0
        while i < 9 and i < len(self.log):
            arcade.draw_text(self.log[-1 - i], x, y + (16 * i), (0,0,0,255), 13)
            i += 1

    def wlog(self, text):
        self.log.append(text)

    def on_update(self, delta_time):
        self.animator.update()
        self.game.update()

        self.board.pop()
        try:
            phaseName = {
                "newfloor" : "Generate",
                "battle"   : "Battle",
            }[self.game.phase]
            if self.game.phase == "battle":
                phaseName = {
                    "target"   : "Battle",
                    "attack"   : "Attack",
                    "defend"   : "Defend",
                    "evaluate" : "Battle"
                }[self.game.combatPhase]
        except KeyError: phaseName = ""
        self.board.append(arcade.Sprite(f"{ROOT}phase{phaseName}.png"))
        self.board[-1].center_x = SCREEN_WIDTH / 2
        self.board[-1].center_y = RACK_HEIGHT + CARD_HEIGHT + 30

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        self.cursor.center_x = x
        self.cursor.center_y = y

    def on_mouse_press(self, x, y, button, key_modifiers):
        if   self.game.phase == "lose": return
        if   self.animator.wait : return
        elif self.animator.pause: self.animator.clear()
        elif arcade.check_for_collision(self.cursor, self.board[0]): #shuffle button
                self.game.player.shuffle()
        elif (self.game.phase        == "battle"    and
              (self.game.combatPhase == "attack" and 
               self.game.turn        == 0)          or 
              (self.game.combatPhase == "defend" and
               self.game.turn        != 0)          ):
            for i in range(0, len(self.game.player.hand)):
                if arcade.check_for_collision(self.cursor, self.game.player.hand[i].sprite()):
                    self.game.action(self.game.player.play(i, True))
                    break
            if arcade.check_for_collision(self.cursor, self.game.player.deck.back):
                self.game.action(self.game.player.flop(True))
        elif self.game.phase == "battle" and self.game.combatPhase == "target":
            for i in range(1, len(self.infoSheets)):
                if arcade.check_for_collision(self.cursor, self.infoSheets[i]):
                    self.game.target = self.game.actors[i]
                    break
        elif self.game.phase == "wait":
            for button in self.game.buttons:
                if arcade.check_for_collision(self.cursor, button[0]):
                    button[1]()
                    break



def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()