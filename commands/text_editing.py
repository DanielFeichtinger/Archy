# text_editing.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
import messages
from archy_state import archyState


# --- --- ---
class SelectCommand(commands.CommandObject):
    def name(self):
        return "Select"

    def execute(self):
        mT = archyState.mainText
        self.origCursorPos = mT.getCursorPos()
        self.origSelections = mT.copySelectionList()

        start, end = mT.getSelection('preselection')
        mT.createNewSelection( start, end)
        mT.setCursor(end+1)
        archyState.commandHistory.setSelectionAnchor(end+1)

    def undo(self):
        mT = archyState.mainText
        mT.setSelectionList(self.origSelections)
        mT.setCursor(self.origCursorPos)

#end class SelectCommand

# --- --- ---

class SingleCharacterSelectCommand(commands.CommandObject):
    def name(self):
        return "S"

    def execute(self):
        print "Setting somthing in cursor so that it makes the sel into a presel on cursor move"

    def undo(self):
        print "undoes it"

#end class SelectCommand

# --- --- ---


class SimpleAddTextCommand(commands.CommandObject):

    def __init__(self, newText, newTextStyle = None):
        #The AddTextCommand accepts styling information.
        self.newText = newText
        self.newTextStyle = newTextStyle

    def name(self):
        return "SimpleAddText"

    def execute(self):
        #print "SimpleAddText.execute()"
        mT = archyState.mainText
        self.origCursorPos = mT.getCursorPos()
        self.origSelections = mT.copySelectionList()
        
        mT.addText(self.newText, self.origCursorPos, self.newTextStyle)
# Set the last leap or creep anchor to be the cursors new position
        if len(self.newText) > 1:
            archyState.commandHistory.setSelectionAnchor( self.origCursorPos+len(self.newText) )

# Adjust selection cursor and preselection so that the selection is the new text, the cursor is one character after the selection.

        mT.createNewSelection(self.origCursorPos, self.origCursorPos+len(self.newText)-1)
        mT.setSelection('preselection', archyState.commandHistory.getSelectionAnchor(), self.origCursorPos+len(self.newText)-1)


    def undo(self):
        startPos = self.origCursorPos
        endPos = startPos + len(self.newText) - 1

        mT = archyState.mainText
        mT.delText(startPos, endPos)

        mT.setSelectionList(self.origSelections)

#end class AddTextCommand

class AddTextCommand(commands.CommandObject):
    def __init__(self, text = None, styles = None):
# TO DO: remove this!
        if text:
            self.setinfo( text, styles)
        pass

    def name(self):
        return "AddText"
        
    def setinfo(self, newText, newTextStyle = None):
        self.newText = newText
        self.newTextStyle = newTextStyle            
        
    def execute(self):
        #correctSelections = mT.copySelectionList()
        mT = archyState.mainText
        cursorPos = mT.getCursorPos()
        
        self.addCommands = []
        
        for com in mT.behaviorArray.getAddBehavior(cursorPos):
            addCommand = com(self.newText, self.newTextStyle)
            addCommand.execute()
            self.addCommands.insert(0, addCommand)
            
            if addCommand.stopBit():
                return
        
    def undo(self):
        for command in self.addCommands:
            command.undo()

# --- --- ---
class SimpleDeleteTextCommand(commands.CommandObject):  
    delDoc = 1

    def name(self):
        return "SimpleDeleteText"

    def noDeletionsDocument(self):
        self.delDoc = 0

    def execute(self):
        mT = archyState.mainText
        self.origCursorPos = mT.getCursorPos()
        self.origSelections = mT.copySelectionList()

        self.origSelStart, self.origSelEnd = mT.getSelection('selection')
        deletedText, deletedStyle= mT.getStyledText(self.origSelStart, self.origSelEnd) 
        if mT.isExtendedSelection():
            archyState.commandHistory.setSelectionAnchor(self.origSelStart)

        #delete the text
        mT.delText(self.origSelStart, self.origSelEnd)
        mT.setCursor(self.origSelStart)
        mT.setSelection('selection', mT.cursorPosInText-1)

        #Put the deleted text into the deletions document:
        correctAnchor = archyState.commandHistory.getSelectionAnchor()
        # execute the DeletionsDocAdd command
        if self.delDoc:
            self.addToDeletionCommand = archyState.commandMap.findSystemCommand("DeletionsDocAdd")
            self.addToDeletionCommand.setinfo(deletedText, deletedStyle)
            self.addToDeletionCommand.execute()
        self.deletedText, self.deletedStyle = deletedText, deletedStyle

        # reset the anchor to values before adding to deletions document
        archyState.commandHistory.setSelectionAnchor(correctAnchor)

    def undo(self):
        if self.delDoc:
            self.addToDeletionCommand.undo()
        archyState.mainText.setCursor(self.origSelStart)
        addText = AddTextCommand(self.deletedText, self.deletedStyle)
        addText.execute()

