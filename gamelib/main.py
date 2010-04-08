'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

#
# cocos2d
# http://cocos2d.org
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import data
import pyglet
import game_menu
from cocos.director import director


def main():
    pyglet.font.add_directory(data.filepath('fonts'))
    pyglet.resource.path.append(data.filepath('.'))
    pyglet.resource.path.append(data.filepath('maps'))
    pyglet.resource.path.append(data.filepath('chars'))
    pyglet.resource.reindex()
    
    director.init(resizable=True, width=800, height=600, audio=None)
    s = game_menu.get_scene()
    director.run( s )
