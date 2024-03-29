import pyglet.window.key
# To change this template, choose Tools | Templates
# and open the template in the editor.

from cocos.actions.interval_actions import Accelerate
from cocos.actions.interval_actions import Delay
from cocos.layer.util_layers import ColorLayer
from cocos.text import Label
from cocos.actions.grid3d_actions import Shaky3D
from cocos.actions.interval_actions import *
from cocos.scenes.transitions import FadeTransition
import pyglet
from pyglet.gl import *
import sys

from cocos.director import director
from cocos.batch import BatchNode
from cocos.menu import Menu, MenuItem, RIGHT,BOTTOM, zoom_in, zoom_out, MultipleMenuItem,shake
from cocos.menu import verticalMenuLayout
from cocos.scene import Scene
from cocos.sprite import Sprite
from cocos.layer.base_layers import MultiplexLayer, Layer

import reader_scene
import intro_scene
from blob_transitions import *

import sounds
from sfx import Sfx
#import cocos.audio


class DisableEscapeKeyLayer(Layer):
    is_event_handler = True
    def on_key_press(self,key,modifiers):
        print "Key " + str(key)
        if(key == pyglet.window.key.ESCAPE ):
            return True

class BrandedMenu(Menu):
    """Branded menus for the game -- all menus inherit from here"""
    def __init__(self,title=""):
        super(BrandedMenu, self).__init__(title)
        self.menu_vmargin = 30
        self.menu_hmargin = 30
        
#        self.font_title['font_name'] = '!Limberjack'
        self.font_title['font_name'] = 'Casual'
        self.font_title['font_size'] = 20
        self.font_title['color'] = (130,185,85,200)
        self.font_title['dpi']=100

        self.font_item['font_name'] = 'Casual'
        self.font_item['font_size'] = 30
        self.font_item['color'] = (255,255,255,255)
        self.font_item['dpi'] = 100
        
        self.font_item_selected['font_name'] = 'Casual'
        self.font_item_selected['font_size'] = 30
        self.font_item_selected['color'] = (134,197,64,255)
        
        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT
        self.select_sound = Sfx('sfx/menu_change.wav')

    def on_key_press(self,key,modifiers):
        if(key == pyglet.window.key.ESCAPE ):
            return True
        super(BrandedMenu, self).on_key_press(key, modifiers)

    def create_menu(self, items, selected_effect=None, unselected_effect=None,
                    activated_effect=None, layout_strategy=verticalMenuLayout):

        super(BrandedMenu, self).create_menu(items, selected_effect, unselected_effect, activated_effect, layout_strategy)

        delay = 0.3
        for i in items:
            i.scale=0
            i.do(Delay(delay)+
                Accelerate(ScaleTo(1.3,duration=0.3), 2)+
                ScaleTo(1,duration=0.1))
            delay += 0.2


class AnimatedMenuItem(MenuItem):
    def __init__(self, text, callback, delay = 2):
        super(AnimatedMenuItem, self).__init__(text, callback)
        self.scale = 0
        self.do(Delay(delay)+ScaleTo(1.1,duration=0.2)+ScaleTo(1,duration=0.1))
        

class MainMenu(BrandedMenu):
    """Main menu for the game"""
    def __init__(self):
        super(MainMenu, self).__init__()

        items = []
        self.title=""
        items.append(MenuItem('Play', self.on_new_game))
#        items.append(MenuItem('Scores', self.on_score))
        items.append(MenuItem('Story', self.on_story))
        items.append(MenuItem('Credits', self.on_credits))
#        items.append(MenuItem('Editor', self.on_editor,delay = 1.2))
#        items.append(MenuItem('Options', self.on_configure))
        items.append(MenuItem('Quit', self.on_quit))
        self.create_menu(items, zoom_in(1.4), zoom_out(), shake())

    def on_new_game(self):
        #director.push(game_scene)
        director.push(FadeTransition(intro_scene.get_scene(),duration = 0.4))

    def on_editor(self):
        director.push(FadeTransition(reader_scene.CreditsScene(),duration = 0.4))

    def on_credits(self):
        director.push(FadeTransition(reader_scene.CreditsScene(),duration = 0.4))
        
    def on_story(self):
        director.push(FadeTransition(reader_scene.StoryScene(),duration = 0.4))

    def on_score(self):
        print "Aca mostramos los Scores"

    def on_configure(self):
        self.parent.switch_to(1)
       # print "Aca vamos a la configuracion"

    def on_quit(self):
        pyglet.app.exit()