#end class SimpleDeleteTextCommand

class DeleteTextCommand(commands.CommandObject):
    def __init__(self):
        self.delDoc = 1

    def name(self):
        return "DeleteText"

    def setinfo(self, useDeletionsDocument = 1):
        self.delDoc = useDeletionsDocument

    def execute(self):
        mT = archyState.mainText
        cursorPos = mT.getCursorPos()
        self.start, self.end = mT.getSelection('selection')

        self.deleteCommands = []

        deleteCount = 0
        for ranges in mT.behaviorArray.deletableRanges(self.start, self.end):
        #This code will be  simplified once we have discontiguous selections.
            mT.setSelection('selection', ranges[0]-deleteCount, ranges[1]-deleteCount)
            
            
            for com in mT.behaviorArray.getDeleteBehavior(ranges[0]-deleteCount):
                delCommand = com()
                if not self.delDoc:
                    delCommand.noDeletionsDocument()
                delCommand.execute()
                self.deleteCommands.insert(0, delCommand)
                
                if delCommand.stopBit():
                    break
            deleteCount += (ranges[1]-ranges[0])+1


    def undo(self):
        for command in self.deleteCommands:
            command.undo()
        archyState.mainText.setSelection('selection', self.start, self.end)

# --- --- ---
# --- --- ---
# TO DO: Get rid of these non-commands!
# The CursorMovmentCommand holds common code and interfaces 
# for the LeapCommand and CreepCommand.

class CursorMovementCommand(commands.CommandObject):

    def __init__(self):
        self.origNonContentMemento = archyState.mainText.getNonContentMemento()
        
    def setNewInformation(self):
        self.newNonContentMemento = archyState.mainText.getNonContentMemento()

    def name(self):
        return "CursorMovement"

    def execute(self):
        archyState.mainText.setNonContentInformation(self.newNonContentMemento)

    def undo(self):
        archyState.mainText.setNonContentInformation(self.origNonContentMemento)
#end class MoveCursorCommand

# --- --- ---
# The LeapCommand is used to just undo/redo
# leaps from the command history. Actual LEAP is initiated from the 
# LEAP quasimode of the module key.

class LeapCommand(CursorMovementCommand):
    def name(self):
        return "LEAP"
#end class LeapCommand

# --- --- ---
# The CreepCommand is used to just undo/redo
# creeps from the command history. Actual creep is initiated from the 
# module key.

class CreepCommand(CursorMovementCommand):
    def name(self):
        return "CREEP"

#end class CreepCommand

# --- --- ---

# To do: If you expunge across locked text, undo does not work correctly
class ExpungeCommand(commands.CommandObject):
    def name(self):
        return "EXPUNGE"

    def execute(self):
        mT = archyState.mainText
        start, end = mT.getSelection('selection')
        self.length = end-start+1

        DeleteTextCommand().execute()

    def undo(self):
        AddTextCommand('*'*self.length).execute()


# --- --- ---

class AcceptReplaceCommand(commands.CommandObject):
    replacement = None

    def name(self):
        return " "

    def execute(self):
        mT = archyState.mainText

        self.origSel = mT.getSelection('selection')
        if mT.textArray.getSubString(*self.origSel).lower() <> FindNextCommand.searchTerm.lower():
            raise commands.AbortCommandException("Current selection is not \"%s\". Use command-tab to find the next instantance." % (FindNextCommand.searchTerm))

        self.origSearchEnd = FindNextCommand.searchEnd
        FindNextCommand.searchEnd += len(self.replacement) - len(FindNextCommand.searchTerm)

        self.delText = DeleteTextCommand()
        self.addText = AddTextCommand(self.replacement)
        self.findNext = FindNextCommand()

        self.delText.execute()
        self.addText.execute()
        try:
            self.findNext.execute()
        except commands.AbortCommandException, e:
            self.findNext = None
            messages.queue(e.getExplanation())

    def undo(self):
        self.addText.undo()
        self.delText.undo()
        if self.findNext:
            self.findNext.undo()
        archyState.mainText.setSelection('selection', *self.origSel)
        archyState.mainText.setCursor(self.origSel[1]+1)
        FindNextCommand.searchEnd = self.origSearchEnd

class FindNextCommand(commands.CommandObject):
    searchEnd = None
    searchTerm = None

    def name(self):
        return "\t"

    def execute(self):
        mT = archyState.mainText
    
        self.cursorPos = mT.getCursorPos()
        self.origSel = mT.getSelection('selection')

        pos = mT.textArray.find(self.searchTerm, self.cursorPos)
        if pos < self.searchEnd and pos > 0:
            mT.setSelection('selection', pos, pos+len(self.searchTerm)-1)
            mT.setCursor(pos+len(self.searchTerm))
        else:
            messages.unqueue('persistant')
            archyState.commandMap.unregisterCommand(FindNextCommand())
            archyState.commandMap.unregisterCommand(AcceptReplaceCommand())
            raise commands.AbortCommandException("Last \"%s\" found within selected range." % (self.searchTerm))

    def undo(self):
        mT = archyState.mainText
        mT.setSelection('selection', *self.origSel)
        mT.setCursor(self.cursorPos)

