# To change this template, choose Tools | Templates
# and open the template in the editor.

import pyglet
from cocos.sprite import Sprite
from cocos.layer import Layer
from cocos.scene import *
from cocos.scenes.transitions import *
from cocos.director import director
import sounds
import game_menu
from game_map import GameMapScene
from blob_transitions import *
from bilboard_scene import BilboardScene
current_level = 0
max_level = 2

class GameOverScene(BilboardScene):
    image = 'bgs/game_over.jpg'
    def __init__(self):
        super(GameOverScene,self).__init__()
        sounds.set_music('music/game_over.ogg')

class GameWinScene(BilboardScene):
    image = 'bgs/ftw.jpg'
    def __init__(self):
        super(GameWinScene,self).__init__()
        sounds.set_music('music/ftw.ogg')
        

class GameInputLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(GameInputLayer,self).__init__()

    def on_key_press(self, key, modifiers):
        if key == pyglet.window.key.ESCAPE:
            director.push(blob_fade_transition(game_menu.pause_menu()))
            return True

def reset_levels():
    global current_level
    current_level = 0
    
def next_level():
    global current_level
    global max_level

    if(current_level <= max_level):
        controls = GameInputLayer()
        current_level += 1
        scene = GameMapScene('level'+str(current_level)+'.xml', speed=50, contents=controls)
        director.window.set_caption("Level "+str(current_level))
    else:
        scene = GameWinScene()
    return scene

def cur_level():
    global current_level


    controls = GameInputLayer()
    scene = GameMapScene('level'+str(current_level)+'.xml', speed=50, contents=controls)
    director.window.set_caption("Level "+str(current_level))
    
    return scene


def first_level():
    reset_levels()
    return next_level()



def get_current_level():
    global current_level
    return current_level