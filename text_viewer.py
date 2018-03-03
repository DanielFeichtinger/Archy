# text_viewer.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import glyph
import line
import surfaces
import archy_globals
from archy_state import archyState

# debugging code to print if on_screen_part has changed.

printed_selection_ranges = {}

def print_if_changed(selNum, selection_range):
  pass
  try:
    printed_range = printed_selection_ranges[selNum]
    if printed_range[0] <> selection_range[0] or printed_range[1] <> selection_range[1]:
      printed_selection_ranges[selNum] = selection_range
      print "text_viewer: selection ",selNum, ":", selection_range
      return 1
    return 0

  except KeyError:
    printed_selection_ranges[selNum] = selection_range
    print "text_viewer: selection ",selNum, ":", selection_range
    return 1
#end print_if_changed

# --- --- ---
# --- --- ---
# ARCHY TEXT VIEWER AND DISPLAY MANAGEMENT

# The text_view.TextViewer class manages a linked list of lines (line.Line objects). Each line corresponds to a line of text that can be displayed on the screen. Lines are composed of a list of glyphs. Each glyph corresponds to a single entry in the text array as well as a "character" on the screen.

# In addition to the list of lines, the TextViewer maintains indexes that link glyphs with specific text positions. The indexes are used to map between the glyphs and the text contents. These variables are :

# -firstGlyphPosition
# -firstScreenPosition
# -lastScreenPosition
# -lastGlyphPosition

# Other data that the TextViewer maintains is the Y positions of each of the visible lines and a reference to the line object that corresponds to the top displayed line on the screen.

# The TextViewer descendent classes HumaneDocumentTextViewer and CommandMessageViewer participate in MVC (or Observer) design patterns where HumaneDocumentText or CommandMessageText objects are Model(M) objects and a TextViewer is a View(V). The TextViewers have onAddText and onDelText methods that are called when text is added and deleted from the document.

# --- --- ---
# The Mapping Between the Lines and the Display
# --- --- ---

# While Archy is running, there will be at least as many lines of glyphs managed by the text viewer as there are displayed on the screen.

# A fresh screen is drawn by the method :

# - TextViewer.regenerateTextAroundCursor(self,pos).

# The lines of glyphs are generated one paragraph at a time. A paragraph is a range text that is terminated by a new line character (end of paragraph). The position in text of the first glyph of the first line in the linked list is firstGlyphPosition and the position of the last glyph in the linked is lastGlyphPosition.

# Because the lines are generated a paragraph at a time, the first glyph position and last glyph position will usually be outside the screen. Within the range (firstGlyphPosition .. lastGlyphPosition) there will be a range defined by (firstScreenPosition .. lastScreenPosition) that delimits the glyphs that are on the screen. 

# - firstGlyphPosition <= firstScreenPosition <= lastScreenPosition <= lastGlyphPosition

# After the lines are generated, and firstScreenPosition is valid, the method:

# - TextViewer.calcVisibleLineInfo() 

# can calculate the lastScreenPosition and lineYPositions correctly.

# --- --- ---
# Mapping the glyphs to the actual display screen
# --- --- ---

# The TextViewer.calcVisibleLineInfo() method will produce a Python map data structure TextViewer.lineYPosition which can be used to correctly calculate the rectangle dimensions of the rectangle that is covered by any glyph that is on the screen.

# --- --- ---
# Constraints on the Text Viewer's data
# --- --- ---

# The firstGlyphPosition and firstScreenPosition will always map to the 0th glyphs on their lines. lastScreenPosition and lastGlyphPosition will always map to the last glyphs on their lines. 

# Any change to the set of glyphs must keep the values of firstGlyphPosition, firstScreenPosition, lastScreenPosition, and lastGlyphPosition in synch with the text contents. Furthermore, the following conditions must be true on after any modification to the glyphs.

# - (firstGlyphPosition - 1) indexes a new line character.
# - topLine references a valid line and is not None.
# - the firstScreenPosition maps to the glyph at offset 0 on the topLine
# - the lastScreenPosition is adjusted properly with a call to calcVisibleLineInfo if the firstScreenPosition has been modified.
# - lastGlyphPosition indexes a new line character unless it indexes the last character of the document.

# If the conditions for the firstGlyphPosition and lastGlyphPosition are not true (e.g., the new line character preceding the firstGlyphPosition is deleted) regenerateTextAroundCursor() must be called to refresh the set of glyphs.

# --- --- ---
# Mapping Functions between glyphs and text position and screen position
# --- --- ---

# If the text positions mapping to the first and last glyph and first and last screen characters are correct, the there are methods can be used to calculate the line,offset of a text position if it is within the range (firstGlyphPosition..lastGlyphPosition). Other methods can map the other direction and find the text position of a valid line,offset value.

# - TextViewer.textPosToLinePos( self, textPos)
# Return the line, offset that corresponds to the textPos if the textPos is within (firstGlyphPosition..lastGlyphPosition). Returns None, -1 if the textPos is outside the range of glyphs.

# - TextViewer.movePos (self, line, linePos, delta)
# Returns a (line, offset) that represents a move of delta from the glyph referenced by (line, linePos). delta < 0 indicates a move backwards and 0 < delta indicated a move forward.

# -TextViewer.linePosToTextPos( self, line, offset)
# Returns the text position of (line,offset).

# -TextViewer.TextPosToScreenLinePos(self, textPos)
# If the textPos is within the bounds [firstScreenPosition..lastScreenPosition], return the (line,offset). The line will have an entry in the Python map data type lineYPositions and together with the widths of the glyphs, the rectangle position of a glyph on the screen can be calculated.

# --- --- ---
# onAddText and onDelText and rewrapping of the lines
# --- --- ---

# The contents of the set of glyphs can be changed to match additions and deletions in the documents that the TextViewer observes. Adding and deleting text also affects the word wrapping and therefore reorganizes the new set of glyphs into new sets of lines.

# The firstGlyphPosition, firstScreenPosition, lastScreenPosition and lastGlyphPosition indexes must be kept synchronized with the changes. Certain changes, such as deleting the newline character that precedes the firstGlyphPosition, can require a call to regenerateTextAroundCursor to refresh the glyphs from scratch. At the time onAddText and onDelText are called, the cursor position is not stable so the onAddText and onDelText return with calls to._clearContent(). This will clear the glyphs. When the screen is redrawn (in the current design, this will be after the new cursor position is set) the lack of glyphs will trigger a call to regenerateTextAroundCursor().

