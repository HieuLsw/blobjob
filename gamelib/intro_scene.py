# To change this template, choose Tools | Templates
# and open the template in the editor.



from cocos.scene import Scene
from cocos.layer.base_layers import Layer
from cocos.sprite import Sprite
from cocos.director import director

import game_scene

class IntroHandlerLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(IntroHandlerLayer,self).__init__()

    def on_key_press(self, key, modifiers):
        director.replace(game_scene.next_level())

class IntroScene(Scene):
    
    def __init__(self):
        super(IntroScene,self).__init__()
        bg = Layer()
        bg.image = 'bgs/howto_bg.jpg'
        sprite = Sprite(bg.image)
        sprite.x = 400
        sprite.y = 300
        bg.add(sprite)
        self.add(bg)
        self.add(IntroHandlerLayer())

        
def get_scene():
    scene = IntroScene()

    print "Showing Game Tutorial"
    return scene