from cocos.scene import Scene
from cocos.layer import Layer

class BilboardScene(Scene):
    def __init__(self):
        super(BilboardScene,self).__init__()
        if(self.image):
            self.sprite = Sprite(self.image)
            self.sprite.x = self.sprite.width/2
            self.sprite.y = self.sprite.height/2
            self.add(self.sprite)
        self.add(BilboardControlLayer())

class BilboardControlLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(BilboardControlLayer,self).__init__()

    def on_key_press(self, key, modifiers):
        director.pop(blob_fade_transition)
        return True

    def on_mouse_press(self, x, y,  buttons, modifiers):
        director.pop(blob_fade_transition)