# --- --- ---
# Class TextViewer Implementation
# --- --- ---

class TextViewer:

# Define methods that initialize the TextViewer.

  def __init__(self, documentText, surface, isTransparent = 1):
    self._convert_document_and_page_characters = 0
    self.show_cursor = 1
    self._cursor_changed = 1
    self.document = documentText
    self.document.addObserver(self)
    self._isTransparent = isTransparent

    self.documentCharacterGlyph = glyph.DocumentCharacterGlyph()
    self.pageCharacterGlyph = glyph.PageCharacterGlyph()

    self.setSurfaces(surface)
    self.initializeContent()
    self._needs_redraw=1
  #end __init__

  def initializeContent(self):
    self._clearContent()
    initialTextLength = self.document.getLength()

    self.onAddText(0,initialTextLength)
    #print "initializeContent: with initialTextLength=", initialTextLength
  # end initializeContent

# The TextViewer._clearContent method resets the linked list of lines and other structures.

  def _clearContent(self):
    # Manage the lines of glyphs.
    self.startLine = line.Line(self)
    self.firstGlyphPosition = -1
    self.lastGlyphPosition = -1

    # Manage the screen.
    self.topLine = self.startLine
    self.firstScreenPosition = -1
    self.lastScreenPosition = -1
    self.lineYPositions = {}
  # end _clearContent

  def setSurfaces(self,drawingSurface):
    self.surface = drawingSurface
    glyphWidth = self.surface.getWidth() - 1
    self.documentCharacterGlyph.setWidth(glyphWidth)
    self.pageCharacterGlyph.setWidth(glyphWidth)
    self.surface.clear()
  # end setSurfaces

# TextViewer: Check the validity of variables used to manage the linked list of lines and glyphs.

# --- (firstGlyphPosition - 1) indexes a new line character.

  def isFirstGlyphPositionValid(self):

    if self.firstGlyphPosition < 0:
      return False

    if self.firstGlyphPosition == 0:
      return True

    if self.firstGlyphPosition > 0:
      pass
      d = self.document
      if d.getChar(self.firstGlyphPosition-1) <> "\n":
        return False
    #end if
    return True
  #end isFirstGlyphPositionValid

# --- topLine references a valid line and is not None.
# --- The firstScreenPosition maps to the glyph at offset 0 on the topLine

# Assume that firstGlyphPosition is correct. Find the line,offset of the firstScreenPosition. If the offset is not 0, adjust it. Reset the topline and 

  def recalibrateFirstScreenPosition(self):

    fsp = self.firstScreenPosition
    if fsp < 0:
      # _clearContent() was called
      return -1
    #end if

    self.topLine, offset = self.textPosToLinePos(fsp)

    if self.topLine is None:
      # this should never occur but just in case..
      self._clearContent()
      return -1

    if offset > 0:
      self.firstScreenPosition = fsp - offset

    return offset
  # end recalibrateFirstScreenPosition

# - lastGlyphPosition indexes a new line character or the last character in Humane Document.

  def isLastGlyphPositionValid(self):

    if self.lastGlyphPosition < 0:
      return False

    d = self.document
    docLength = d.getLength()

    if self.lastGlyphPosition == docLength-1:
      return True

    if d.getChar(self.lastGlyphPosition) == "\n":
      return True
    else:
      return False
    # end if

  #end islastGlyphPositionValid

# --- --- ---
# --- --- ---
# TextViewer: Mapping between text position and (line, pos)

# --- --- ---
# TextViewer.movePosition.

# From a position in the text defined by [current line, position within current line], find the new position [line, position] such that the new position represents a move of N positions.

# If N > 0, the move is forward.
# If N < 0, the move is backward.

# movePosition returns the last [line, position] if the move results in a position outside the set of existing lines. Therefore, moves to outside the set of glyphs contained in the TextViewer (e.g., a Leap operation that places the cursor far away) must do their own bounds checking and handling of such situations.

  def movePosition(self, currLine, posInLine, N):
    if N == 0: 
      return currLine, posInLine

    if N > 0:
      if currLine.getLength() - posInLine - N > 0:
        return currLine, posInLine + N
      if currLine.Next == None:
        return currLine, currLine.getLength() -1
      N -= currLine.getLength() - posInLine
      while N >= 0:
        currLine = currLine.Next
        N -= len(currLine._glyphs)
      return currLine, currLine.getLength() + N

    if N < 0:
      N *= -1
      if posInLine - N >= 0:
        return currLine, posInLine - N
      if currLine.Previous == None:
        return currLine, 0
      N -= posInLine
      while N > 0:
        currLine = currLine.Previous
        N -= len(currLine._glyphs)
      return currLine, -N

# --- --- ---
# TextViewer.textPosToLinePos.

# Obtain a [line, position] of a text position. Return [None,-1] if text position is outside the glyphs.
# This function requires correct values for the TextViewer.firstGlyphPosition and lastGlyphPosition

  def textPosToLinePos(self, textPos):
    #print "textpostolinepos: %d" % textPos
    #print "start, end: %d, %d" % (self.firstGlyphPosition, self.lastGlyphPosition)
    if self.firstGlyphPosition == -1:
      return None,-1

    if textPos < self.firstGlyphPosition or textPos > self.lastGlyphPosition:
      return None, -1
    line, posOnLine = self.movePosition(self.startLine, 0, textPos-self.firstGlyphPosition)
    return line, posOnLine
  # end textPosToLinePos

# --- --- ---
# TextViewer.findOffset( line, pos)

# Find the difference between the firstGlyphPosition and the position indexed by line, pos. It can be used to calculate the text position from the (line, pos), if the return value > 0.

  def findOffset(self, line, pos):
    pass
    if self.firstGlyphPosition == -1:
      return -1
    
    offset = 0
    currLine = self.startLine
    while currLine <> line:
      offset = offset + currLine.getLength()
      currLine = currLine.getNext()
    offset = offset + pos
    return offset
  #end findOffset

# --- --- ---
# TextViewer.isCharOnScreeen

