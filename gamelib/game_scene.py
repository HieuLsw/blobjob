# To change this template, choose Tools | Templates
# and open the template in the editor.

from cocos.scenes.transitions import FadeTransition
import pyglet
from cocos.layer.base_layers import Layer
from cocos.scene import *
from cocos.scenes.transitions import *
from cocos.director import director
import cocos
import game_menu
from game_map import GameMapScene

current_level = 0

class GameInputLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(GameInputLayer,self).__init__()

    def on_key_press(self, key, modifiers):
        print(pyglet.window.key.symbol_string (key))
        if key == pyglet.window.key.ESCAPE:
            print "NO ESCAPES!"
            director.push(FadeTransition(game_menu.pause_menu(),duration=0.3))
            return True


def next_level():
    global current_level
    bg = Layer()
    bg.text = cocos.text.Label("Level "+str(current_level),x=200,y=250)
    bg.add(bg.text)
    controls = GameInputLayer()

    current_level += 1
    scene = GameMapScene('maps/level'+str(current_level)+'.xml',controls)

#    scene = Scene(bg,controls)
    director.window.set_caption("Level "+str(current_level))
    return scene
