# To change this template, choose Tools | Templates
# and open the template in the editor.

import sounds

class Sfx:
    def __init__(self,sound):
        try:
            self.snd = sound
            sounds.load(self.snd)
        except e:
            print "Error loading "+sound

    def play(self):
        sounds.play(self.snd)