# firstScreenPosition and lastScreenPosition must be set correctly.
# Make sure the text position is on the screen by checking firstScreenPos <= textPos <=lastScreenPos. 

  def isCharOnScreen(self, position):
    return self.firstScreenPosition <= position and position <= self.lastScreenPosition

# --- --- ---
# TextViewer.textPosToScreenLocation( textPos )

# Requires correct settings for firstScreenPos and lastScreenPos. Obtain the line,pos of a glyph on the screen from a text position. We also use the firstScreenPosition (topLine,0) to start the search so it saves time compared to getting the line,Pos from the firstGlyphPosition at startLine, 0.

  def textPosToScreenLocation(self, textPos):
    #print "textpostolinepos: %d" % textPos
    #print "start, end: %d, %d" % (self.firstScreenPosition, self.firstScreenPosition)

    if self.firstScreenPosition == -1 or self.lastScreenPosition == -1:
      return None,-1

    if not self.isCharOnScreen(textPos):
      return None,-1

    line, posOnLine = self.movePosition(self.topLine, 0, textPos-self.firstScreenPosition)
    return line, posOnLine
  # end textPosToScreenLocation

# --- --- ---
# --- --- ---
# TextViewer: Create and manage the linked list of lines.

# TextViewer.regenerateTextAroundCursor will create a linked list of lines and correctly set the firstGlyphPosition, firstScreenPosition, lastScreenPosition, and lastGlyphPosition. It should be called after the cursor in the document is set to a valid position. The display of the document will be ready for drawing at this point.

# TextViewer.onAddText and .onDelText do not require the cursor to be set at its final position. These methods will try to add or delete the glyphs that map to the characters that have been added or deleted in the self.document. Word wrapping will be performed and the firstGlyphPosition, firstScreenPosition, lastScreenPosition, and lastGlyphPosition will be adjusted properly. If the deletion invalidates the any of these 4 positions, the contents will be cleared using ._clearContent(). 

# When ._clearContent() is called, the next redraw of the screen will call regenerateTextAroundCursor() which will create a fresh display with a correct set of glyphs and correct settings for firstGlyphPosition, firstScreenPosition, lastScreenPosition, and lastGlyphPosition.

# --- --- ---
# TextViewer.regenerateTextAroundCursor

  def regenerateTextAroundCursor(self, cursorPosInText):

    self._clearContent()

    #Backtrack to the last newline.

    maxHeight = self.surface.getHeight()
    tA = self.document.textArray
    lineBreakBeforeCursor = tA.raw_rfind('\n', 0, cursorPosInText)
    lineBreakAfterCursor = tA.raw_find('\n', cursorPosInText)
    if lineBreakAfterCursor == -1:
      lineBreakAfterCursor = tA.getLength()-1
    #print "range: %d to %d" % (lineBreakBeforeCursor, lineBreakAfterCursor)
    #print "text: %s" % str([contents[lineBreakBeforeCursor:lineBreakAfterCursor]])

# Note if a new line was not found before the cursor, lineBreakBeforeCursor == -1 and the value of lineBreakBeforeCursor+1 == 0. Therefore the value of firstGlyphPosition will be correctly set to 0 (first character of humane document) if a new line can not be found before the cursor. See also _generatePreviousLines() for similar usage of the "not found" return value of -1.

    glyphsToAdd = self.generateGlyphList(lineBreakBeforeCursor+1, lineBreakAfterCursor-lineBreakBeforeCursor)
    self.addGlyphsWordwrap(glyphsToAdd, self.startLine)

    self.firstGlyphPosition = lineBreakBeforeCursor+1
    self.lastGlyphPosition = lineBreakAfterCursor

    self.cursorLine, self.cursorPosOnLine = self.textPosToLinePos(cursorPosInText)

    self.topLine = self.cursorLine
    self.firstScreenPosition = cursorPosInText - self.cursorPosOnLine
    distanceFromTop = self.topLine.getHeight()

    while distanceFromTop < (maxHeight/2):
      if self.topLine.getPrevious() == None:
        if not self._generatePreviousLines():
          break
      self._moveTopLineUp()
      distanceFromTop += self.topLine.getHeight()

    # now add all text after the cursor position

    maxDistanceFromBottom = maxHeight - distanceFromTop
    bottomLine = self.cursorLine
    distanceFromBottom = bottomLine.getHeight()
    while distanceFromBottom < maxDistanceFromBottom:
      if bottomLine.getNext() == None:
        if not self._generateNextLines(bottomLine):
          break
      bottomLine = bottomLine.getNext()
      distanceFromBottom += bottomLine.getHeight()

# If we reached the bottom of the document, then there will be useless white space at the bottom; let's see if we can print more of the lines above the cursor to fill that space.

    if distanceFromBottom < maxDistanceFromBottom:
      totalHeight = distanceFromTop + distanceFromBottom
      #print "distfrom bottom: %d   distfromtop: %d   total: %d  maxheight: %d" % (distanceFromBottom, distanceFromTop, totalHeight, maxHeight)
      while totalHeight < maxHeight:
        if self.topLine.getPrevious() == None:
          if not self._generatePreviousLines():
            break
        self._moveTopLineUp()
        totalHeight += self.topLine.getHeight()

# At this point the firstGlyphPosition, firstScreenPosition, and lastGlyphPosition have been set properly. The call to calcVisibleLineInfo will set the lastScreenPosition correctly and fill the lineYPositions map.

    height = self.calcVisibleLineInfo()
    self._needs_redraw = 1
  #end regenerateTextAroundCursor

# --- --- ---
# TextViewer._generateNextLines

# Add a paragraph of lines to the linked list of lines at tail. Adjust the lastGlyphPosition.

  def _generateNextLines(self, bottomLine):
    tA = self.document.textArray
    if self.lastGlyphPosition == tA.getLength()-1:
      return 0
    lineBreakAfterEnd = tA.raw_find('\n', self.lastGlyphPosition+1)

    if lineBreakAfterEnd == -1:
      # There is no new line beyond last Glyph Position. 
      # Just set to the last character position of the humane document
      lineBreakAfterEnd = tA.getLength()-1

    strLen = lineBreakAfterEnd - self.lastGlyphPosition
    glyphsToAdd = self.generateGlyphList(self.lastGlyphPosition+1, strLen)
    bottomLine.insertNewLineAfter()
    bottomLine = bottomLine.Next
    self.addGlyphsWordwrap(glyphsToAdd, bottomLine)
    self.lastGlyphPosition += strLen
    return 1
  #end _generateNextLines

