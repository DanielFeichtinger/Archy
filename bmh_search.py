# bmh_search.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: bmh_search.hpy,v 1.6 2005/02/15 23:42:12 bzwebcorp Exp $"

# VERSION 40

# BMH_SEARCH MODULE

# NOTE:

# The BMH(Boyer-Moore Horspool) algorithm is used to implement Leap(tm). See the Technical Specifications at raskincenter.org for information on the Leap patents using Leap for non-commercial purposes.

# AUTHORS AND EDITORS

# Written by Aza Raskin 28 July 2001 (Used Boyer Moore pattern matching algorithm)
# Modified by Rebecca Fureigh 5 August 2001
# Modified by Aza Raskin 6 August 2001
# Turned into SP0010 by Jef 7 August 2001
# Modified by Aza Raskin 8 August 2001
# Edits by Jef 8 Aug 2001
# Added the humane cursor. Aza Raskin 10 August 2001.
# Modified by Rebecca Fureigh 13 August 2001
# Modified by Aza Raskin 13 August 2001
# Modified by Rebecca Fureigh 14 August 2001
# Modified by Aza Raskin 14 August 2001
# Modified by Atul Varma 15 November 2004 (Adapted the Boyer-Moore-Horspool)

# EXPLANATION OF ARCHY BMH(Boyer Moore Horspool) pattern matching.

# An excellent explanation and C++ implementation of the fast string search method can be found at the web site:

# http://www.glenmccl.com/bmh.htm

# SPEED ISSUES

# Currently, the efficiency of this code is improved by a factor of about 25 when Psyco is used to accelerate it.

# --------------------------
# Imported modules
# --------------------------

import archy_globals

# --------------------------
# Global constants
# --------------------------

MATCH = 1
NOT_MATCH = 0
# --------------------------
# Supplementary character and pattern matching functions
# --------------------------

# The following function returns a tuple of characters that will match the given character under the current Leap spec.  For example, getPossibleMatchingChars('x') should return ('x', 'X').

def getPossibleMatchingChars(char):
  if char.islower():
    return (char,char.upper())
  else:
    shiftedChar = archy_globals.apply_shift_key_to_character(char)
    if shiftedChar <> char:
      return (char, shiftedChar)
    return (char)

# The following function takes a Leap pattern and returns a list of tuples, where each tuple is a list of characters that can match the corresponding position of the pattern.  For instance, makePatternList('Hi') should return [('H',), ('i','I')].

def makePatternList(patternStr):
  patternList = []
  for c in patternStr:
    patternList.append(getPossibleMatchingChars(c))
  return patternList

# The following function compares a pattern-list with a range of text.

def comparePattern(patternList, textString, start): ###############
  for i in range(0, len(patternList)):
    if textString[start+i] not in patternList[i]:
      return NOT_MATCH

# At this point, the entire pattern is a match.

  return MATCH

# --------------------------
# Supplementary BMH skip table creation functions
# --------------------------

# The following function Builds a Boyer-Moore-Horspool skip forward table.

def buildBMHSkipForwardTable(patternList):
  skipTable = {}
  patternLength = len(patternList)
  for i in range(0,patternLength-1):
    charList = patternList[i]
    for c in charList:
      skipTable[ c ] = patternLength - i - 1
  return skipTable

# The following function Builds a Boyer-Moore-Horspool skip backward table.

def buildBMHSkipBackwardTable(patternList):
  skipTable = {}
  patternLength = len(patternList)
  for i in range(patternLength-1,0,-1):
    charList = patternList[i]
    for c in charList:
      skipTable[ c ] = i
  return skipTable

# --------------------------
# BMH Search Forward function
# --------------------------

# The following function implements Boyer-Moore-Horspool search forward.

# The parameters to the function are the same as those for string.find().

def BMHSearchForward(textString, pattern, startPos=0, endPos=None):

# Do a validity check against empty pattern. Returns -1 if
# pattern can not be found or is an empty pattern.

  patternLength = len(pattern)
  if patternLength == 0:
    return -1

  if endPos == None:
    endPos = len(textString)

# We subtract 1 from the end position to make this function behave just like the string.find/rfind() functions.

  endPos -= 1

# Initialize things for a BMH Search

  patternList = makePatternList(pattern)
  
  skipTable = buildBMHSkipForwardTable(patternList)

  compareStart = startPos
  compareEnd = compareStart + patternLength - 1

# Continue searching as long as the pattern could possibly fit in the range
# [startPos..endPos] (inclusive). If a match is found, return the
# position where comparison started.

  while compareEnd <= endPos:
    res = comparePattern(patternList, textString, compareStart)
    if res == MATCH:
      return compareStart

# A match was not found, so update the next possible start of comparison,
# and try again.

    lastTextChar = textString[compareEnd]
    if skipTable.has_key(lastTextChar):

# Here, we will find how far we can shift the text "window" for a possible match.

      skipLength = skipTable[lastTextChar]
      compareStart = compareStart + skipLength
      compareEnd = compareStart + patternLength - 1
    else:

# At this point, we know the last text char to be compared did not occur at all within 
# the pattern. We can now move the start the whole length of the pattern.

      compareStart = compareEnd+1
      compareEnd = compareStart + patternLength - 1

# If we reached all the way here without returning, the pattern could not
# be found in the range [startPos..endPos](inclusive) of the text

  return -1

# --------------------------
# BMH Search Backward function
# --------------------------

# The following function implements Boyer-Moore-Horspool search backward.

# The parameters to the function are the same as those for string.rfind().

def BMHSearchBackward(textString, pattern, startPos=0, endPos=None):

# Do a validity check against empty pattern. Returns -1 if
# pattern can not be found or is an empty pattern.

  patternLength = len(pattern)
  if patternLength == 0:
    return -1

# Initialize things for a BMH Search

  if endPos == None:
    endPos = len(textString)

# We subtract 1 from the end position to make this function behave just like the string.find/rfind() functions.

  endPos -= 1

  patternList = makePatternList(pattern)
  
  skipTable = buildBMHSkipBackwardTable(patternList)
  compareEnd = endPos
  compareStart = compareEnd - patternLength + 1

# Continue searching as long as the pattern could possibly fit in the range
# [startPos..endPos] (inclusive). If a match is found, return the
# position where comparison started.

  while startPos <= compareStart:
    res = comparePattern(patternList, textString, compareStart)
    if res == MATCH:
      return compareStart

# A match was not found, so update the next possible start of comparison,
# and try again.

    firstTextChar = textString[compareStart]
    if skipTable.has_key(firstTextChar):

# Here, we will find how far we can shift the text "window" for a possible match.

      skipLength = skipTable[firstTextChar]
      compareStart = compareStart - skipLength
      compareEnd = compareStart + patternLength - 1
    else:

# At this point, we know the first text char to be compared did not occur at all within 
# the pattern. We can now move the start the whole length of the pattern.

      compareStart = compareStart - patternLength
      compareEnd = compareStart + patternLength - 1

# If we reached all the way here without returning, the pattern could not
# be found in the range [startPos..endPos](inclusive) of the text

  return -1
