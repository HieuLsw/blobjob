from cocos.actions.interval_actions import *
from cocos.actions.grid3d_actions import *
from cocos.scenes.transitions import *

def blob_fade_transition(scene,duration = 0.2):
    return FadeTransition(scene, duration)


def zoom_in(scale=1.5, duration=0.2):
    '''Predefined action that scales to 1.5 factor in 0.2 seconds'''
    d = duration
    return ScaleTo( scale, duration=d ) + Shaky3D(duration=d/2, randrange=3)
#    return ScaleTo( scale, duration=d ) + shake()

def zoom_out(scale=1.0, duration=0.2):
    '''Predefined action that scales to 1.0 factor in 0.2 seconds'''
    d = duration
    return ScaleTo( scale, duration=0.2 )
