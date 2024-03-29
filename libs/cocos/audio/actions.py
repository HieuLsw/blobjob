from cocos import actions
from cocos import audio

class PlayAction(actions.InstantAction):
    def init(self, sound):
        self.sound = sound

    def start(self):
        if audio._working:
            self.sound.play()
    
    def __deepcopy__(self, memo):
        # A shallow copy should be enough because sound effects are immutable
        # Also, we don't need to use the memo, because there can not be a cycle
        return PlayAction(self.sound)

