# audio.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import pygame

# Frequency to initialize mixer with
MIXER_FREQUENCY = 44100

def _checkFileExists(filename):
    "Ensures the given file exists and can be read."

    f = open(filename, "r")
    f.close()

def init():
    try:
        pygame.mixer.init(MIXER_FREQUENCY)
    except:
        print "Failed to initialize sound system"
        import debug
        print debug.get_traceback()


def isAvailable():
    return pygame.mixer.get_init() != None

def getSound(soundName):
    _checkFileExists(soundName)
    if not isAvailable():
        return NullSound()
    if soundName.endswith(".ogg"):
        return MusicSound(soundName)
    return pygame.mixer.Sound(soundName)

class MusicSound:
    def __init__(self, soundName):
        self.soundName = soundName

    def set_volume(self, level):
        pygame.mixer.music.set_volume(level)

    def stop(self):
        pygame.mixer.music.stop()

    def play(self):
        pygame.mixer.music.load(self.soundName)
        pygame.mixer.music.play()

class NullSound:
    def set_volume(self, level):
        pass

    def stop(self):
        pass

    def play(self):
        pass