# --- --- ---
# TextViewer._generatePreviousLines

# Add a single paragraph of lines to the linked list of lines at head. Adjust the firstGlyphPosition.


  def _generatePreviousLines(self):
    if self.firstGlyphPosition == 0:
      return 0
    tA = self.document.textArray

    # note that the slice notation for rfind will search for a line break
    # in 0..self.firstGlyphPosition-2. The line break on firstGlyphPosition - 1 will
    # not be in the search range.
    #
    lineBreakBeforeStart = tA.raw_rfind('\n', 0, self.firstGlyphPosition-1)

# Note if a new line was not found before the firstGlyphPosition, lineBreakBeforeStart == -1 and the value of lineBreakBeforeStart+1 == 0 . Therefore the value of firstGlyphPosition will be correctly set to 0 (first character of humane document) if a paragraph break can not be found before the cursor. See also regenerateTextAroundCursor().

    strLen = self.firstGlyphPosition-1 - lineBreakBeforeStart
    glyphsToAdd = self.generateGlyphList(lineBreakBeforeStart+1, strLen)
    self.startLine.insertNewLineBefore()
    self.startLine = self.startLine.Previous
    #print "glyphs to add: %s" % get_glyph_str(glyphsToAdd)
    self.addGlyphsWordwrap(glyphsToAdd, self.startLine)
    self.firstGlyphPosition -= strLen
    return 1
  # end _generatePreviousLines

# --- --- ---
# TextViewer.calcVisibleLineInfo

# Requires that the firstScreenPosition is set correctly.
# lastScreenPosition and lineYPositions are correctly calculated.

  def calcVisibleLineInfo(self):
    to_render = self.topLine
    curr_char = self.firstScreenPosition

    line_pos = 0
    self.lineYPositions[to_render] = line_pos
    self.visibleLines = [to_render]
    curr_char += to_render.getLength()
    next_line = to_render.Next
    next_pos = line_pos + to_render.getHeight()
    while next_line <> None and next_pos < self.surface.getHeight():
      line_pos = next_pos
      to_render = next_line
      self.lineYPositions[to_render] = line_pos
      self.visibleLines.append(to_render)
      curr_char += to_render.getLength()
      next_line = to_render.Next
      next_pos = line_pos + to_render.getHeight()

    curr_char -= 1
    self.lastScreenPosition = curr_char
    return next_pos
  # end calcVisibleLineInfo

# --- --- ---
# TextViewer.onAddText

# An observer method that is called whenever the TextViewer's target document has added text to itself.

  def onAddText(self, insertPos, length):

    fGP = self.firstGlyphPosition
    fSP = self.firstScreenPosition
    lSP = self.lastScreenPosition
    lGP = self.lastGlyphPosition

# If the insert position was behind the glyphs, there is no need to change anything. Note that lGP is a new line so newly inserted text after lGP will not affect the lGP due to the rewrapping.

    if lGP < insertPos:
      return

    import archy_globals

# NOTE:
# The firstGlyphPosition firstScreenPosition are updated differently on insert than other text positions. Other text positions index the same text and will get pushed back when the insertion position is equal to them. However, when new text is inserted on the firstGlyphPosition and firstScreenPosition, they keep their positions and index the newly inserted text. That is why firstGlyphPosition and firstScreenPosition get the updateTextPositionOnAdd called only when the insertPos < firstGlyphPosition or insertPos < firstScreenPosition respectively.

# lastScreenPosition and lastGlyphPosition behave like normal text positions.

# If the insertPos < firstGlyphPosition, there is no need to add glyphs and rewrap lines. Just update the text positions for glyphs and screen.

    if insertPos < fGP:
      self.firstGlyphPosition = archy_globals.updateTextPositionOnAdd(fGP,insertPos, length)
      self.firstScreenPosition = archy_globals.updateTextPositionOnAdd(fSP,insertPos, length)
      self.lastScreenPosition = archy_globals.updateTextPositionOnAdd(lSP,insertPos, length)
      self.lastGlyphPosition = archy_globals.updateTextPositionOnAdd(lGP,insertPos, length)
      return

# At this point we know that the fGP <= insertPos and insertPos <= lGP. Within this range, new glyphs will be added and the text will have to be rewrapped.

# This heuristic checks if the work on rewrapping will be more difficult than just redrawing the screen from scratch with regenerateTextAroundCursor. If there are more characters inserted that have to be wrapped than the current glyphs on the screen, we just clear the content and let regenerateTextAroundCursor handle all the adjustments later.

    if lSP - fSP + 1 < length:
      self._clearContent()
      return

# Find the line and position. Note that firstGlyphPosition is valid at this point since the insert point is behind it. The textPosToLinePos function will work correctly.

    line, posOnLine = self.textPosToLinePos(insertPos)
    glyphsToAdd = self.generateGlyphList(insertPos, length)

# We're done generating the new glyphs.  Before inserting them, we're going to see if we have a wrapped line (i.e., a line that doesn't end in CR) before the insertion point; if we do, we're going grab all of the glyphs on our current line and add them to the previous line.  This will allow us to deal with situations in which a space character was inserted near the beginning of a line, which breaks the first word of the line into two, allowing the first word to be wrapped up to the previous line.

# For the same reasons, we will also check to see if the previous line has a previous wrapping line, and do the same with it.  This will be for situations in which our insertion point is on a document character and a space character is inserted.

    if line.Previous != None and not line.Previous.endsInNewline():
      #print "LINE HAS PREVIOUS!"
      glyphsToAdd[0:0] = line._glyphs[0:posOnLine]
      glyphsToAdd.extend(line._glyphs[posOnLine:])
      line = line.Previous
      self.disposeOneLine(line.Next)
      if line.Previous != None and not line.Previous.endsInNewline():
        #print "LINE HAS PREVIOUS!"
        glyphsToAdd[0:0] = line._glyphs
        line = line.Previous
        self.disposeOneLine(line.Next)
    else:
      glyphsToAdd.extend(line._glyphs[posOnLine:])
      line._glyphs[posOnLine:] = []

