
from cocos import tiles
from cocos.scene import Scene
from cocos.layer import ScrollingManager
from cocos.layer import Layer

class GameMapScene(Scene):
    def __init__(self,level_xml,contents=None):
        super(GameMapScene, self).__init__(contents)

#        self.remove(self.manager)
        self.manager = ScrollingManager()
        self.add(self.manager)

        level = tiles.load(level_xml)
        print level
        mz = 0
        for id, layer in level.find(tiles.MapLayer):
            print layer
            self.manager.add(layer, z=layer.origin_z)
            mz = max(layer.origin_z, mz)

        
        self.add(GameControlLayer(self.manager, 10))

    def step(self,dt):
        print "step"

        
        

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
        self.fx += self.speed*dt
        self.manager.force_focus(self.fx, self.fy)
