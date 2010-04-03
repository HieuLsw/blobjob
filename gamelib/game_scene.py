# To change this template, choose Tools | Templates
# and open the template in the editor.

from cocos.scenes.transitions import FadeTransition
import pyglet
from cocos.sprite import Sprite
from cocos.layer import Layer
from cocos.scene import *
from cocos.scenes.transitions import *
from cocos.director import director
import cocos
import game_menu
from game_map import GameMapScene
import sys

current_level = 0

class BilboardScene(Scene):
    def __init__(self):
        super(BilboardScene,self).__init__()
        if(self.image):
            self.sprite = Sprite(self.image)
            self.sprite.x = self.sprite.width/2
            self.sprite.y = self.sprite.height/2
            self.add(self.sprite)

class GameOverScene(BilboardScene):
    image = 'bgs/game_over.jpg'
    def __init__(self):
        super(GameOverScene,self).__init__()
        self.add(GameOverControlLayer())
        
class GameOverControlLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(GameOverControlLayer,self).__init__()

    def on_key_press(self, key, modifiers):
        director.pop()

class GameInputLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(GameInputLayer,self).__init__()

    def on_key_press(self, key, modifiers):
        if key == pyglet.window.key.ESCAPE:
            director.push(FadeTransition(game_menu.pause_menu(),duration=0.3))
            return True


def reset_levels():
    global current_level
    current_level = 0

def next_level():
    global current_level
#    bg = Layer()
#    bg.text = cocos.text.Label("Level "+str(current_level),x=200,y=250)
#    bg.add(bg.text)
    controls = GameInputLayer()

    current_level += 1
    scene = GameMapScene('level'+str(current_level)+'.xml', speed=50, contents=controls)

#    scene = Scene(bg,controls)
    director.window.set_caption("Level "+str(current_level))
    return scene


def first_level():
    reset_levels()
    return next_level()