# Now we call addGlyphsWordwrap to add the glyphs to the line.
    #print "onAddText: glyphs to add: %s   line: %s" % (get_glyph_str(glyphsToAdd), get_glyph_str(line._glyphs))
    self.addGlyphsWordwrap(glyphsToAdd, line)

# If the insertPos is before the start of the screen, rewrapping may cause a change in the start of screen.
# Check for it and adjust the fSP, lSP and lGP accordingly

    if fGP <= insertPos and insertPos < fSP:
      self.firstScreenPosition = archy_globals.updateTextPositionOnAdd(fSP,insertPos, length)
      fSP_offset = self.recalibrateFirstScreenPosition()
      if fSP_offset == 0:
        self.lastScreenPosition = archy_globals.updateTextPositionOnAdd(lSP,insertPos, length)
      else:
        height = self.calcVisibleLineInfo()
      self.lastGlyphPosition = archy_globals.updateTextPositionOnAdd(lGP,insertPos, length)

# Even if the insert position is behind the lSP, the rewrap can change the lSP, so do a calcVisibleLineInfo to make sure the lSP is updated for any other condition on the insert position.

    if fSP <= insertPos and insertPos <= lGP:
      height = self.calcVisibleLineInfo()
      self.lastGlyphPosition = archy_globals.updateTextPositionOnAdd(lGP,insertPos, length)

  # end onAddText

# --- --- ---
# TextViewer.onDelText

  def onDelText(self, delStart, delEnd):
    pass
    oldFGP = self.firstGlyphPosition
    oldFSP = self.firstScreenPosition
    oldLSP = self.lastScreenPosition
    oldLGP = self.lastGlyphPosition

# If the start of the deletion was behind the glyphs, there is no need to change anything. Note that lGP is a new line so deleted text after lGP will not affect the lGP due to the rewrapping.

    if oldLGP < delStart:
      return

    import archy_globals
# We need to obtain deletion line pos before we adjust any of the start positions.

    glyphDelStart,glyphDelEnd = archy_globals.intersection( [delStart,delEnd],[oldFGP, oldLGP] )
    if glyphDelStart <= glyphDelEnd:
      firstLine, posOnFirstLine = self.textPosToLinePos(glyphDelStart)
      lastLine, posOnLastLine = self.textPosToLinePos(glyphDelEnd)



    self.firstGlyphPosition = archy_globals.updateTextPositionOnDelete(oldFGP,delStart, delEnd)

    if not self.isFirstGlyphPositionValid():
      self._clearContent()
      return

    self.firstScreenPosition = archy_globals.updateTextPositionOnDelete(oldFSP,delStart, delEnd)
    #lastScreenPosition will be updated via calcVisibleLineInfo()
    self.lastGlyphPosition  = archy_globals.updateTextPositionOnDelete(oldLGP,delStart, delEnd)
    if not self.isLastGlyphPositionValid():
      self._clearContent()
      return

    if glyphDelEnd < glyphDelStart:
      # no glyphs will be deleted so we just need to update the lastScreenPos
      self.lastScreenPosition = archy_globals.updateTextPositionOnDelete(oldLSP,delStart, delEnd)
      return

# At this point we know that glyphs will be deleted. 

# We use a heuristic that checks if the glyphs that are deleted exceed half of the glyphs in the range [end of deletion..lastGlyphPosition]. If so, we do not bother to delete glyphs and rewrap, and instead just clear the content and return. That is because it is likely that there will not be enough glyphs to draw the screen and we will have to clear the content anyway.

    screenDelStart, screenDelEnd = archy_globals.intersection( [delStart,delEnd],[oldFSP, oldLGP] )

    if screenDelStart <= screenDelEnd:
      #deletion occurs on the screen
      numberOfGlyphsToDelete = screenDelEnd - screenDelStart + 1
      numberOfGlyphsBehindDelete = oldLGP - screenDelEnd
      if numberOfGlyphsBehindDelete < numberOfGlyphsToDelete * 2:
        self._clearContent()
        return

# Delete the glyphs and rewrap.

# First, we'll try to "mass delete" as much of our selection as possible.  We call this "mass deletion" because we are deleting lines of text without performing any other computations, such as word-wrap, which speeds things up.

# During the mass deletion, we will actually delete more of the selection than we need to, to speed things up; we will then quickly add back any deleted characters that weren't actually supposed to be deleted.

    firstLine._needs_recalc_glyph_metrics = 1
    firstLine._needs_redraw = 1

    if firstLine != lastLine:
      while firstLine.Next <> lastLine:
        firstLine.deleteNextLine()
      glyphsToAdd = firstLine._glyphs[0:posOnFirstLine]
      glyphsToAdd = lastLine._glyphs[posOnLastLine+1:]
      firstLine.deleteNextLine()
    else:
      #print "posOnFirstLine: %d  posOnLastLine: %d" % (posOnFirstLine, posOnLastLine)
      glyphsToAdd = firstLine._glyphs[posOnLastLine+1:]

    firstLine._glyphs[posOnFirstLine:] = []

# If we have a previous line that is word-wrapped (i.e., doesn't end in a CR), then we will delete our entire current line and add it to the end of the last line.  This is for situations in which the user deleted part of the first word on the line so that it can be wrapped up to the previous line.

# If the previous line itself has a previous word-wrapped line, then we will do the same thing for the previous line; this is for situations in which a single document character is deleted.

    if firstLine.Previous != None and not firstLine.Previous.endsInNewline():
      glyphsToAdd[0:0] = firstLine._glyphs
      theLine = firstLine.Previous
      self.disposeOneLine(theLine.Next)
      if theLine.Previous != None and not theLine.Previous.endsInNewline():
        glyphsToAdd[0:0] = theLine._glyphs
        theLine = theLine.Previous
        self.disposeOneLine(theLine.Next)
    else:
      theLine = firstLine

    #print "glyphs to add: %s" % get_glyph_str(glyphsToAdd)
    #print "TheLine: %s" % get_glyph_str(theLine._glyphs)
    self.addGlyphsWordwrap(glyphsToAdd, theLine)

