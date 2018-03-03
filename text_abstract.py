# text_abstract.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: text_abstract.hpy,v 1.51 2005/04/04 04:04:53 andrewwwilson Exp $"

# These imports are for their structures.   
import text_array
import behavior
import style

from archy_state import archyState

import archy_globals
import copy

# --------------------------
# Abstract Text class
# --------------------------

class Text:
    def __init__(self):
        self.textArray = text_array.TextArray('')
        self.styleArray = style.StyleArray(self.textArray)
        self.behaviorArray = behavior.BehaviorArray(self.textArray)
        self._is_changed = 1
        self.observers = []

    def clear(self):
        self.textArray.clearText()
        self.styleArray.clear(self.textArray)
        self.onClear()
        self._is_changed = 1
        self._notifyClear()

    def onClear(self):
        pass
    
    def addObserver(self, observer):
        self.observers.append(observer)

    def clearChanged(self):
        self._is_changed = 0
        
    def isChanged(self):
        return self._is_changed

    def isValidPos(self, textPos):
        if textPos >= 0 and textPos <= self.textArray.getLength() -1:
            return 1
        else:
            return 0
    
    def getLength(self):
        return self.textArray.getLength()

    def getSize(self):
        raise Exception("don't call me!")
        return self.textViewer.surface.getSize()
    
    def getChar(self, pos):
        return self.textArray.getChar(pos)
    
    def getCharStyle(self,pos):
        return self.styleArray.getCharStyle(pos)

    def getDefaultStyle(self):
        return self.styleArray.getDefaultStyle()

    def getStyles(self):
        return self.styleArray.getStyles()

    def getStyledText(self, start, end):
        justText = self.textArray.getSubString(start, end)[:]
        justStyle = self.styleArray.getSubString(start, end)
        return justText, justStyle
    
    def _notifyClear(self):
        for o in self.observers:
            o.onClear()


    def _notifyAddText(self, insertPos, textLen):
        self._is_changed = 1
            
        for o in self.observers:
            o.onAddText(insertPos, textLen)

    def _notifyDelText(self, startPos, endPos):
        self._is_changed = 1

        for o in self.observers:
            o.onDelText(startPos, endPos)

    def _notifyStyleChange(self, startPos, endPos):
        self._notifyDelText(startPos, endPos)
        self._notifyAddText(startPos, endPos - startPos + 1)

# addText adds text and styles to the insert position.
# It will work with behaviors later.

    def addText(self, newText, startPos, theStyle=None, behaviorString=None):
        insertPos = startPos

        try:
            newText = unicode(newText)
        except:
            newText = unicode(newText, 'iso-8859-1')

        self.textArray.addText(newText,insertPos)
        self.styleArray.addText(newText,insertPos)
        self.behaviorArray.addText(newText,insertPos)

        if type(theStyle) == int:
            self.styleArray.setStyleInRange(theStyle, insertPos, insertPos+len(newText)-1)
        elif type(theStyle) == list:
            self.styleArray.replaceStyles(theStyle, insertPos)

        self._notifyAddText(insertPos, len(newText))
        self.onAddText(newText, startPos)

    def onAddText(self):
        pass

    def delText(self, startPos, endPos):
        self.textArray.delText(startPos, endPos)
        self.styleArray.delText(startPos, endPos)
        self.behaviorArray.delText(startPos, endPos)
        self._notifyDelText(startPos, endPos)
        self.onDelText(startPos, endPos)

    def onDelText(self, startPos, endPos):
        pass

    #This (like most of the other style setting functions) allows for the
    #style to be a single integer or a list of integers. The former sets
    #the entire range, from startPos to endPos, to the style indicated. The
    #latter starts at the starPos and continues through the style array assign
    #each character to its respective style in the list.
    def setStyle(self, theStyle, startPos, endPos = None):
        if   type(theStyle) == int:
            self.styleArray.setStyleInRange(theStyle, startPos, endPos)
        elif type(theStyle) == list:
            self.styleArray.replaceStyles(theStyle, startPos)
            endPos = startPos + len(theStyle)
        self._notifyStyleChange(startPos, endPos)

    def setStyleOverlay(self, overlay, startPos, endPos = None):
        if endPos == None: endPos = startPos
        for pos in range(startPos, endPos + 1):
            currentStyle = self.styleArray.getCharStyle(pos)
            newStyle = archyState.stylePool.mergeStyleWithOverlay(currentStyle, overlay)
            self.styleArray.setCharStyle(pos, newStyle)
        self._notifyStyleChange(startPos, endPos)

