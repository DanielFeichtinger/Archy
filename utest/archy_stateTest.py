# archy_stateTest.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import unittest
from archy_state import *

class ArchyStateTest(unittest.TestCase):
    def testCreate(self):
        state = ArchyState()
        self.failIf(state.screenSurface)
        self.failIf(state.mainText)
        self.failIf(state.mainTextViewer)
        self.failIf(state.quasiModeText)
        self.failIf(state.quasiModeTextViewer)
        self.failIf(state.whitespaceVisible)
        self.failIf(state.preselectionVisible)
        self.failIf(state.stylePool)
        self.failIf(state.commandMap)
        self.failIf(state.commandHistory)
        self.failIf(state.keyState)

if __name__ == '__main__':
    unittest.main()