# At this point, the glyphs are modified correctly and the firstGlyphPosition and lastGlyphPosition are valid. Because of the rewrapping, the firstScreenPosition may no longer be the 0th offset of the topLine. We need to recalibrate the firstScreenPosition and reset the lastScreenPosition.

    offset = self.recalibrateFirstScreenPosition()
    height = self.calcVisibleLineInfo()
    screenHeight = self.surface.getHeight()
    if height < screenHeight:
      # there were not enough lines in TextViewer to fill the screen.
      # clear the content so that regenerateTextAroundCursor can be called.
      self._clearContent()
  # end onDelText

# --- --- ---
# TextViewer.disposeOneLine

  def disposeOneLine( self, line):
    if line.Previous is None:
      self.startLine = line.Next
    else:
      line.Previous.Next = line.Next

    if line.Next is not None:
      line.Next.Previous = line.Previous
  # end disposeOneLine

# --- --- ---
# --- --- ---
# TextViewer: Wordwrap related methods

# --- --- ---
# TextViewer.generateGlyphList

  def generateGlyphList(self, posInText, length):
    length = min( length, self.document.getLength() - posInText )
    glyphsToAdd = [None] * length
    chars, styles = self.document.getStyledText(posInText, posInText+length-1)

    #print "generating glyphs (len %d) for: %s" % (length, str([chars]))
    glyphDict = glyph.globalGlyphPool.glyphDict
    convertDocAndPageChars = self._convert_document_and_page_characters

    for i in range(length):
      new_char = chars[i]
      new_style = styles[i]

# Based on the character being inserted, we will determine what kind of Glyph object to instantiate for displaying said character.

      if new_char == '`' and convertDocAndPageChars:
        new_glyph = self.documentCharacterGlyph
      elif new_char == '~' and convertDocAndPageChars:
        new_glyph = self.pageCharacterGlyph
      else:
        try:
          new_glyph = glyphDict[(new_char, new_style)]
        except:
          new_glyph = glyph.globalGlyphPool.makeGlyph(new_char, new_style)

      glyphsToAdd[i] = new_glyph

    return glyphsToAdd
  # end generateGlyphList(self, posInText, length):

# --- --- ---
# TextViewer.addGlyphsWordwrap

  def addGlyphsWordwrap(self, glyphs, theLine):
    if theLine is None:
      raise Exception("trying to add glyphs to null line")
    if len(theLine._glyphs) == 0 and len(glyphs) == 0:
      self.disposeOneLine( theLine )
      return
    
    max_width = self.surface.getWidth()

    width = 0
    curr_word_width = 0
    i = 0
    last_space = -1

# First, we will process through all the characters on the current line so we can figure out where the last word begins, and the width of the line.

    for g in theLine._glyphs:
      width += g.width
      curr_word_width += g.width
      if g._char in [' ', '\t']:
        last_space = i
        curr_word_width = 0
      i += 1

# Now we will add each glyph to the line, creating new lines if necessary and performing word-wrap.

    for g in glyphs:
      if width + g.width > max_width:
        theLine.insertNewLineAfter()
        chars_after_space = i - 1 - last_space

# Here we wrap our current word to the next line, if possible.

        if last_space != -1 and chars_after_space > 0:
          theLine.passToNext(chars_after_space)
          width = curr_word_width

# The following conditional is for when the glyph being added would make the word we just wrapped longer than the *next* line--this is typically the case with document characters.

          if width + g.width > max_width:
            theLine = theLine.Next
            theLine.insertNewLineAfter()
            width = 0
        else:
          width = 0
        i = 0
        curr_word_width = width
        last_space = -1
        theLine._needs_recalc_glyph_metrics = 1
        theLine._needs_redraw = 1
        theLine = theLine.Next

      width += g.width
      curr_word_width += g.width
      theLine._glyphs.append(g)

      if g._char in [' ', '\t']:
        last_space = i
        curr_word_width = 0
      elif g._char == '\n':
        theLine.insertNewLineAfter()
        theLine._needs_recalc_glyph_metrics = 1
        theLine._needs_redraw = 1
        theLine = theLine.Next
        width = 0
        curr_word_width = 0
        last_space = -1
        i = -1
      i += 1

    #print "glyphswordwrap: theLine is now: %s" % get_glyph_str(theLine._glyphs)
    #if theLine.Previous:
    # print "  theLine.Previous is: %s" % get_glyph_str(theLine.Previous._glyphs)
    #if theLine.Next:
    # print "  theLine.Next is: %s" % get_glyph_str(theLine.Next._glyphs)

# We're done inserting the new characters.  If the last glyph we added was not a newline character, then we need to wrap the next line up to the current line.  Otherwise, due to the structure of the loop just executed, we have a completely blank line just after the newline character we just inserted; delete it and we're done.

    if g._char != '\n':
      theLine._needs_recalc_glyph_metrics = 1
      theLine._needs_redraw = 1
      theLine.wordWrap(max_width)
    else:
      theLine.Previous.deleteNextLine()
  #end of addGlyphsWordwrap

# --- --- ---
# --- --- ---
# TextViewer: Cursor related methods

# These methods read various information about the cursor and manipulate it.

# --- --- ---
# TextViewer.toggle_cursor_display

# Used to make the cursor blink.

  def toggle_cursor_display(self):
    self.show_cursor = (self.show_cursor == 0)
    self._needs_redraw = 1
  # end toggle_cursor_display

# --- --- ---
# TextViewer._refreshCursor

# _refreshCursor() realigns the cursorLine and cursorPosOnLine to be the same as the cursor Position of the text.

  def _refreshCursor(self):
    textCursorPos = self.document.getCursorPos()
    self.cursorLine, self.cursorPosOnLine = self.textPosToLinePos(textCursorPos)
    # both the cursorLine and the next line should be visible so that the bottom of the cursor is fully visible
    if self.cursorLine == None or not self.isCharOnScreen(textCursorPos):
      self.recenterOnCursor()
    elif self.cursorLine.Next is not None:
      nextLineChar = textCursorPos - self.cursorPosOnLine + self.cursorLine.getLength()
      if not self.isCharOnScreen(nextLineChar):
        self.recenterOnCursor()

# --- --- ---
# TextViewer.onCursorChange

  def onCursorChange(self):
    self._cursor_changed = 1
  #end onCursorChange

# --- --- ---
# TextViewer.recenterOnCursor

