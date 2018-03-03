# line.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: line.hpy,v 1.37 2005/02/06 12:17:14 bzwebcorp Exp $"

# --------------------------
# Module imports
# --------------------------

import glyph
import pygame
import drawing_surface
import surfaces

# --------------------------
# The Line Class
# --------------------------

# The Line class represents a physical line on the screen; it does not represent a paragraph of text, which has sometimes historically been referred to as a "line".

# The class maintains within it:

# - a list of glyphs
# - a margin (distance from left edge to start rendering).
# - a height (which is the maximum of the glyph heights).
# - a width (which is the pixel width of the line).
# - a length (which is the number of characters on the line).

class Line:

# '__init__' creates an empty Line, with a height and margin of 0, and the given
# TextViewer parent.

    def __init__(self, parent):
        self.parent = parent
        self._ascent = 0
        self._descent = 0
        self._lineHeight = 0 # use the get_linesize() method of a pygame Font
        self._height = 0
        self._margin = 0
        self._glyphs = []
        self.Previous = None
        self.Next = None
        self._needs_redraw = 1
        self._needs_recalc_glyph_metrics = 0
        self._surface = None
        self._height_changed = 1
        self._cached_screenWidth = None

# --------------------------
# Doubly-Linked List
# --------------------------

    def setNext(self, nextLine):
        self.Next = nextLine

    def getNext(self):
        return self.Next

    def setPrevious(self, previousLine):
        self.Previous = previousLine

    def getPrevious(self):
        return self.Previous


# 'insertNewLineAfter' inserts a new Line into the linked list, right after the current Line, and returns that new Line.

    def insertNewLineAfter(self):

# If there is no next Line, add a new one and if there is a next line, insert a new line between them:

        NewLine = Line(self.parent)
        NewLine.setPrevious(self)
        if self.Next <> None:
            NewLine.setNext(self.Next)
            self.Next.setPrevious(NewLine)
        self.setNext(NewLine)

        return self.Next


# 'insertNewLineBefore' inserts a new Line into the linked list, right before the current Line, and returns that new Line. If there is no previous Line, add a new one and if there is a previous line, insert a new line between them


    def insertNewLineBefore(self):

        newline = Line(self.parent)
        newline.setNext(self)
        if self.Previous != None:
            newline.setPrevious(self.Previous)
            self.Previous.setNext(newline)
        self.setPrevious(newline)

        return self.Previous
        
    def deleteNextLine(self):
        temp = self.Next
        self.setNext(self.Next.Next)
        if self.Next != None:
            self.Next.setPrevious(self)                 
        del temp

# --------------------------
# Linked List Passing Functions
# --------------------------

# 'passToNext' passes the final 'number' Glyphs to the start of the next line in the list.  If there is no next line, 'passToNext' creates a new line.  
# 'passToNext' returns whatever Line recieved the Glyphs.

    def passToNext(self, number):
        if self.Next == None:
            self.insertNewLineAfter()
            
        self.Next.addGlyphs(self._glyphs[-number:], 0)
        del self._glyphs[-number:]

        self._needs_recalc_glyph_metrics = 1
        self._needs_redraw = 1
        return self.Next

# 'passToPrevious' passes the first 'number' Glyphs to the end of the previous line in the list.    If there is no previous line, 'passToPrevious' creates one.
# 'passToPrevious' returns whatever Line recieved the Glyphs.

    def passToPrevious(self, number):
        if self.Previous == None:
            self.insertNewLineBefore()

        self.Previous.addGlyphs(self._glyphs[:number])
        del self._glyphs[:number]

        self._needs_recalc_glyph_metrics = 1
        self._needs_redraw = 1
        return self.Previous

# --------------------------
# Word Wrap handling functions
# --------------------------

    def dbg(self, txt):
        "Prints a debugging message to the console."

        print "line %d: %s" % (id(self), txt)

# The following function is a helper function for wordWrap() that takes the first i characters from the next line and passes them up to the current one, performing word-wrap on the next line or deleting the next line if it's empty.

    def __wordWrap_pushNextLineUp(self, i, screenWidth):
        #self.dbg("Bringing up text from next line NOW.")
        self.Next.passToPrevious(i)
        if self.Next.getLength() == 0:
            #self.dbg("Deleting next line b/c it's empty.")
            self.deleteNextLine()
            #self.dbg("Done deleting next line.")
        else:
            #self.dbg("Word-wrapping next line.")
            self.Next.wordWrap(screenWidth)
            #self.dbg("Done wrapping next.")

# The following word-wrap method word-wraps the current line and all following lines, until it is no longer possible to word wrap.

    def wordWrap(self, screenWidth):

        #debug_str = ""
        #for i in range(len(self._glyphs)):
        #   debug_str += self._glyphs[i]._char
        #self.dbg("wordWrap() called on line %s" % str([debug_str]))

        charPos = self._margin
        totalLength = 0

