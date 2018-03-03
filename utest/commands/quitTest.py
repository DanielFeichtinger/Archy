# quitTest.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import unittest
from commands.quit import *

class QuitCommandTest(unittest.TestCase):
    def testBasics(self):
        command = QuitCommand()
        self.assertEqual("QUIT", command.name())
        self.failIf(command.recordable())

if __name__ == '__main__':
    unittest.main()