class ConfigMenu(Layer):
    """Config menu"""
    def __init__(self):
        super(ConfigMenu, self).__init__()
        menu = ConfigMenuMenu()
        fo = pyglet.font.load(menu.font_item['font_name'], menu.font_item['font_size'])
        fo_height = int( (fo.ascent - fo.descent) * 0.9 )
        font_item = {}
        font_item['font_name'] = menu.font_item['font_name']
        font_item['font_size'] = menu.font_item['font_size'] + 10
        font_item['anchor_x'] = "right"
        font_item['x'] = 770
        font_item['y'] = int(180)
        font_item['text'] = 'Options'
        label = Label(**font_item )

        
        self.add(menu)
        self.add(label)
        
class ConfigMenuMenu(BrandedMenu):
    """Config menu"""
    def __init__(self):
        super(ConfigMenuMenu, self).__init__('')

        self.font_title['font_size'] = 20
        self.font_item_selected['font_size'] = 20
        self.font_item['font_size'] = 20
        
        l = []
        volumes = ['Mute', '10','20', '30', '40', '50', '60', '70', '80', '90', 'Max']
        l.append( MultipleMenuItem('Music Volume: ', self.on_music_volume, volumes, 7))
        l.append( MultipleMenuItem('SFX Volume: ', self.on_sfx_volume, volumes, 7))
        l.append( MenuItem('Fullscreen', self.on_fullscreen))
        l.append( MenuItem('Back', self.on_quit))
        self.create_menu(l, zoom_in(1.4), zoom_out(), shake())

    def on_music_volume(self, value):
        print 'music volume: %d' % value
        sounds.sound_volume(value/10)

    def on_sfx_volume(self, value):
        print 'sfx volume: %d' % value
        sounds.sound_volume(value/10)

    def on_fullscreen(self):
        director.window.set_fullscreen( not director.window.fullscreen )

    def on_quit(self):
        print "Thanks for playing!"
        self.parent.parent.switch_to(0)

class PauseMenu(BrandedMenu):
    """Pause menu"""
    def __init__(self):
        super(PauseMenu, self).__init__('Paused')

        l = []
        l.append( MenuItem('Continue', self.on_continue))
        l.append( MenuItem('Quit to Main Menu', self.on_main_menu))
        l.append( MenuItem('Exit', self.on_quit))
        self.create_menu(l)
        sounds.stop_music()

    def on_continue(self):
        sounds.play_music()
        director.pop()

    def on_main_menu(self):
        print "Thanks for playing!"
        director.pop()
        director.pop()
        sounds.set_music('music/intro.ogg')

    def on_quit(self):
        print "Thanks for playing!"
        sys.exit()


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
#                print "sprite agregado", self.batch
    def back_batch(self):
        return self.batch

class MainMenuScene(Scene):
    def __init__(self):
        super(MainMenuScene, self).__init__()
        self.add(DisableEscapeKeyLayer())

    def on_enter(self):
        sounds.set_music('music/intro.ogg')
        super(MainMenuScene, self).on_enter()

class PauseMenuScene(Scene):
    def __init__(self):
        super(PauseMenuScene, self).__init__()
        self.add(DisableEscapeKeyLayer())

    def on_enter(self):
        sounds.stop_music()
        super(PauseMenuScene, self).on_enter()



def get_scene():
    menu_layer = MultiplexLayer(MainMenu(), ConfigMenu())
#    back = BackgroundLayer('bgs/menu_background.jpg')
#    back_layer.add(back.back_batch())
    back_layer = Layer()
    bg_sprite = Sprite('bgs/menu_background.jpg')
    bg_sprite.x = bg_sprite.width/2
    bg_sprite.y = bg_sprite.height/2
    back_layer.add(bg_sprite)
    scene = MainMenuScene()
    scene.add(back_layer, z=0)
#    menu_layer.image = 'bgs/menu_background.jpg'
    scene.add(menu_layer)
    return scene

def pause_menu():
    w, h = director.window.width, director.window.height
    texture = pyglet.image.Texture.create_for_size(
                    GL_TEXTURE_2D, w, h, GL_RGBA)
    texture.blit_into(pyglet.image.get_buffer_manager().get_color_buffer(), 0,0,0)
    scene = PauseMenuScene()
    bg = Sprite(texture.get_region(0, 0, w, h))
    bg.x=w/2;
    bg.y=h/2;
    scene.add(bg,z=-999)
    overlay = ColorLayer(25,25,25,205)
    scene.add(overlay)
    menu = PauseMenu()
    scene.add(menu)
    return scene