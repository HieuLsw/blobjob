import os

from cocos.text import Label
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

#Character extra lives
#shoudl be an attribute of the character class
char_initial_lives = 2
lives = 2


class OSDLayer(Layer):
    def __init__(self):
        super(OSDLayer,self).__init__()

        #blob image
        self.lives_sprite = Sprite("chars/wobble/blob_1.png")
        self.add(self.lives_sprite);
        self.lives_sprite.x = 720
        self.lives_sprite.y = 575
        self.lives_sprite.scale = 0.4
        self.lives_sprite.opacity = 100

        #lives text
        font_name = "Casual"
        font_size = 10
        fo = pyglet.font.load(font_name, font_size)
        font_item = {}
        font_item['font_name'] = font_name
        font_item['font_size'] = font_size
        font_item['anchor_x'] = "right"
        font_item['color'] = (130,185,85,200)
        font_item['x'] = 770
        font_item['y'] = 550
        
        self.label = Label(**font_item )

        self.update()
        self.add(self.label)
        

    def update(self):
        global lives
        print "Lives are now: "+str(lives)
        self.label.element.text = 'x '+str(lives)

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
        self.osd = OSDLayer()
        
        self.add(self.fg,z=999)
        self.add(self.osd,z=1000)
        sounds.set_music('music/on_game.ogg')
        #This line fixes the grid added by the MapLayer
        self.manager.do(Waves(waves=1,amplitude=0))
        
    def char_die(self):
        global lives
        if(lives>0):
            lives -= 1
            self.osd.update()
            director.replace(FadeTransition(game_scene.cur_level(),duration=1))
        else:
            director.replace(FadeTransition(game_scene.GameOverScene(),duration=1))
            lives = char_initial_lives


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