# --------------------------
# The CursorText class
# --------------------------

# This is a class based on the Text class, which additionally keeps a cursor that serves as a text insert position.

class CursorText(Text):
    def __init__(self):
        Text.__init__(self)
        self.cursorPosInText = 0

    def onClear(self):
        self.setCursor(0)
        
    def getCursorPos(self):
        return self.cursorPosInText

    def onAddText(self, newText, startPos):
        # update cursor
        import archy_globals
        insertPos = startPos
        cursor = self.getCursorPos()
        newCursor = archy_globals.updateTextPositionOnAdd(cursor, insertPos, len(newText))
        self.setCursor(newCursor)
        # print "class %s added text at %d:\n%s\n" % (self.__class__.__name__, startPos, str([newText]))

    def onDelText(self, startDel, endDel):
        # update cursor
        import archy_globals
        cursor = self.getCursorPos()
        newCursor = archy_globals.updateTextPositionOnDelete(cursor, startDel, endDel)
        self.setCursor(newCursor)

    def addTextAtCursor(self, newText):
        self.addText(newText, self.cursorPosInText)
        
    def delTextAtCursor(self, length):
        self.moveCursor(-length)
        self.delText(self.cursorPosInText, self.cursorPosInText + length - 1)

# Two cursor movement methods:

# moveCursor is a relative move of the cursor from the
# current cursor position. setCursor which assigns a
# new position to the cursor.

    def setCursor(self, newPos):
        if newPos <= 0:
            self.cursorPosInText = 0
        elif newPos >= self.textArray.getLength()-1: 
            self.cursorPosInText = self.textArray.getLength()-1
        else:
            self.cursorPosInText = newPos

        for o in self.observers:
            o.onCursorChange()
        
        self._is_changed = 1

    def moveCursor(self, offset):
        #print "CursorText.moveCursor", offset
        newPos = self.cursorPosInText + offset
        self.setCursor(newPos)
#end class CursorText


# --------------------------
# The HumaneDocumentText class
# --------------------------

# This is a cursor text class with a preselection anchor, and selections.  An instance of this class is used for the main text document of Archy.

class HumaneDocumentText(CursorText):
    def __init__(self):
        CursorText.__init__(self)
        self.initializeTextPositions()

    def initializeTextPositions(self):
        self.selections = [ [-1,-1],[-1,-1],[-1,-1],[-1,-1]]
        self.selectionNames = ['preselection', 'selection', 'old selection', 'first old selection']
        self.passwordList = {}
        self.settingList = {}

    def onClear(self):
        CursorText.onClear(self)
        self.initializeTextPositions()


# The following method is used to save the selections so that the values
# can be restored.  It is important to use a deepcopy instead of just
# assigning the HumaneDocumentText.selections because of the semantics
# of Python objects.

    def copySelectionList(self):
        return copy.deepcopy(self.selections)

# We originally checked whether the length of the passed in selection list was the same length as the current selection list. If they were not equally we would raise an error. This did not yield the correct behavior. For instance, if a saved state of the system as n old selections then when that state is loaded the passed-in selection list will have n more elements than the internal selection list. The desired behavior is to have the n old selections. This function call does not need to care about comparing the new and current selection list lengths.
    def setSelectionList(self, list):
        list = copy.deepcopy(list)
        self.selections = list
        self._on_selections_changed()

# Modify the selections, and anchor upon the deletion of text.

    def onDelText(self, startDel, endDel):

        import archy_globals
        CursorText.onDelText(self, startDel, endDel)

        # update selections
        changed = False
        for i in range(len(self.selections)):
            start, end = self.selections[i]
            newStart = archy_globals.updateTextPositionOnDelete(start, startDel, endDel)
            newEnd = archy_globals.updateTextPositionOnDelete(end, startDel, endDel)
            if newStart <> start or newEnd <> end:
                self.selections[i] = [newStart, newEnd]
                changed = True

        if changed:
            self._on_selections_changed()

    def onAddText(self, newText, startPos):