# The lastSpace variable keeps track of where the last space character is on the line, so that if we ever need to word wrap, we know where the word we want to wrap begins at.

        lastSpace = -1

        line_length = len(self._glyphs)
        
        for i in range(line_length):
            glyph = self._glyphs[i]
            totalLength += glyph.width

# Here, we check to see if the line is too long (i.e., its glyphs cannot physically fit on the screen).  If it is, we pass characters to the next line, wordwrap it, and exit.

            if totalLength >= screenWidth:
                if lastSpace == -1:
                    self.passToNext(line_length - i) 
                else:
                    self.passToNext(line_length - lastSpace - 1)
                #self.dbg("Line is too long, wrapping next now...")
                self.Next.wordWrap(screenWidth)
                #self.dbg("Done wrapping next.")
                return
            elif glyph._char in [" ", "\t"]:
                lastSpace = i
            elif glyph._char == "\n":

# Here we have determined that the line isn't too long, and the current character being added is a carriage return.  If the CR is the last character in the line, no word-wrapping needs to be done, so just exit.

                if i == line_length - 1:
                    #self.dbg("CR at end of line, I'm done!")
                    return

# Otherwise, we insert a new line, push the rest of this line to the next line, word-wrap the next line, and exit.

                #self.dbg("CR in middle of line, wrapping next.")
                self.insertNewLineAfter()
                self.passToNext(line_length - i - 1)
                self.Next.wordWrap(screenWidth)
                #self.dbg("Done wrapping next.")
                return

# At this point, we've determined that our line doesn't have a newline at the end, and it doesn't span the width of the text area.

# Here logic gets a little complex because what we do now depends on two things: whether our current line has whitespace (spaces or tabs, in this case) anywhere in it, and whether our current line's last character is a space or tab.

# If our current line has no whitespace, we can freely take as much from the next line as we can fit (we need not copy only full words).  We do not need to give anything to the next line.

# If our current line has whitespace in it, but does not end in a space or tab, then we have a "partial word" at the end of our line.  We can try taking the rest of the word (and possibly more words) from the next line, but if that fails, we need to give the "partial word" at the end of our line to the next line.

# If our current line does have a space/tab at the end of it, we can only take full words from the next line.  We do not need to give anything to the next line.

        if self.Next:

# The nextLineLastSpace variable keeps track of where the last space character is on the next line, so that if we need to bring up full words from the next line, we know where the words end at.

            nextLineLastSpace = -1

# We begin iterating through the characters of the next line, trying to figure out how many characters from the next line we can add to ours.

            for i in range(len(self.Next._glyphs)):
                glyph = self.Next._glyphs[i]
                totalLength += glyph.width

                if totalLength >= screenWidth:
                    #self.dbg("totalLength >= screenWidth, breaking out.")
                    i -= 1
                    break
                elif glyph._char == "\n":

# If the current character we're looking at is a carriage return, then we'll just copy the characters up to (and including) the carriage return and be done with it.

                    #self.dbg("CR on next line found, copying everything up to and including it to current line.")
                    self.__wordWrap_pushNextLineUp(i+1, screenWidth)
                    return
                elif glyph._char in [" ", "\t"]:
                    nextLineLastSpace = i

# We've figured out how much we can take from the next line, so now we have to make a decision.

            #self.dbg("i = %d    nextLineLastspace = %d" % (i, nextLineLastSpace))

            if self.endsInSpaceOrTab():

# The last character of our current line is a space or tab, so we'll try to bring up as many full words from the next line as we can.  If we can't pull up any full words, we're done with word wrapping, so return.

                if nextLineLastSpace != -1:
                    #self.dbg("Pulling up full word(s) from next line.")
                    self.__wordWrap_pushNextLineUp(nextLineLastSpace+1, screenWidth)
                    return
                else:
                    #self.dbg("Can't pull up full words from next line.")
                    return
            else:

# The last character of our current line is not a space or tab; if our current line has no whitespace anywhere in it, we need to fit as much of the next line in as we can, even if it's a partial word.

                if lastSpace == -1:
                    #self.dbg("Current line has no whitespace, last character is not whitespace.  Fitting as much of next line in as possible...")
                    if nextLineLastSpace != -1:
                        charIndex = nextLineLastSpace
                        #self.dbg("  pushing full word(s) (index %d)." % i)
                    else:
                        if i == -1:
                            return
                        else:
                            charIndex = i
                        #self.dbg("  pushing partial word(s) (index %d)." % i)
                    self.__wordWrap_pushNextLineUp(charIndex+1, screenWidth)
                    return
                else:

