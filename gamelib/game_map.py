import os

from cocos.scenes.transitions import FadeTransition
from cocos.sprite import Sprite
from cocos.scenes.pause import PauseScene
from cocos.actions.tiledgrid_actions import FadeOutTRTiles
from cocos import tiles
from cocos.director import director
from cocos.scene import Scene
from cocos.layer import ScrollingManager
from cocos.layer import Layer
from wobble import  Wobble
import data
import pyglet
import game_scene

class GameDecoratorLayer(Layer):
    def __init__(self):
        super(GameDecoratorLayer,self).__init__()
        bg = "bgs/the_void.png"
        sprite = Sprite(bg)
        sprite.x = sprite.width/2
        sprite.y = sprite.height/2
        
        self.add(sprite)
        

class GameMapScene(Scene):
    def __init__(self,level_xml,speed=30, contents=None):
        super(GameMapScene, self).__init__(contents)

#        self.remove(self.manager)
        self.manager = ScrollingManager()
        self.add(self.manager)
        print pyglet.resource.path
        level = tiles.load(level_xml)
        print level
        mz = 0
        for id, layer in level.find(tiles.MapLayer):
            print layer
            self.manager.add(layer, z=layer.origin_z)
            mz = max(layer.origin_z, mz)

        self.level = level

        self.add(GameControlLayer(self.manager, 60))
        self.wobble = Wobble((5,3),level)
        self.add(self.wobble)
        self.manager.y = -25
        self.fg = GameDecoratorLayer()
        self.add(self.fg,z=999)
        sounds.set_music('music/on_game.ogg')


    def char_die(self):
        director.replace(FadeTransition(game_scene.GameOverScene(),duration=1))


class GameControlLayer(Layer):
    def __init__(self, manager, speed):
        super(GameControlLayer, self).__init__()
        self.speed = speed
        self.manager = manager
        self.fx = self.manager.fx
        self.fy = self.manager.fy
        self.schedule(self.step)
        print "control layer engaged"
        
    def step(self,dt):
        delta = self.speed*dt
        self.fx += delta
        self.parent.wobble.x -= delta

        self.manager.set_focus(self.fx, self.fy)
