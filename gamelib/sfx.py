# To change this template, choose Tools | Templates
# and open the template in the editor.

import sounds

class Sfx:
    def __init__(self, sound):
        try:
#            self.snd = sounds.load(sound)
            self.snd = sound
        except e:
            print "Error loading " + sound

    def play(self):
#        print "Playing sound " + str(self.snd)
        try:
            sounds.play(self.snd)
        except Exception, inst:
            print "Error, cant play sound "
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to printed directly

