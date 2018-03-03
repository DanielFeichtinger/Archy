# keyboardTest.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import unittest
from commands.tutorial.keyboard import *

class KeyboardTest(unittest.TestCase):
    def testInitialization(self):
        self.assert_(visible() >= 0)

    def testShowHide(self):
        hide()
        self.failIf(visible())
        self.assertEqual('', shownKey())
        
        sampleKey = 'Sample Key'

        show(sampleKey)
        self.assert_(visible())
        self.assertEqual(sampleKey, shownKey())

        hide()
        self.failIf(visible())
        self.assertEqual('', shownKey())
        
        show()
        self.assert_(visible())
        self.assertEqual('', shownKey())


if __name__ == '__main__':
    unittest.main()