class EndReplaceCommand(commands.CommandObject):
    def name(self):
        return "END"

    def execute(self):
        messages.unqueue('persistant')
        archyState.commandMap.unregisterCommand(FindNextCommand())
        archyState.commandMap.unregisterCommand(AcceptReplaceCommand())
        archyState.commandMap.unregisterCommand(EndReplaceCommand())

    def undo(self):
        archyState.commandMap.registerCommand(EndReplaceCommand())
        archyState.commandMap.registerCommand(AcceptReplaceCommand())
        archyState.commandMap.registerCommand(FindNextCommand())

        messages.queue("command-space: change\ncommand-tab: find next\nEND - Exit REPLACE", "persistant")

class ReplaceCommand(commands.CommandObject):
    def name(self):
        return "REPLACE"

    def execute(self):
        mT = archyState.mainText
        foSel = mT.getSelection('first old selection')
        oSel = mT.getSelection('old selection')
        sel = mT.getSelection('selection')

        self.origSel = sel
        self.origCursor = mT.getCursorPos()

        searchTerm = mT.textArray.getSubString(*foSel)
        replacement = mT.textArray.getSubString(*oSel)

        pos = mT.textArray.find(searchTerm, sel[0])
        if pos < sel[1] and pos > 0:
            mT.setSelection('selection', pos, pos+len(searchTerm)-1)
            mT.setCursor(pos+len(searchTerm))
            
            FindNextCommand.searchEnd = sel[1]
            FindNextCommand.searchTerm = searchTerm
            AcceptReplaceCommand.replacement = replacement

            archyState.commandMap.unregisterCommand(AcceptReplaceCommand())
            archyState.commandMap.unregisterCommand(FindNextCommand())
            archyState.commandMap.unregisterCommand(EndReplaceCommand())
            
            archyState.commandMap.registerCommand(AcceptReplaceCommand())
            archyState.commandMap.registerCommand(FindNextCommand())
            archyState.commandMap.registerCommand(EndReplaceCommand())

            messages.queue("command-space: change\ncommand-tab: find next\nEND - Exit REPLACE", "persistant")

        else:
            raise commands.AbortCommandException('\"%s\" was not found in the selection.' % (searchTerm))

    
    def undo(self):
        mT = archyState.mainText

        mT.setSelection('selection', *self.origSel)
        mT.setCursor(self.origCursor)

class SetSelectionCommand(commands.CommandObject):
    def __init__(self):
        pass

    def setinfo(self, selectionName, start, end):
        self.selectionName = selectionName
        self.start = start
        self.end = end

    def name(self):
        return "SetSelection"

    def execute(self):
        mT = archyState.mainText
        self.old_start, self.old_end = mT.getSelection(self.selectionName)
        mT.setSelection(self.selectionName, self.start, self.end)

    def undo(self):
        mT = archyState.mainText
        mT.setSelection(self.selectionName, self.old_start, self.old_end)

class SetCursorCommand(commands.CommandObject):
    def __init__(self):
        pass

    def setinfo(self, pos):
        self.pos = pos

    def name(self):
        return "SetCursor"

    def execute(self):
        mT = archyState.mainText
        self.old_pos = mT.getCursorPos()
        mT.setCursor(self.pos)

    def undo(self):
        mT = archyState.mainText
        mT.setCursor(self.old_pos)

class SetSelectionListCommand(commands.CommandObject):
    def __init__(self):
        pass
    
    def setinfo(self, selections):
        self.selections = selections

    def name(self):
        return "SetSelectionList"

    def execute(self):
        mT = archyState.mainText
        self.old_selections = mT.copySelectionList()
        mT.setSelectionList(self.selections)

    def undo(self):
        mT = archyState.mainText
        mT.setSelectionList(self.old_selections)

# -- --- ---

# Initialization for the Command objects

COMMANDS = []
BEHAVIORS = []
SYSTEM_COMMANDS = []

COMMANDS.append(ReplaceCommand)
COMMANDS.append(ExpungeCommand)
COMMANDS.append(SingleCharacterSelectCommand)

SYSTEM_COMMANDS.append( AddTextCommand )
SYSTEM_COMMANDS.append( DeleteTextCommand )
SYSTEM_COMMANDS.append( SelectCommand )
SYSTEM_COMMANDS.append( SetCursorCommand )
SYSTEM_COMMANDS.append( SetSelectionListCommand )
SYSTEM_COMMANDS.append( SetSelectionCommand )

# AddText, DeleteText, LeapCommand and CreepCommand are not 
# registerCommand()-ed since they are not run from the command quasimode.


