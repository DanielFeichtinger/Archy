# cursor.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# Cursor Commands

# This module is intended to implement CREEP and LEAP as commands.  It has direct access to the main text modules, and sets selections directly.

import commands
from archy_state import archyState

# ============================================
# Abstract Creep Comand
# code common to Creep left and right
# ============================================

class AbstractCreepCommand(commands.CommandObject):
    def __init__(self):
        self._oldCursorPos, self._oldSelections = 0, []
        self._newCursorPos, self._newSelections = 0, []

    def recordable(self):
        return 1
        
    def saveSelectionInfo(self):
        self._oldCursorPos, self._oldSelections = archyState.mainText.getNonContentMemento()
                                    
    def collapseSelection(self, newCursorPos):
        return [newCursorPos, newCursorPos]

# ============================================
# Creep Left command
# ============================================

class CreepLeftCommand(AbstractCreepCommand):
    def name(self):
        return "CreepLeft"

    def dragPreselection(self, newCursorPos, preselection):
        if preselection[0] == self._oldCursorPos:
            newPreselection = [newCursorPos,preselection[1]]
        elif preselection[1] == self._oldCursorPos:
            newPreselection = [preselection[0],newCursorPos]
        elif preselection[1] == newCursorPos-1:
            newPreselection = [preselection[0],newCursorPos]
        else:
            newPreselection = [newCursorPos, newCursorPos]
        return newPreselection

    def execute(self):
        self.saveSelectionInfo()
        newSelections = []
# If the selection is the cursor selection:
        if self._oldSelections[1][0] == self._oldSelections[1][1]:
# - If the cursor is just to the right of the selection, collapse the cursor to the selection, do not change the selections, and move the appropriate preselection anchor:
            if self._oldCursorPos == (self._oldSelections[1][1]+1):
                newCursorPos = self._oldCursorPos-1
                newSelections.append( self.dragPreselection( newCursorPos, self._oldSelections[0] ) )
                newSelections.append( self.collapseSelection( newCursorPos ) )
# - If the cursor is on the selection and both are on the initial character, then don't change anything:
            elif (self._oldCursorPos == 0) and (self._oldSelections[1][0] == 0):
                newCursorPos = self._oldCursorPos
                newSelections.append(self._oldSelections[0])
                newSelections.append(self._oldSelections[1])
# - If the cursor is on the selection, then move cursor, selection, and the appropriate preselection anchor one character left, and copy the old selections:
            elif self._oldCursorPos == self._oldSelections[1][0]:
                newCursorPos = self._oldCursorPos-1
                newSelections.append( self.dragPreselection(newCursorPos, self._oldSelections[0]) )
                newSelections.append( self.collapseSelection(newCursorPos) )
            else:
                newCursorPos = self._oldCursorPos
                newSelections = [ [newCursorPos, newCursorPos], [newCursorPos, newCursorPos] ]
# If the selection is extended:
        elif self._oldSelections[1][0] < self._oldSelections[1][1]:
# - collapse the cursor to the first character of the selection
            newCursorPos = self._oldSelections[1][0]
# - set the preselection to the selection
            newSelections = [ self._oldSelections[1] ]
# - recollapse the selection to the cursor (redundant, but that's okay)
            newSelections.append( self.collapseSelection(newCursorPos) )
# - move the selection to the first old selection
            newSelections.append( self._oldSelections[1] )
        else:
            raise commands.AbortCommandException("Selection was invalid.")
# Finally, append all the previous old selections
        for i in self._oldSelections[2:]:
            newSelections.append(i)
        archyState.mainText.setCursor(newCursorPos)
        archyState.mainText.setSelectionList(newSelections)

        archyState.commandHistory.setSelectionAnchor(newCursorPos)
        
    def undo(self):
        archyState.mainText.setCursor(self._oldCursorPos)
        archyState.mainText.setSelectionList(self._oldSelections)

        archyState.commandHistory.setSelectionAnchor(self._oldCursorPos)
        

# ============================================
# Creep Right command
# ============================================

