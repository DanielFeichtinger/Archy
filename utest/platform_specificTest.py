# platform_specificTest.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import testUtil
import unittest
import platform_specific

class platform_specificTest(unittest.TestCase):
    def testInitialization(self):
        ini_msg = "Probably platform_specific is initialized before pygame"
        self.assert_(platform_specific.Command_Key, ini_msg)
        self.assert_(platform_specific.LEAP_Forward_Key, ini_msg)
        self.assert_(platform_specific.LEAP_Backward_Key, ini_msg)

if __name__ == '__main__':
    unittest.main()
