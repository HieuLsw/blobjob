
from cocos.text import Label
from cocos.scene import Scene
from game_scene import BilboardScene
import data

class ReaderScene(BilboardScene):
    image = "bgs/credits.jpg"
    font_item = {
        'font_name' : 'Casual',
        'font_size' : 15,
        'anchor_x'  : "center",
        'anchor_y'  : "top",
        'halign'    : "center",
        'color'     : (30,30,30,255),
        'x'         : 400,
        'y'         : 580,
        'multiline' : True,
        'width'     : 370,
        'height'    : 600,
        'bold'      : False,
    }
    def __init__(self):
        super(ReaderScene, self).__init__()
        self.text = ""
        if(self.text_file):
            self.text = data.load(self.text_file).read()

        self.font_item['text'] = self.text
        label = Label(**self.font_item )
        label.content_width = 300
        self.label = label
        self.add(label,z=9999)
        print self.text
        

class StoryScene(ReaderScene):
    text_file = 'txt/story.txt'
    def __init__(self):
        self.font_item['font_size'] = 10
        super(StoryScene, self).__init__()

class CreditsScene(ReaderScene):
    text_file = 'txt/credits.txt'
    def __init__(self):
        self.font_item['font_size'] = 15
        super(CreditsScene, self).__init__()