class CreepRightCommand(AbstractCreepCommand):
    def name(self):
        return "CreepRight"
    
    def dragPreselection(self, newCursorPos, preselection):
        if preselection[1] == self._oldCursorPos:
            newPreselection = [preselection[0],newCursorPos]
        elif preselection[0] == self._oldCursorPos:
            newPreselection = [newCursorPos,preselection[1]]
        elif preselection[1] == newCursorPos-1:
            newPreselection = [preselection[0],newCursorPos]
        else:
            newPreselection = [newCursorPos, newCursorPos]
        return newPreselection

    def execute(self):
        self.saveSelectionInfo()
        newSelections = []
# If the selection is the cursor selection:
        if self._oldSelections[1][0] == self._oldSelections[1][1]:
# - If the cursor is just to the right of the selection, then collapse the selection to the cursor, copy the preselection, and copy the selections:
            if self._oldCursorPos == (self._oldSelections[1][1]+1):
                newCursorPos = self._oldCursorPos
                newSelections.append( self.dragPreselection( newCursorPos, self._oldSelections[0] ) )
                newSelections.append( self.collapseSelection(newCursorPos) )
# - If the cursor and the selection are on the last character, then do nothing:
            elif (self._oldCursorPos == (archyState.mainText.getLength()-1)) and (self._oldSelections[1][0] == (archyState.mainText.getLength()-1)):
                newCursorPos = self._oldCursorPos
                newSelections.append(self._oldSelections[0])
                newSelections.append(self._oldSelections[1])
# - If the cursor and the selection are on the same character (which isn't the last), the move the cursor, the selection, and the appropriate preselection anchor right one character:
            elif self._oldCursorPos == self._oldSelections[1][0]:
                newCursorPos = self._oldCursorPos + 1
                newSelections.append( self.dragPreselection( newCursorPos, self._oldSelections[0] ) )
                newSelections.append( self.collapseSelection(newCursorPos) )
            else:
                newCursorPos = self._oldCursorPos
                newSelections.append(self.collapseSelection(newCursorPos) )
                newSelections.append(self.collapseSelection(newCursorPos) )
# If there is an extended selection:
        elif self._oldSelections[1][0] < self._oldSelections[1][1]:
# -collapse the cursor to the last character of the selection
            newCursorPos = self._oldSelections[1][1]
# -make sure the preselection is set to the selection
            newSelections.append( [self._oldSelections[1][0], newCursorPos] )
            newSelections.append( self.collapseSelection(newCursorPos) )
# -move the selection to the first old selection
            newSelections.append( self._oldSelections[1] )
        else:
            raise commands.AbortCommandException("Selection was invalid.")
        for i in self._oldSelections[2:]:
            newSelections.append(i)
        archyState.mainText.setCursor(newCursorPos)
        archyState.mainText.setSelectionList(newSelections)

        archyState.commandHistory.setSelectionAnchor(newCursorPos)

    def undo(self):
        archyState.mainText.setCursor(self._oldCursorPos)
        archyState.mainText.setSelectionList(self._oldSelections)

        archyState.commandHistory.setSelectionAnchor(self._oldCursorPos)

# ============================================
# AbstractLeap command object
# Code common to both LEAP forward and LEAP backward
# ============================================

class AbstractLeapCommand(commands.CommandObject):
    def __init__(self, target = ''):
        self._target = ''
# TO DO: Eliminate this!!
        if target:
            self._target = target

    def setinfo(self, target = ""):
        self._target = target

    def recordable(self):
        return 1
        
    def collapseSelection(self, newCursorPos):
        return [newCursorPos, newCursorPos]

    def _updateSelections(self, firstOccurance):
        newCursorPos = firstOccurance
# Set the preselection:
        if self._oldCursorPos <= newCursorPos:
            newSelections = [ [self._oldCursorPos, newCursorPos] ]
        else:
            newSelections = [ [newCursorPos, self._oldSelections[1][1] ] ]
# Collapse the selection:
        newSelections.append( self.collapseSelection(newCursorPos) )
# Update the old selections:
        if self._oldSelections[1][0] == self._oldSelections[1][1]: 
            oldIndex = 2
        else: 
            oldIndex = 1
        for i in self._oldSelections[oldIndex:]:
            newSelections.append(i)
