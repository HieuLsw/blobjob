# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008 Daniel Moisset, Ricardo Quesada, Rayentray Tappa, Lucio Torre
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
'''cocos2d
cocos2d is a framework for building 2D games, demos, and other graphical/interactive applications.

Main Features:
--------------
    * Flow control: Manage the flow control between different scenes in an easy way
    * Sprites: Fast and easy sprites
    * Actions: Just tell sprites what you want them to do. Composable actions like move, rotate, scale and much more
    * Effects: Effects like waves, twirl, lens and much more
    * Tiled Maps: Support for rectangular and hexagonal tiled maps
    * Transitions: Move from scene to scene with style
    * Menus: Built in classes to create menus
    * Text Rendering: Label and HTMLLabel with action support
    * Documentation: Programming Guide + API Reference + Video Tutorials + Lots of simple tests showing how to use it
    * Built-in Python Interpreter: For debugging purposes
    * BSD License: Just use it
    * Pyglet Based: No external dependencies
    * OpenGL Based: Hardware Acceleration

http://cocos2d.org
'''

__version__ = "0.3.0"
__author__ = "cocos2d team"
version = __version__



# add the cocos resources path
import os, pyglet
pyglet.resource.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources"))
pyglet.resource.reindex()
try:
    unittesting = os.environ['cocos_utest']
except KeyError:
    unittesting = False
del os, pyglet

def import_all():
    import actions
    import director
    import layer
    import menu
    import sprite
    import path
    import scene
    import grid
    import text
    import camera
    import draw
    import skeleton

if not unittesting:
    import_all()
