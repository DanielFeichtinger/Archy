# text-insert.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
from archy_state import archyState


class AbstractAddAwayFromCursor(commands.CommandObject):
    def __init__(self):
        self.cursorCommands = []
        self.selectionCommands = []
        self.newText = ""
        self.newStyles = None
        
    def name(self):
        return "AddAwayFromCursor"
        
    def addSelectionCommand(self, newCommand):
        self.selectionCommands.append( newCommand )
        
    def movePosition(self, a):
        if a >= self.finalCursorPos:
            a += len(self.newText)
        return a
    
    def addCursorMovementCommand(self, newCommand):
        self.cursorCommands.append( newCommand )
    
    def setinfo(self, newText, newStyles = None):
        self.newText = newText
        self.newStyles = newStyles
    
    def execute(self):          
        self.oldCursorPos = archyState.mainText.getCursorPos()
        oldSelections = archyState.mainText.copySelectionList()
        
        self.addTextCommand = archyState.commandMap.findSystemCommand("AddText")
        self.addTextCommand.setinfo(self.newText, self.newStyles)
        self.finalCreep = archyState.commandMap.findSystemCommand("CreepLeft")
        
        for com in self.cursorCommands:
            com.execute()
        self.addTextCommand.execute()
        for com in self.selectionCommands:
            com.execute()
        self.finalCreep.execute()
        self.finalCursorPos = archyState.mainText.getCursorPos()
        archyState.mainText.setCursor( self.movePosition( self.oldCursorPos ) )
        archyState.mainText.setSelectionList( map( lambda c: (self.movePosition(c[0]),self.movePosition(c[1]) ), oldSelections ) )
        
    def undo(self):
        self.selectionCommands.reverse()
        self.cursorCommands.reverse()
        
        self.finalCreep.undo()
        for com in self.selectionCommands:
            com.undo()
        self.addTextCommand.undo()
        for com in self.cursorCommands:
            com.undo()
        
        self.selectionCommands.reverse()
        self.cursorCommands.reverse()

"""
# Algorithm:

store a = cursor pos, b = selections
leap, creep to target pos
addTextCommand
for com in self.whileSelectedCommand:
    com.execute()
creep left
setCursorPos( self.move( a ) )
setSelectionList( map( lambda c: (self.movePosition(c[0]),self.movePosition(c[1]) ), selections )
"""


class DeletionsDocAdd(AbstractAddAwayFromCursor):
    def init(self):
        self.cursorCommands = []
        self.selectionCommands = []
        #self.addSelectionCommand( archyState.commandMap.findSystemCommand("LOCK") )
        leap1 = archyState.commandMap.findSystemCommand("LEAP forward to:")
        leap1.setinfo("`D E L E T I O N S \n")
        self.addCursorMovementCommand( leap1 )
        leap2 = archyState.commandMap.findSystemCommand("LEAP forward to:")
        leap2.setinfo("\n")
        self.addCursorMovementCommand( leap2 )
        self.addCursorMovementCommand( archyState.commandMap.findSystemCommand("CreepRight") )
        self.addCursorMovementCommand( archyState.commandMap.findSystemCommand("CreepRight") )
        if len(self.newText) > 1:
            self.newText = "".join( [self.newText, "\n"] )

    def execute(self):
        self.init()
        AbstractAddAwayFromCursor.execute(self)
        
    def name(self):
        return "DeletionsDocAdd"
        
        
SYSTEM_COMMANDS = [DeletionsDocAdd]