# Use brute force regenerateTextAroundCursor to put the cursor at the center of the display. There should be more sophisticated methods for cases were the glyphs are already available.

  def recenterOnCursor(self):
    self.regenerateTextAroundCursor(self.document.getCursorPos())
  # end recenterOnCursor

# --- --- ---
# --- --- ---
# TextViewer: Display related query methods.

# These methods read various information about the display.

  def isTransparent(self):
    return self._isTransparent
  # end isTransparent

  def getLineYPos(self, theLine):
    if self.lineYPositions.has_key(theLine):
      return self.lineYPositions[theLine]
    return 0
  # end getLineYPos

  def isChanged(self):
    return self.document.isChanged() or self._needs_redraw

# --- --- ---
# --- --- ---
# TextViewer: render() supporting methods

# --- --- ---
# TextViewer.render()

# Public method for redisplay. There should be either a set of lines and valid firstGlyphPosition..lastGlyphPosition values or the display should be clear.

  def render(self, background=None):
    self.document.clearChanged()
    if self._isTransparent:
      self.surface.clear()

    if self.firstGlyphPosition == -1:
      textCursorPos = self.document.getCursorPos()
      self.regenerateTextAroundCursor(textCursorPos)
      self._cursor_changed = 0

    if self._cursor_changed:
      self._refreshCursor()
      self._cursor_changed = 0

    if background:
      self.surface.blitRectangle(background, (0,0))
    self.doRender()
    self._needs_redraw = 0

# --- --- ---
  def doRender(self):
    """Template method for render()."""
    self.renderLines()
    self.renderCursor()
  #end render

# --- --- ---
  def renderLines(self):
    #print "redraw all the visible lines and white space symbols"
    for line in self.visibleLines:
      linePos = self.lineYPositions[line]
      self.surface.blitRectangle(line.render( self.surface.getWidth()), (line._margin,linePos))
    if not self._isTransparent and linePos+line._height < self.surface.getHeight():
      # Clear the part of the display area below the lowest line.
      # TODO: background color shouldn't be hardcoded...
      self.surface.fillRectangle((0, linePos+line._height, self.surface.getWidth(), self.surface.getHeight()), (255,255,255))

    if archyState.whitespaceVisible:
      for line in self.visibleLines:
        linePos = self.lineYPositions[line]
        line.drawWhitespaceSymbols(self.surface, linePos)
  #end renderLines

# --- --- ---
# TextViewer.renderCursor

  def renderCursor(self):
    if not self.isCharOnScreen(self.document.getCursorPos()):
      return
    yPos = self.getLineYPos(self.cursorLine)
    xPos = self.cursorLine.posToPixel(self.cursorPosOnLine)

    self.cursorLine.drawWhitespaceSymbols( self.surface, yPos, xPos, self.cursorPosOnLine, self.cursorPosOnLine )

    if self.show_cursor:
      width = self.cursorLine.getPosWidth(self.cursorPosOnLine)
      height = self.cursorLine.getHeight()
      self.surface.drawRectangle( [width, height], [xPos,yPos], [255,100,255], 100)

# --- --- ---
# --- --- ---
# TextViewer: View Memento related methods.

# --- --- ---
# TextViewer.getViewMemento

  def getViewMemento(self):
    m = [ self.startLine, self.topLine, self.firstGlyphPosition, self.firstScreenPosition, self.lastScreenPosition, self.lastGlyphPosition ]
    return m
  # end getViewMemento

# --- --- ---
  def setViewInformation(self, viewMemento):
    self.startLine = viewMemento[0]
    self.topLine = viewMemento[1]
    self.firstGlyphPosition = viewMemento[2]
    self.firstScreenPosition = viewMemento[3]
    self.lastScreenPosition = viewMemento[4]
    self.lastGlyphPosition = viewMemento[5]
    self.calcVisibleLineInfo()
    self._refreshCursor()
    self._needs_redraw = 1
  # end setViewInformation

# --- --- ---
# --- --- ---
# TextViewer: scroll related methods

# --- --- ---
  def _moveTopLineUp(self):
    self.topLine = self.topLine.getPrevious()
    self.firstScreenPosition -= self.topLine.getLength()

# --- --- ---
  def _moveTopLineDown(self):
    self.firstScreenPosition += self.topLine.getLength()
    self.topLine = self.topLine.getNext()

# --- --- ---
  def scrollUp(self):
    if not self.topLine.getPrevious():
      if not self._generatePreviousLines():
        return
    self._moveTopLineUp()
    self.calcVisibleLineInfo()
    self._needs_redraw=1
  # end scrollUp

# --- --- ---
  def scrollDown(self):
    maxHeight = self.topLine.getHeight()
    currHeight = 0

    bottomLine = self.visibleLines[-1]
    while currHeight < maxHeight:
      if not bottomLine.getNext():
        if not self._generateNextLines(bottomLine):
          return
      bottomLine = bottomLine.getNext()
      currHeight += bottomLine.getHeight()

    self._moveTopLineDown()
    self.calcVisibleLineInfo()
    self._needs_redraw=1
  # end scrollDown


#end TextViewer

# --- --- ---
# constants for indexing selection indicators and colors

PRESELECTION = 0
SELECTION = 1
OLD_SELECTION = 2
WHITE = [255,255,255]

# --- --- ---
# --- --- ---

# HumaneDocumentTextViewer class

# A TextViewer that always has a HumaneDocumentText as its document and maintains and draws selections as well as the cursor.

class HumaneDocumentTextViewer(TextViewer):
  def __init__(self, humaneDocumentText, surface):
    TextViewer.__init__(self, humaneDocumentText, surface, isTransparent=0)
    self._convert_document_and_page_characters = 1

    self.selectionColors = ( [254,243,100], [0,0xff,0xcc], [0x7f,0xff,0xe6], [0xbf,0xff,0xb3],[0xe1,0xff,0xf9] )

  def onClear(self):
    #print "HumaneDocumentTextViewer: onClear"
    self.initializeContent()

  def onSelectionsChanged(self):
    self._needs_redraw=1

