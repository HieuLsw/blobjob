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
current_level = 0

class GameInputLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(GameInputLayer,self).__init__()

    def on_key_press(self, key, modifiers):
        print(pyglet.window.key.symbol_string (key))
        if key == pyglet.window.key.ESCAPE:
            print "NO ESCAPES!"
            director.push(FadeTransition(game_menu.pause_menu(),duration=1))
            return True


def next_level():
    bg = Layer()
    bg.text = cocos.text.Label("Level "+str(current_level),x=200,y=250)
    bg.add(bg.text)
    controls = GameInputLayer()

    scene = Scene(bg,controls)
    return scene
