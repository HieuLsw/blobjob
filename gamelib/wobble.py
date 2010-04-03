from cocos.actions.interval_actions import *
from cocos.actions.instant_actions import *
from cocos.tiles import MapLayer
from cocos.cocosnode import CocosNode
import pyglet.window.key
import pyglet
from cocos.actions.base_actions import Repeat
from cocos.actions.grid3d_actions import *
import pyglet.image
from cocos.tiles import *

import os
import sounds

from cocos.layer import Layer
from cocos.sprite import Sprite

def jump_up(callback=None):
    return MoveBy((0,400),duration=0.5) + CallFunc(callback)

def jump_down(callback=None):
    return MoveBy((0,-400),duration=0.5) + CallFunc(callback)

class Wobble(Layer):
    is_event_handler = True
    def __init__(self, position = (2,1), level = None):
        super(Wobble,self).__init__()
        self.level = level
        
        self.move_speed = 200
        self.status = "still"
        self.facing = "up"
        self.can_jump = True
        
        self.keyboard = {
            'LEFT'  :   False,
            'RIGHT' :   False,
            'SPACE' :   False,
            'UP'    :   False,
            'DOWN'  :   False,
        }
        self.sequences ={
            'still': [
                'blob_1.png',
                ],
            'walk': [
                'blob_1.png',
                'blob_2.png',
                'blob_3.png',
                'blob_4.png',
                'blob_5.png',
                'blob_6.png',
                'blob_7.png',
                'blob_6.png',
                'blob_5.png',
                'blob_4.png',
                'blob_3.png',
                'blob_2.png',
                'blob_1.png',
                ],
            'jump': [
                'blob_8.png',
                ],
            'death': [
                'death_1.png',
                'death_2.png',
                'death_3.png',
                'death_4.png'
            ]
        }
        
        self.tile_types = {
            'block-02': 'wall',
            'block-03': 'wall',
            'block-04': 'wall',
            'block-05': 'wall',
            'block-06': 'wall',
            'block-07': 'air',
            'block-08': 'air',
            'block-09': 'air',
            'block-10': 'air',
            'block-11': 'bad',
            'block-12': 'bad',
        }
        self.images = {}
        for animation in self.sequences:
            self.images[animation] = (pyglet.image.load("data/chars/wobble/"+filename) for filename in self.sequences[animation])
#            self.images[animation] = (pyglet.image.load(os.path.join("chars","wobble",filename)) for filename in self.sequences[animation])
        
        self.animations = {
            'still': Sprite(pyglet.image.Animation.from_image_sequence(self.images['still'], 1, True)),
            'walk' : Sprite(pyglet.image.Animation.from_image_sequence(self.images['walk'], 0.05, True)),
            'jump' : Sprite(pyglet.image.Animation.from_image_sequence(self.images['jump'], 1, True)),
#            'death': Sprite(pyglet.image.Animation.from_image_sequence(self.images['death'], 0.2, False)),
        }

#        print self.animations
#        self.sprite = Sprite(self.animations['still'])
        self.char = CocosNode()
        self.char.scale = 0.75
        self.set_grid_position(position)
        self.x = 0
        self.y = 0

        self.sprite = None
        self.add(self.char)
        
        self.set_animation()
#        self.sprite = Sprite(self.animations['jump'])
#        self.do(Repeat(Liquid(waves=5,amplitude=5)))
        self.do(Repeat(Waves(hsin=False)))
        self.do(Repeat(Waves(vsin=False,amplitude=5)))
        self.schedule(self.step)
        self.grid_type(1, 1)

    def set_grid_position(self,position):
        x = self.grid_x_to_x(position[0])
        y = self.grid_y_to_y(position[1])

        print "iniciando en ",x,",",y
        self.char.x = x
        self.char.y = y

    def grid_x_to_x(self, grid_x):
        return grid_x  * 50 + 25
    
    def grid_y_to_y(self, grid_y):
         y = grid_y  * 50 + 25
         return y

    def x_to_grid_x(self, x):
        return round((x - 25)  / 50)

    def y_to_grid_y(self, y):
        return round((y - 25)  / 50)

    def pos_to_grid(self,x,y):
        return self.x_to_grid_x(x),self.y_to_grid_y(y)

    def char_to_grid(self):
        posx = self.char.x
        posy = self.char.y
        if self.facing == "down":
            posy += 50

        return self.pos_to_grid(posx, posy)

    
    def grid_type(self,grid_x,grid_y = None):
        if(grid_y == None):
            grid_y = grid_x[1]
            grid_x = grid_x[0]
            
        x = self.grid_x_to_x(grid_x)
        y = self.grid_y_to_y(grid_y)
        return self.grid_type_at_pixel(x, y)

    def grid_type_at_pixel(self,x,y):
        type = 'air'
        for id,layer in self.level.find(MapLayer):
            cell = layer.get_at_pixel(x, y)
            if(cell):
                tile = cell.tile
                if(tile and self.tile_types[tile.id]):
                    type = self.tile_types[tile.id]
        return type

    def char_left_tile_type(self):
        posY = self.char.y
        if(self.facing == "down"):
            posY = self.char.y + 50
            
        posX = self.char.x - 40
        return self.grid_type_at_pixel(posX, posY)

    def char_right_tile_type(self):
        posY = self.char.y
        if(self.facing == "down"):
            posY = self.char.y + 50
