import os

from cocos.actions import Repeat
from cocos.actions.grid3d_actions import *
from cocos.actions.camera_actions import *
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
import sounds
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
        

class GameMapBaseScene(Scene):
    def __init__(self,level_xml,speed=30, contents=None):
        super(GameMapBaseScene, self).__init__(contents)

        self.manager = ScrollingManager()
        self.add(self.manager)
        level = tiles.load(level_xml)
        mz = 0
        mx = 0
        for id, layer in level.find(tiles.MapLayer):
            self.manager.add(layer, z=layer.origin_z)
            mz = max(layer.origin_z, mz)
            mx = max(layer.px_width, mx)

        self.level = level
        self.px_width = mx

class GameMapScene(GameMapBaseScene):
    def __init__(self,level_xml,speed=30, contents=None):
        super(GameMapScene, self).__init__(level_xml,speed,contents)
        self.add(GameControlLayer(self.manager, 80))
        self.wobble = Wobble((5,7), self.level)
        self.add(self.wobble)
        self.wobble.x=0
        self.wobble.y=0
        self.manager.y = -25
        self.fg = GameDecoratorLayer()
        self.add(self.fg,z=999)
        sounds.set_music('music/on_game.ogg')
        #This line fixes the grid added by the MapLayer
        self.manager.do(Waves(waves=1,amplitude=0))
        
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
        self.playing = True

        
    def step(self,dt):
        if(self.playing):
            delta = self.speed*dt
            self.fx += delta
            self.parent.wobble.x -= delta

            self.manager.set_focus(self.fx, self.fy)
            if(self.parent.px_width - self.fx <= 400):
                director.replace(FadeTransition(game_scene.next_level(),duration=1))
                self.playing = False
