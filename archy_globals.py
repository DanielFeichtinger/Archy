# archy_globals.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: the_globals.hpy,v 1.11 2005/04/04 04:04:54 andrewwwilson Exp $"

# --------------------------
# Global variables
# --------------------------

lastSearchString = ""
lastSearchDirection = ""

verbose = 0

keyCount = 0
deletionDoc = 1
autoSave = 1
creptBack = 0
restored = 0

appIsRunning = 1

# --------------------------
# A note on debugging interactive systems
# --------------------------

# One recurring difficulty with debugging the "paint"
# messges of interactive programs is that the windows of 
# the debugger and the program being debugged overlap.

# Sometimes things that were painted get overwritten and erased
# by the debugger window, and other times extra paint messages
# get generated and it is confusing to distinguish the "true"
# paint messages that would occur during normal usage, and 
# the ones that were generated due to the focus changes between
# the program and the debugger. Kind of like a "Heisenberg Principle"
# of debugging [apologies to Physicists].

# The "correct" way to handle this would be to
# use multiple screens and/or a remote debugger but this can
# be cumbersome.  Print statements to a debug file usually work
# well for the majority of problems.

# --------------------------
# The debug log
# --------------------------

# We define the debug log file here and a simple wrapper for 
# printing to it.

# createDebugFile() - 
# create the file

# writeDebugFile() -
# write a string to the debug file

# - Han Kim Dec 6 2003

theDebugFile = None

def createDebugFile():
    global theDebugFile
    #theDebugFile = open("ArchyDebug.txt","w")

def writeDebugFile(str):
    global theDebugFile
    if theDebugFile == None:
        pass
        #createDebugFile()
    else:
        pass
        #theDebugFile = open("ArchyDebug.txt","a")
    #theDebugFile.write(str)
    #theDebugFile.close()

# --------------------------
# In-range function
# --------------------------

# Utility function that returns true if value is within a range

def inRange(value, lo, hi):
    if lo <= value and value <= hi:
        return true
    else:
        return false

# --------------------------
# Bounding function
# --------------------------

# Utility function to restrict the value to a range

def bound(value, lo, hi):
    if value < lo:
        return lo
    if hi < value:
        return hi
    return value

# --------------------------
# Range intersection
# --------------------------

# Return the intersection of a range. Returns a invalid range where
# start > end if there is no intersection.

def intersection(range1, range2):
    return [ max(range1[0], range2[0]) , min(range1[1], range2[1]) ]



def doRangesOverlap(rangeA, rangeB):
    #the ranges should be in the form of a tuple
    #find which range starts first
    if rangeA[0] < rangeB[0]:
        minRange = rangeA
        maxRange = rangeB
    else:
        minRange = rangeB
        maxRange = rangeA
    #now we see if the min range extends into the max range
    if minRange[1] >= maxRange[0]:
        return 1
    else:
        return 0

# --------------------------
# Key processing constants
# --------------------------

# I am here defining a set of constants for the universal handling of keystrokes.
# For new platforms / implementations, simply change the values of these constants

# Shift-key character modification
# --------------------------

# The following function returns the character for the given character as though the shift key was pressed; for instance, given the character "a", it would return "A", and given the character "2", it would return "@".

SHIFTED_KEYS = {u'~':u'`', u'!':u'1', u'@':u'2', u'#':u'3', u'$':u'4', u'%':u'5', u'^':u'6', u'&':u'7', u'*':u'8', u'(':u'9', u')':u'0', u'_':u'-', u'+':u'=', u'{':u'[', u'}':u']', u'|':u'\\', u':':u';', u'\"':u'\'', u'<':u',', u'>':u'.', u'?':u'/'}

UNSHIFTED_KEYS = {u'`':u'~', u'1':u'!', u'2':u'@', u'3':u'#', u'4':u'$', u'5':u'%', u'6':u'^', u'7':u'&', u'8':u'*', u'9':u'(', u'0':u')', u'-':u'_', u'=':u'+', u'[':u'{', u']':u'}', u'\\':u'|', u';':u':', u'\'':u'\"', u',':u'<', u'.':u'>', u'/':u'?' }

def apply_shift_key_to_character(char):
    char = char.upper()
    if char in UNSHIFTED_KEYS: 
        char = UNSHIFTED_KEYS[char]
    return char

def remove_shift_key_from_character(char):
    char = char.lower()
    if char in SHIFTED_KEYS: 
        char = SHIFTED_KEYS[char]
    return char


# Key State Constants

# Currently maintaining the Mac OS 9 values for code compatability.

Key_down   = 3  #  A keyboard key has been pressed.
Key_up     = 4  #  A keyboard key has been released.
Key_auto   = 5  #  A key is being auto-repeated
Mouse_down  = 1  #  A mouse button is down
Mouse_up   = 2  #  A mouse button has been realeased.

# Key Constants

# Currently maintaing the Mac OS 9 values for code compatability.

Left_shift        = 0x38
Right_shift       = 0x38
Left_command      = 0x37
Right_command     = 0x37
Left_altOrOption  = None
Right_altOrOption = None

# Key Modifiers

# Currently maintaing the Mac OS 9 values for code compatability.

def isLeftShiftDown(M):
    return (M%1024 - M%256)/512

def isRightShiftDown(M):
    return (M%1024 - M%256)/512

def isLeftCommandDown(M):
    return (M%512 - M%128)/256

def isRightCommandDown(M):
    return (M%512 - M%128)/256

def isLeftOptionDown(M):
    return (M%2048 - M%512)/1024

def isRightOptionDown(M):
    return (M%2048 - M%512)/1024

def isLeftOptionDown(M):
    return (M%8192 - M%2048)/4096

def isRightOptionDown(M):
    return (M%8192 - M%2048)/4096

def isLeftMouseButtonDown(M):
    return not ((M%256- M%64)/128)

def isRightMouseButtonDown(M):
    return not ((M%256- M%64)/128)

# --------------------------
# Functions to aid in moving the cursor with text
# --------------------------

# The functions updateTextPositionOnAdd(position, insertPos, length) and updateTextPositionOnDelete(position, startDel, endDel) return the position within the text that keeps the position, on the same character when new text when is added or deleted. If the position itself is deleted the position "collapses" onto the start of the deletion.

# The calling code needs to take care of error handling and validation of values. insertPos should be a valid document position and length > 0. startDel <= endDel and valid text positions.

def updateTextPositionOnAdd(position, insertPos, length):
    if insertPos <= position:
        return position + length
    return position
#end function updateTextPositionOnAdd

def updateTextPositionOnDelete(position, startDel, endDel):
    if position < startDel:
        return position
    if startDel <= position and position <= endDel:
        #the position is within the deleted range
        return startDel
    if endDel < position:
        length = endDel - startDel + 1
        return position - length
#end function updateTextPositionOnDelete