# Write the changes to the main text:
        archyState.mainText.setCursor(newCursorPos)
        archyState.mainText.setSelectionList(newSelections)

        archyState.commandHistory.setSelectionAnchor(newCursorPos)

    def execute(self):
        self._oldCursorPos, self._oldSelections = archyState.mainText.getNonContentMemento()
        firstOccurance = self.findTarget(self._oldSelections[1][1]+1)
        if firstOccurance == -1:
            if self._target == "": 
                self._status = 0
                raise commands.AbortCommandException("Leap to "+self._target+" failed.")
            else: 
                self._status = -1
                raise commands.AbortCommandException("Leap to "+self._target+" failed.")
        self._updateSelections(firstOccurance)

    def undo(self):
        archyState.mainText.setCursor(self._oldCursorPos)
        archyState.mainText.setSelectionList(self._oldSelections)

        archyState.commandHistory.setSelectionAnchor(self._oldCursorPos)

    def addChar(self, newChar):
        self._target += newChar
        firstOccurance = self.findTarget(self._oldSelections[1][1]+1)
        if firstOccurance == -1:
            if self._target == "": 
                self._status = 0
                self.undo()
                raise commands.AbortCommandException("Leap to "+self._target+" failed.")
            else: 
                self._status = -1
                self.undo()
                raise commands.AbortCommandException("Leap to "+self._target+" failed.")
        self._status = 1
        self._updateSelections(firstOccurance)

    def delChar(self):
        if len(self._target)==0:
            self._status = 0
            return
        self._target = self._target[:-1]
        if len(self._target)==0:
            self._status = 0
            self.undo()
            return
        firstOccurance = self.findTarget(self._oldSelections[1][1]+1)
        self.undo()
        if firstOccurance == -1:
            if self._target == "": 
                self._status = 0
                raise commands.AbortCommandException("Leap to "+self._target+" failed.")
            else: 
                self._status = -1
                raise commands.AbortCommandException("Leap to "+self._target+" failed.")
        self._status = 1
        self._updateSelections(firstOccurance)

    def status(self):
        return self._status

    def isTargetAllDocs(self):
        for i in self._target:
            if i <> '`':
                return False
        if self._target <> "":
            return True
        else:
            return False


# ============================================
# LEAP forward command
# ============================================

# Directions used by text_array.TextArray.find(..)
_FORWARD = 1
_BACKWARD = 0

class LeapForwardCommand(AbstractLeapCommand):
    def name(self):
        return "LEAP forward to:" + self._target

    def findTarget(self, startPos):
        firstOccurance = archyState.mainText.textArray.find(self._target, startPos, _FORWARD)
        # if not found see if it matches the infinite number of doc characters at the end of text
        if firstOccurance == -1 :
            if self.isTargetAllDocs():
                firstOccurance = archyState.mainText.textArray.getLength()-1
            else:
                firstOccurance = archyState.mainText.textArray.find(self._target, 0, _FORWARD)
        return firstOccurance


# ============================================
# LEAP backward command
# ============================================

class LeapBackwardCommand(AbstractLeapCommand):
    def name(self):
        return "LEAP backward to:" + self._target

    def findTarget(self, startPos):
        startPos -= 1
        if startPos < 1:
            startPos = archyState.mainText.textArray.getLength()-1
        firstOccurance = archyState.mainText.textArray.find(self._target, startPos, _BACKWARD)
        if firstOccurance == -1:
            if self.isTargetAllDocs():
                firstOccurance = 0
            else:
                firstOccurance = archyState.mainText.textArray.find(self._target, archyState.mainText.textArray.getLength()-1, _BACKWARD)
        return firstOccurance



# ============================================
# AbstractRepeatLeap command object
# Code common to both repeat LEAP forward and repeat LEAP backward
# Only difference is the updateSelections routine.
# ============================================

class AbstractRepeatLeapCommand(AbstractLeapCommand):

    def _updateSelections(self, firstOccurance):
# Move the cursor:
        newCursorPos = firstOccurance