#        else:
#            posY = self.char.y + 75
        posX = self.char.x + 40
        return self.grid_type_at_pixel(posX, posY)

    def char_ground_tile_type(self):
        if(self.facing == "up"):
            posY = self.char.y -25
        else:
            posY = self.char.y + 75
        return self.grid_type_at_pixel(self.char.x, posY)
    
    def set_animation(self,name=None):
        if(name == None):
            name = self.status
        if(self.sprite != self.animations[name]):
            if(self.sprite):
                self.char.remove(self.sprite)
            self.sprite = self.animations[name]
            self.char.add(self.sprite)
            self.sprite.x = 0
            self.sprite.y = 0
         
    def char_jump_block(self):
        delta = 1
        if(self.facing == "down"):
            delta = -1
        x,y = self.char_to_grid()
        while self.grid_type(x,y) == 'air' and y > -2 and y < 15 :
            y += delta
        
        return y

    def step(self, dt):
        kb = self.keyboard


        if(self.status != 'death'):
            if self.char.x <= self.parent.manager.fx - 375:
                self.die()
                return

            my_tile = self.char_to_grid()
            my_tile_type = self.grid_type(my_tile[0],my_tile[1])
            ground_tile_type = self.char_ground_tile_type()
            if(ground_tile_type == "bad" or my_tile_type == "bad"):
                self.die()
            elif(ground_tile_type == "air"):
                if(self.facing == "up"):
                    direction = -1
                else:
                    direction = 1
                self.char.y += direction * 400 * dt
            else: #ON WALL
                if(self.status != 'jump'):
                    if(kb['LEFT']):
                        left_tile_type = self.char_left_tile_type()
                        if left_tile_type != 'wall':
                            self.char.x -= self.move_speed * dt
                            self.status = 'walk'
                            self.set_animation()

                    elif(kb['RIGHT']):
                        right_tile_type = self.char_right_tile_type()
    #                    print right_tile_type
                        if right_tile_type != 'wall':
                            self.char.x += self.move_speed * dt
                            self.status = 'walk'
                            self.set_animation()
                    else:
                        self.status = "still"
                        self.set_animation()

                    if(kb['SPACE'] and self.can_jump):
                        self.status = 'jump'
                        self.can_jump = False
                        self.set_animation()
                        if(self.facing == "down"):
                            self.jump_down()
                        else:
                            self.jump_up()

                    elif(kb['UP']):
                        self.status = 'jump'
                        self.jump_up()
                    elif(kb['DOWN']):
                        self.status = 'jump'
                        self.jump_down()
                else: #JUMPING
                    pass
        else: #dead
            pass

    def die(self):
        if self.status != "death":
            self.status = 'death'
            sounds.play("sfx/hurt.ogg")
    #        self.set_animation()

            self.char.remove(self.sprite)
            self.char.add(Sprite(pyglet.image.Animation.from_image_sequence(self.images['death'], 0.05, False)))

            self.char.do(JumpBy(height=150,jumps=3,duration=2) + CallFunc(self.parent.char_die))
        

    def jump_up(self):
#        self.char.do(jump_up(self.end_jump))
        self.char.do(MoveTo((self.char.x,self.grid_y_to_y(self.char_jump_block()-2)),duration=0.2) + CallFunc(self.end_jump))
        self.facing = "down"
        sounds.play("sfx/jump.ogg")
#        print self.char_to_grid()

    def jump_down(self):
#        self.char.do(jump_down(self.end_jump))
        self.char.do(MoveTo((self.char.x,self.grid_y_to_y(self.char_jump_block()+1)),duration=0.2) + CallFunc(self.end_jump))
        self.facing = "up"
        sounds.play("sfx/jump.ogg")
#        print self.char_to_grid()

    def end_jump(self):
        self.status = 'still'
        if(self.facing=="up"):
            self.char.rotation = 0
            self.char.anchor_y = -10
        else:
            self.char.rotation = 180
            self.char.anchor_y = 5
            
#        self.char.do(FlipX3D(duration=0.01))
        
    def on_key_press(self, key, modifiers):
        key_name = pyglet.window.key.symbol_string (key)
        if key == pyglet.window.key.RIGHT or \
            key == pyglet.window.key.LEFT or \
            key == pyglet.window.key.SPACE:
            self.keyboard[key_name] = True
#            key == pyglet.window.key.UP or \
#            key == pyglet.window.key.DOWN or \

    def on_key_release(self, key, modifiers):
        key_name = pyglet.window.key.symbol_string (key)
        if key == pyglet.window.key.RIGHT or \
            key == pyglet.window.key.LEFT or \
            key == pyglet.window.key.SPACE:
            self.keyboard[key_name] = False
            self.can_jump = True
#            key == pyglet.window.key.UP or \
#            key == pyglet.window.key.DOWN or \
