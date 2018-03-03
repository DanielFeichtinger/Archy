# text_array.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: text_array.hpy,v 1.16 2005/02/10 23:06:51 andrewwwilson Exp $"

# Archy wide global items
import archy_globals

# --------------------------
# The TextArray class
# --------------------------

# Eventually we will move to use the array module for faster access to text.
# Eventually, we will move to using a proper Buffer Gap for better memory usage.

# For now, we will make do with the Python string.

class TextArray:
    def __init__(self, contents):
        self.initialize(contents)

    def initialize(self, contents=""):
        #print "in TextContent.initialize()"
        self._contents = contents
        self._touched = 0
        
    def clearText(self):
        self.initialize()

    def getLength(self):
        return len(self._contents)

    def raw_find(self, sub, start=0, end=-1):
        return self._contents.find(sub, start, end)

    def raw_rfind(self, sub, start=0, end=-1):
        return self._contents.rfind(sub, start, end)

    def find(self, pattern, start, direction = 1):
        return self._boyerMooreFind(pattern, start, direction)

    def _boyerMooreFind(self, pattern, start, direction):
        import bmh_search
        if direction == 1:
            return bmh_search.BMHSearchForward(self._contents, pattern, start)
        else:
            return bmh_search.BMHSearchBackward(self._contents, pattern, 0, start)

    def _naiveFind(self, pattern, start, direction):

# NOTE: This method does not perform a search as per the Leap spec.  Specifically, the search is entirely case-insensitive, even if there are capital letters in the pattern string.

        pattern = pattern.lower()
        content = self._contents.lower()
        if direction == 1:
            return content.find(pattern, start)
        else:
            return content.rfind(pattern, 0, start)

    def addText(self, value, pos=-1):
        #print "in content.TextContent.addText:" + str(value) + "<< pos=" + str(pos)
        if pos < 0 or len(self._contents)-1 < pos :
            pos = -1

        #print "TextContent.addText(). pos = ", pos,
        #print "value="+value+"<<"
        if pos == -1:
            self._contents = self._contents + value
        else:
            self._contents = "".join((self._contents[0:pos], value, self._contents[pos:len(self._contents)]))

        #print "contents:"+self._contents

        self._touched = 1

# Delete text from start..end inclusive.  start and end are enforced to be positive and valid

    def delText(self, start, end):
        if end < start:
            return

        if len(self._contents) - 1 < start:
            return

        if end < 0:
            return

        if start < 0:
            start = 0

        if len(self._contents) - 1 < end:
            end = len(self._contents) - 1


        self._contents = self._contents[0:start] + \
            self._contents[end+1: len(self._contents)]

        self._touched = 1



    def wasTouched(self):
        if self._touched:
            self._touched = 0
            return 1
        else:
            return 0

# Return a character at position pos

    def getChar(self,pos):
        return self._contents[pos:pos+1]

# Return a substring from positions start..end inclusive.

    def getSubString(self, start, end):
        pass
        n = len(self._contents)-1
        if end < 0:
            return ""
        if n < start:
            return ""
        if end < start:
            return ""
        start = archy_globals.bound(start,0,n)
        end = archy_globals.bound(end,0,n)
        return self._contents[start:end+1]