# Modify the selections, and anchor on an insertion of text.

        import archy_globals
        CursorText.onAddText(self, newText, startPos)
        
        insertPos = startPos
        length = len(newText)
        
        # update selections
        changed = False
        for i in range(len(self.selections)):
            start, end = self.selections[i]
            newStart = archy_globals.updateTextPositionOnAdd(start, insertPos, length)
            newEnd = archy_globals.updateTextPositionOnAdd(end, insertPos, length)
            if newStart <> start or newEnd <> end:
                self.selections[i] = [newStart, newEnd]
                changed = True

        if changed:
            self._on_selections_changed()
        
    # end onAddText

    def selectionNameToNumber(self, name):
        if type(name) == int:
            return name
        elif name in self.selectionNames:
            return self.selectionNames.index(name) 
        else:
            raise name + " is not a valid selection name"

    def _on_selections_changed(self):
        self._is_changed = 1
        for o in self.observers:
            o.onSelectionsChanged()

# TODO: setSelection and getSelection should be symmetric. If we do not allow selections to be set to (-1,-1), we should not be range checking from 0..textLength. Need to clarify the logic and make it consistent.

    def setSelection(self,sel, startPos,endPos = -1):
        if endPos == -1:
            endPos = startPos
            
        if (startPos < 0) or (endPos > self.textArray.getLength() - 1):
            return
        if (endPos < 0) or (startPos > self.textArray.getLength() - 1):
            return
        startPos, endPos = min(startPos, endPos), max(startPos, endPos)
        self.selections[self.selectionNameToNumber(sel)] = [startPos, endPos]
        self._on_selections_changed()
        
    def getSelection(self, sel):
        return self.selections[self.selectionNameToNumber(sel)]

# createNewSelection is the function that should be used to set a new value for
# the main selection, and update the old selection lists.

    def createNewSelection(self,startPos,endPos):
        lastPos = self.getLength()-1
        startPos = archy_globals.bound(startPos, 0, lastPos)
        endPos = archy_globals.bound(endPos, 0, lastPos)
        startPos, endPos = min(startPos, endPos), max(startPos, endPos)
        #print "in createNewSelection: selection startPos, endPos=", startPos, endPos
        if self.isExtendedSelection():
            #print "in createNewSelection: after INSERT: ", self.selections
            self.selections.insert(1,[startPos, endPos])
        else:
            self.setSelection("selection",startPos, endPos)
            #print "in createNewSelection: after set: ", self.selections

# If this is a new extended selection, delete any old selections that overlap.


        if endPos - startPos + 1 > 1:
            self.removeOverlappingOldSelections(startPos,endPos)
    #end method createNewSelection

# The technique used to delete overlapping selections in the self.selections
# list:

# 1. collect all the indices to the overlapping old selections in indices_to_del.
# The first old selection starts at index 2(0=preselection, 1=selection 2=first old selection).
# 2. reverse the indices_to_del so that the higher indices appear first
# 3. loop through the indices_to_del, deleting the higher indices first.

    def removeOverlappingOldSelections(self, start, end):
        indices_to_del = []
        for i in range(2,len(self.selections)):
            selection = self.selections[i]
            if archy_globals.doRangesOverlap( selection, [start, end] ):
                indices_to_del.append(i)
        if len(indices_to_del)>0:
            indices_to_del.reverse()
            for i in indices_to_del:
                del self.selections[i]
        self._on_selections_changed()
    

    def isExtendedSelection(self):
        start, end = self.getSelection('selection')
        if end - start +1 > 1:
            return True
        else:
            return False

    def selectionExists(self, sel):
        try:
            s = self.selections[self.selectionNameToNumber(sel)]
            if s == [-1,-1]:
                raise
        except:
            return 0

        return 1

    def getNonContentMemento(self):
        memento = [self.cursorPosInText, self.copySelectionList()]
        return memento

    def setNonContentInformation(self, nonContentMemento):
        self.setCursor(nonContentMemento[0])
        self.setSelectionList(nonContentMemento[1])

class CommandMessageText(CursorText):
    pass
