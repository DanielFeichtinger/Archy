# text_editing.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
from archy_state import archyState
import text_editing
import style

# --- --- ---

class SimpleStyleCommandAbstract(commands.CommandObject):
    def setStyleOverlay(self, **dict):
        self.theStyle = dict
        
    def setStyleDictionary(self, dict):
        self.theStyle = dict

    def execute(self):
    
        mT = archyState.mainText
        start, end = mT.getSelection('selection')

        copiedText, self.copiedStyle = mT.getStyledText(start, end)

        newOverlay = archyState.stylePool.newStyleOverlay(style = self.theStyle)
        mT.setStyleOverlay(newOverlay, start, end)
        mT.setCursor( mT.getCursorPos() )

        self.startPos = start
        self.endPos = end

    def undo(self):
        mT = archyState.mainText
        mT.setStyle(self.copiedStyle, self.startPos, 0)
        mT.setCursor( mT.getCursorPos() )

#end class SimpleStyleCommandAbstract

class StyleCommandAbstract(commands.CommandObject):
    def setStyleOverlay(self, **dict):
        self.theStyle = dict

    def setStyleDictionary(self, dict):
        self.theStyle = dict

    def execute(self):
        mT = archyState.mainText
        cursorPos = mT.getCursorPos()
        start, end = mT.getSelection('selection')
        
        self.styleCommands = []
        
        for ranges in mT.behaviorArray.styleableRanges(start, end):
            mT.setSelection('selection', *ranges)
            for com in mT.behaviorArray.getStyleBehavior(cursorPos):
                styleCommand = com()
                styleCommand.setStyleDictionary(self.theStyle)
                styleCommand.execute()
                self.styleCommands.append(styleCommand)
                
                if styleCommand.stopBit():
                    break

        mT.setSelection('selection', start, end)
            

    def undo(self):
        for command in self.styleCommands:
            command.undo()

#end class StyleCommandAbstract

# --- --- ---

# This is the perfered method of programatically changing text style.

class StyleCommand(StyleCommandAbstract):
    def __init__(self, **dict):
        self.theStyle = dict
        
    def name(self):
        return "Style"
        
    def setinfo(self, **dict ):
        self.theStyle = dict
    
    def setStyleDictionary(self, dict):
        self.theStyle = dict

SYSTEM_COMMANDS = [StyleCommand]