# To change this template, choose Tools | Templates
# and open the template in the editor.

from cocos.scenes.transitions import FadeTransition
import pyglet

from pgu.gui.basic import Color
from cocos.director import director
from cocos.batch import BatchNode
from cocos.menu import Menu, MenuItem, CENTER, zoom_in, zoom_out, EntryMenuItem, ImageMenuItem, MultipleMenuItem,shake
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.layer.base_layers import MultiplexLayer, Layer

import intro_scene
#import sounds
#from sfx import Sfx


class BrandedMenu(Menu):
    """Branded menus for the game -- all menus inherit from here"""
    def __init__(self,title="Wibble-wobble"):
        super(BrandedMenu, self).__init__(title)

#        self.font_title['font_name'] = '!Limberjack'
        self.font_title['font_name'] = 'Warender Bibliothek'
        self.font_title['font_size'] = 70
        self.font_title['color'] = (130,185,85,200)
        self.font_title['dpi']=100

        self.font_item['font_name'] = 'Handserif'
        self.font_item['font_size'] = 40
        self.font_item['color'] = (100,255,100,150)
        self.font_item['dpi'] = 100
        
        self.font_item_selected['font_name'] = 'Handserif'
        self.font_item_selected['font_size'] = 40
        self.font_item_selected['color'] = (200,255,200,255)
        
        self.menu_valign = CENTER
        self.menu_halign = CENTER


class MainMenu(BrandedMenu):
    """Main menu for the game"""
    def __init__(self):
        super(MainMenu, self).__init__()

        items = []
        self.title="Wibble-Wobble"
#        self.select_sound = Sfx('sfx/menu_change.wav')
        items.append(MenuItem('Play', self.on_new_game))
#        items.append(MenuItem('Scores', self.on_score))
        items.append(MenuItem('Configure', self.on_configure))
        items.append(MenuItem('Quit', self.on_quit))
        self.create_menu(items, zoom_in(), zoom_out(), shake())
#        sounds.set_music('music/Ambient_loop1.ogg')

    def on_new_game(self):
        #director.push(game_scene)
        director.push(FadeTransition(intro_scene.get_scene(),duration = 0.4))

    def on_score(self):
        print "Aca mostramos los Scores"

    def on_configure(self):
        self.parent.switch_to(1)
       # print "Aca vamos a la configuracion"

    def on_quit(self):
        pyglet.app.exit()


class ConfigMenu(BrandedMenu):
    """Config menu"""
    def __init__(self):
        super(ConfigMenu, self).__init__('Configure')

        l = []
#        volumes = ['Mute', '10','20', '30', '40', '50', '60', '70', '80', '90', 'Max']
#        l.append( MultipleMenuItem('Music Volume: ', self.on_music_volume, volumes, 7))
#        l.append( MultipleMenuItem('SFX Volume: ', self.on_sfx_volume, volumes, 7))
        l.append( MenuItem('Fullscreen', self.on_fullscreen))
        l.append( MenuItem('Main Menu', self.on_quit))
        self.create_menu(l)

    def on_music_volume(self, value):
        print 'music volume: %d' % value

    def on_sfx_volume(self, value):
        print 'sfx volume: %d' % value

    def on_fullscreen(self):
        director.window.set_fullscreen( not director.window.fullscreen )

    def on_quit(self):
        print "Thanks for playing!"
        self.parent.switch_to(0)

class PauseMenu(BrandedMenu):
    """Pause menu"""
    def __init__(self):
        super(PauseMenu, self).__init__('Paused')

        l = []
        l.append( MenuItem('Continue', self.on_continue))
        l.append( MenuItem('Quit to Main Menu', self.on_quit))
        self.create_menu(l)

    

    def on_continue(self):
        director.pop()

    def on_quit(self):
        print "Thanks for playing!"
        director.pop()
        director.pop()
#        self.parent.switch_to(0)


class BackgroundLayer(object):
    "Creates a background from an image, making a mosaic"
    def __init__(self, image):
        self.image = image
        self.batch = BatchNode()
        self.create_background()
    def create_background(self):
        x_size, y_size = director.get_window_size()
        self.sprite = Sprite(self.image)
#        self.sprite.anchor_x = self.sprite.width / 2
#        self.sprite.anchor_y = self.sprite.height / 2
        for x in xrange(0, x_size, self.sprite.width):
            for y in xrange(0, y_size, self.sprite.height):
                sprite = Sprite(self.image)
                sprite.x = x
                sprite.y = y
                self.batch.add(sprite)
                print "sprite agregado", self.batch
    def back_batch(self):
        return self.batch



def get_scene():
    menu_layer = MultiplexLayer(MainMenu(), ConfigMenu())
    back_layer = Layer()
    back = BackgroundLayer('bgs/menu_background.jpg')
    back_layer.add(back.back_batch())
    scene = Scene()
    scene.add(back_layer, z=0)
    scene.add(menu_layer)
    return scene

def pause_menu(bg=None):
    scene = Scene()
    if(bg != None):
        scene.add(bg, z=0)
        
    scene.add(PauseMenu())
    return scene