# Our current line has spaces/tabs in it, but not at the end of it, which means that we have a partial word at the end of our line.  We will see if we can pull the remainder of our partial word up from the next line; if not, we need to pass our partial word off to the next line.

                    if nextLineLastSpace != -1:
                        #self.dbg("Pulling rest of partial word up from next line.")
                        self.__wordWrap_pushNextLineUp(nextLineLastSpace+1, screenWidth)
                        return
                    else:
                        #self.dbg("Current line has whitespace in it, passing our partial word off to next line and wrapping it.")
                        self.passToNext(line_length - lastSpace - 1)
                        self.Next.wordWrap(screenWidth)
                        #self.dbg("Done wrapping next.")
                        return

# --- --- ---
# Interface to glyph list
# --- --- ---

# The following method adds the Glyph list 'glyphs', 'pos' characters into the line (0=first character), and updates the height of the line.

    def addGlyphs(self,glyphs,pos = -1):
        if pos == -1:
            pos = len(self._glyphs)
        self._glyphs[pos:pos] = glyphs
        self._needs_recalc_glyph_metrics = 1            
        self._needs_redraw = 1

    def changeHeight(self):
        #height = self._ascent - self._descent
        height = self._lineHeight
        if height <> self._height:
            self._height_changed = 1
        self._height = height

    def isBlank(self):
        # Return whether the given line consists only of a
        # carriage return.
        # TODO: This may not be entirely accurate.
        if self.getLength() == 1 or self.getLength() == 0:
            return 1
        else:
            return 0

    def endsInNewline(self):
        if len(self._glyphs) == 0:
            return 0
        else:
            return self._glyphs[-1]._char == "\n"

    def endsInSpaceOrTab(self):
        if len(self._glyphs) == 0:
            return 0
        else:
            return self._glyphs[-1]._char in [" ", "\t"]

    def calcGlyphMetrics(self):
        self._ascent = 0
        self._descent = 0
        self._lineHeight = 0
        for glyph in self._glyphs:
            self._ascent = max(self._ascent, glyph.ascent)
            self._descent = min(self._descent, glyph.descent)
            self._lineHeight = max(self._lineHeight, glyph.lineHeight)
        self.changeHeight()
        self._needs_recalc_glyph_metrics = 0
        #print "self._height=",self._height, "glyphHeight=",glyphHeight, "lineHeight=",glyphLineHeight
        

# 'removeGlyph' removes the glyph at 'pos' characters into the line, and updates the height of the line
    def removeGlyph(self,pos):
        del(self._glyphs[pos])
        self._needs_recalc_glyph_metrics = 1
        self._needs_redraw = 1

    def getLength(self):
        return len(self._glyphs)

    def getWidthOfRange( self, startPos, endPos ):
        pass
        width = 0
        for i in range (startPos, endPos+1):
            if 0<= i and i < self.getLength():
                width = width + self._glyphs[i].width
        return width
    # end getWidthOfRange

    def posToPixel(self, pos):
        pixelPos = self._margin
        if pos > len(self._glyphs):
            print "Error, pos is",pos,"but there are only",len(self._glyphs),"characters on line."
        for i in range(pos):
            pixelPos += self._glyphs[i].width
        return pixelPos

    def getPosWidth(self, pos):
        if pos >= len(self._glyphs):
            return 10
        return self._glyphs[pos].width

    def getHeight(self):
        if self._needs_recalc_glyph_metrics:
            self.calcGlyphMetrics()
        return self._height

    def makeSurface(self, screenWidth):
        if self._cached_screenWidth != screenWidth or self._height_changed:
            self._surface = surfaces.PygameSurface( (screenWidth, self._height) )
            self._height_changed = 0
            self._cached_screenWidth = screenWidth
            #print "bustin' a new surface. %d" % id(self._surface)
            if self.parent.isTransparent():
                self._surface.setBackgroundToTransparent()
        # TODO: Maybe we can optimize out this clear() at some point.
        self._surface.clear()
        x = self._margin
        for glyph in self._glyphs:
            y = self._ascent - glyph.ascent
            self._surface.blitRectangle( glyph.render(), (x, y) )
            x += glyph.width

    def drawWhitespaceSymbols(self, surface, ypos, xpos=None, firstChar = 0, lastChar = None):
        if xpos == None:
            xpos = self._margin

        if lastChar != None:
            glyphs = self._glyphs[firstChar:lastChar+1]
        else:
            glyphs = self._glyphs[firstChar:]

        x = xpos
        base_y = ypos + self._ascent

        for glyph in glyphs:
            if glyph.isWhitespace:
                y = base_y - glyph.ascent
                surface.blitRectangle( glyph.renderWhitespaceSymbol(), (x, y) )
            x += glyph.width

    def render(self, screenWidth):
        if self._needs_recalc_glyph_metrics:
            self.calcGlyphMetrics()
        if self._needs_redraw or self._cached_screenWidth != screenWidth:
            self._needs_redraw = 0
            self.makeSurface(screenWidth)
        return self._surface