# --- --- ---
# method HumaneDocumentTextViewer.renderLineSelection(line, firstOffset, lastOffset, color)

  def renderLineSelection(self, line, firstOffset, lastOffset, color):
    try:
      #print "start renderLineSelection"
      xPos = line.posToPixel(firstOffset)
      yPos = self.getLineYPos(line)
      width = line.getWidthOfRange( firstOffset, lastOffset)
      height = line.getHeight()
      line.drawWhitespaceSymbols( self.surface, yPos, xPos, firstOffset, lastOffset )
      self.surface.drawRectangle(  ( width,height), (xPos,yPos), color, 50)
      #print "finished renderLineSelection"
    except:
      #print "something wrong in renderLineSelection"
      #import sys
      #import traceback
      #traceback.print_exc(1000)
      raise

# --- --- ---

# Rendering the selections in HumaneDocumentTextViewer

# There are many ways to implement the renderSelections method. One way would be to iterate through all the visible lines, and for each line check if it is in a selection and render a rectangle. Another way would be to find the intersection of the visible lines and lines in a selection ahead of time and then to draw a rectangle for each line in the intersection.

# The second way is preferrable to the first if we imagine scaling the text editor to the ZUI. If we iterate through all the visible lines, that could involve iterating through an entire document if we are zoomed out to an "elevation" where the whole document is visible.

# The second way will only iterate through the lines that need to be rendered with the selection highlight.

# We will be using the second way.

# --- --- ---

# method renderSelectionIntersection(self, selNum, rangeStart, rangeEnd)

# Render the intersection of the selectionIndicator indexed by selNum and the viewport.

  def renderSelectionIntersection(self, selNum):
    import archy_globals
    try:
      selection = list(self.document.selections[selNum])
      on_screen_part = archy_globals.intersection(selection,[self.firstScreenPosition, self.lastScreenPosition])
      if on_screen_part[1] < on_screen_part[0]:
        # none of selection is on screen.
        return

      # now figure out what lines we need to draw selection highlights on.
      s0_offs = self.textPosToScreenLocation( on_screen_part[0] )
      s1_offs = self.textPosToScreenLocation( on_screen_part[1] )



      # now draw the selection highlight.
      color = self.selectionColors[selNum]

      curr_line = s0_offs[0]
      curr_offset = s0_offs[1]
      end_line = s1_offs[0]
      end_offset = s1_offs[1]

      while curr_line != end_line:
        last_char_of_line = curr_line.getLength() -1
        #draw the line rect
        self.renderLineSelection(curr_line, curr_offset, last_char_of_line, color)
        #update the currLine and currOffset
        curr_line = curr_line.Next
        if curr_line is not None:
          curr_offset=0

      # draw the last line. curr_line should == end_line
      self.renderLineSelection(curr_line, curr_offset, end_offset, color)
      #print "finished renderSelectionIntersection"
    except:
        #import sys
        #import traceback
        #traceback.print_exc(1000)
        raise

# --- --- ---
# method renderSelections

# Render the selections and their intersection with the visible lines on the screen.

  def renderSelections(self):
    #print "render selection humane text viewer"
    currVisibility = archyState.preselectionVisible

    if currVisibility:
      #print "render the preselection"
      self.renderSelectionIntersection(PRESELECTION)

    lastRenderableSelection = min(len(self.selectionColors), len(self.document.selections))
    #any_printed = False

    for i in range(SELECTION, lastRenderableSelection):
      selection = list(self.document.selections[i])
      #res = print_if_changed(i, selection)
      #if res:
        #any_printed = True
      self.renderSelectionIntersection(i)
    #if any_printed:
      #print "--- --- ---"
  # end renderSelections

  def doRender(self):
    self.renderLines()
    self.renderSelections()
    self.renderCursor()

# end class HumaneDocumentTextViewer


# --- --- ---
# --- --- ---

# Command Message Viewer implements a translucent surface with text

class CommandMessageViewer(TextViewer):
  def __init__(self, commandMessageText, screen, size):
    width, height = size
    surface = surfaces.PygameSurface( (width-20, height) )
    TextViewer.__init__(self, commandMessageText, surface, isTransparent=1)
    self.cursorPosOnLine = 0
    self.cursorLine = None

    # TODO: new code from MessageTextSurface starts here
    self.screen = screen
    self.topleft = (0,0)
    self.visible = 1
    self._needs_redraw = 0
    
  def setSurfaces(self, surface):
    TextViewer.setSurfaces(self, surface)
    width = surface.getWidth()
    self.surface.setAlpha( 85 )
    self.surface.setBackgroundColor( [255,255,254] )
    self.surface.setBackgroundToTransparent()

  def setBackgroundColor(self,color):
    self._backgroundColor = color

  def isChanged(self):
    return self.document.isChanged() or self._needs_redraw

  def setPosition(self, pos):
    self.topleft = pos

  def setVisibility(self, visible):
    self.visible = visible
    self._needs_redraw = 1

  def render(self):
    if self.visible:
      TextViewer.render(self)
    self.document.clearChanged()
    self._needs_redraw = 0

  def draw(self):
    if self.visible:
      self.screen.blitRectangle(self.surface, self.topleft)

  def onClear(self):
    self.initializeContent()

  def calcVisibleLineInfo(self):
    self._textHeight = 20
    height = TextViewer.calcVisibleLineInfo(self)
    self._textHeight += height
    return self._textHeight
  # end calcVisibleLineInfo


  def regenerateTextAroundCursor(self, cursorPosInText):
    self._clearContent()
    textLength = self.document.getLength()
    glyphsToAdd = self.generateGlyphList(0, textLength)
    self.addGlyphsWordwrap(glyphsToAdd, self.startLine)
    self.firstGlyphPosition = 0
    self.firstScreenPosition = 0
    self.lastScreenPosition = textLength - 1
    self.lastGlyphPosition = textLength - 1
    height = self.calcVisibleLineInfo()
    self.cursorLine, self.cursorPosOnLine = self.textPosToLinePos(cursorPosInText)

  def renderLines(self):
    TextViewer.renderLines(self)
    # draw borders
    w = self.surface.getWidth()
    h = self._textHeight
    black = (0,0,0)
    self.surface.drawLine( (0,0), (w,0), black)
    self.surface.drawLine( (0,0), (0,h), black)
    self.surface.drawLine( (w-1,0), (w-1,h), black)
    self.surface.drawLine( (0,h), (w,h), black)

  #end renderLines
  def renderCursor(self):
    pass