# Update the preselection anchor that moves with the cursor:
# If the cursor was sitting on the end of the selection:
# -and if the selection beginning is to the left of the new cursor position:
# --set the preselection from the beginning of the selection to the cursor
# -else if the selection beginning is to the right or on the new cursor position:
# --set the preselection from the cursor to the beginning of the selection
# If the cursor was sitting on the beginning of the selection:
# -and if the end of the selection is to the left of the new cursor position:
# --set the preselection from the end of the selection to the new cursor position
# -else if the end of the selection is to the right or on the new cursor position:
# --set the preselection from the new cursor position to the selection end
# else:
# -set the preselection to the new cursor position
        anchor = archyState.commandHistory.getSelectionAnchor()
        if self._oldCursorPos == self._oldSelections[0][1]:
            if self._oldSelections[0][0] <= newCursorPos:
                newSelections = [ [self._oldSelections[0][0], newCursorPos] ]
            else:
                newSelections = [ [newCursorPos, self._oldSelections[0][0]] ]
        elif self._oldCursorPos == self._oldSelections[0][0]:
            if self._oldSelections[0][1] <= newCursorPos:
                newSelections = [ [self._oldSelections[0][1], newCursorPos] ]
            else:
                newSelections = [ [newCursorPos, self._oldSelections[0][1]] ]
        else:
            newSelections = [ [newCursorPos, newCursorPos] ]
# Collapse the selection:
        newSelections.append( self.collapseSelection(newCursorPos) )
# Update the old selections:
        if self._oldSelections[1][0] == self._oldSelections[1][1]: oldIndex = 2
        else: oldIndex = 1
        for i in self._oldSelections[oldIndex:]:
            newSelections.append(i)
        archyState.mainText.setCursor(newCursorPos)
        archyState.mainText.setSelectionList(newSelections)

        archyState.commandHistory.setSelectionAnchor(newCursorPos)

# ============================================
# Repeat LEAP forward command
# ============================================

# Directions used by text_array.TextArray.find(..)
_FORWARD = 1
_BACKWARD = 0

class RepeatLeapForwardCommand(AbstractRepeatLeapCommand):
    def name(self):
        return "Repeat LEAP forward"
    
    def findTarget(self, startPos):
        firstOccurance = archyState.mainText.textArray.find(self._target, startPos, _FORWARD)
        # if not found see if it matches the infinite number of doc characters at the end of text
        if firstOccurance == -1 :
            if self.isTargetAllDocs():
                firstOccurance = archyState.mainText.textArray.getLength()-1
            else:
                firstOccurance = archyState.mainText.textArray.find(self._target, 0, _FORWARD)
        return firstOccurance


# ============================================
# LEAP backward command
# ============================================

class RepeatLeapBackwardCommand(AbstractRepeatLeapCommand):
    def name(self):
        return "Repeat LEAP backward"

    def findTarget(self, startPos):
        startPos -= 1
        if startPos < 1:
            startPos = archyState.mainText.textArray.getLength()-1
        firstOccurance = archyState.mainText.textArray.find(self._target, startPos, _BACKWARD)
        if firstOccurance == -1:
            if self.isTargetAllDocs():
                firstOccurance = 0
            else:
                firstOccurance = archyState.mainText.textArray.find(self._target, archyState.mainText.textArray.getLength()-1, _BACKWARD)
        return firstOccurance



# ============================================
# Cursor Observer class
# for monitoring and implementing Focus behaviors
# ============================================

class CursorObserver:
    def __init__(self):
        archyState.mainText.addObserver(self)
        self.oldPos = 0
        self.behaviorExtent = None

    def onAddText(self, insertPos, textLen):
        return

    def onDelText(self, startPos, endPos):
        return

    def onClear(self):
        return

    def onSelectionsChanged(self):
        return

    def onCursorChange(self):
        pos = archyState.mainText.getCursorPos()

        if self.behaviorExtent <> None:
            unfocus = pos < min(self.behaviorExtent) or pos > max(self.behaviorExtent)
        else:
            unfocus = 0

        if unfocus:
            unfocusBehaviors = filter(lambda com:com <> None, archyState.mainText.behaviorArray.getUnfocusBehavior(self.oldPos))
            for com in unfocusBehaviors:
                unfocusCommand = com()
                unfocusCommand.execute()


        focusBehaviors = filter(lambda com:com <> None, archyState.mainText.behaviorArray.getFocusBehavior(pos))
        for com in focusBehaviors:
            focusCommand = com()
            focusCommand.execute()
            self.behaviorExtent = archyState.mainText.behaviorArray.findActionExtent(focusCommand.behaviorName(), pos)

        if len(focusBehaviors) < 1:
            self.behaviorExtent = None
        
        #print self.behaviorExtent
        self.oldPos = pos

SYSTEM_COMMANDS = [LeapBackwardCommand, LeapForwardCommand, RepeatLeapBackwardCommand, RepeatLeapForwardCommand, CreepRightCommand, CreepLeftCommand]
