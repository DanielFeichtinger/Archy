# behaviorTest.hpy
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import unittest
import behavior

class BehaviorArrayTest(unittest.TestCase):
    def testIsValidPos(self):
        a = behavior.BehaviorArray()
        self.assertEquals(0, len(a._array))
        self.failIf(a.isValidPos(-1))
        self.failIf(a.isValidPos(0))
        self.failIf(a.isValidPos(1))

        a._array.insert(0, 1)
        self.assertEquals(1, len(a._array))
        self.failIf(a.isValidPos(-1))
        self.assert_(a.isValidPos(0))
        self.failIf(a.isValidPos(1))

if __name__ == '__main__':
    unittest.main()
