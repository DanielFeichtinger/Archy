# audioTest.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import unittest
from audio import *

class NullSoundTest(unittest.TestCase):
    def testNothingHappens(self):
        sound = NullSound()
        sound.set_volume(None)
        sound.stop()
        sound.play()

class MusicSoundTest(unittest.TestCase):
    def test__init__(self):
        name = "Sample Name"
        sound = MusicSound(name)
        self.assertEquals(name, sound.soundName)

if __name__ == '__main__':
    unittest.main()
