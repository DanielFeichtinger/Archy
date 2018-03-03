# lock.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
from archy_state import archyState

import behavior_editing

import behavior
import messages

# --- --- ---


# -- Start Normal Lock --

class LockAddCommand(behavior.AddCommand):
    def behaviorName(self):
        return "LOCK"

    def execute(self):
        self.origCursor = archyState.mainText.getCursorPos()
        moveOver = 0
        self.history = []
        
        startPos, endPos = self.findExtent(archyState.mainText)
        
        if self.origCursor == startPos:
            moveOver = 1
            archyState.mainText.setCursor(startPos)
        else:
            archyState.mainText.setCursor(endPos+1)
        
        if moveOver:
            archyState.mainText.setSelection('selection', startPos, startPos)
            theAction = behavior_editing.RemoveActionCommand(self.behaviorName())
            addText = archyState.commandMap.findSystemCommand("AddText")
            addText.setinfo(self.newText, self.newTextStyle)
            theStyle = archyState.commandMap.findSystemCommand("Style")
            theStyle.setinfo(backgroundColor = (255,255,255), foregroundColor = (0,0,0))
            
            theAction.execute()
            addText.execute()
            theStyle.execute()
            
            self.history.append(theAction)
            self.history.append(addText)
            self.history.append(theStyle)
            
            selStart, selEnd = archyState.mainText.getSelection('selection')
            archyState.mainText.setSelection('selection', selEnd+1, selEnd+1)
            self.theAction = behavior_editing.AddActionCommand(self.behaviorName())
            self.theAction.execute()
            self.history.append(self.theAction)
            
            archyState.mainText.setSelection('selection', selStart, selEnd)
        else:
            addText = archyState.commandMap.findSystemCommand("AddText")
            addText.setinfo(self.newText, self.newTextStyle)
            addText.execute()
            self.history.append(addText)
            messages.queue('You cannot type in Locked text.')
            messages.display()
            
            
        
    def undo(self):
        self.history.reverse()
        for com in self.history:
            com.undo()
        archyState.mainText.setCursor(self.origCursor)
        
    def stopBit(self):
        return 1
        
class LockStyleCommand(behavior.StyleCommand):
    def behaviorName(self):
        return "LOCK"

    def stopBit(self):
        return 1
    
class LockDeleteCommand(behavior.DeleteCommand):
    def behaviorName(self):
        return "LOCK"
    
    def stopBit(self):
        return 1

class LockCommand(commands.CommandObject):
    def name(self):
        return "LOCK"

    def execute(self):
        selStart, selEnd = archyState.mainText.getSelection('selection')
        
        self.theStyle = archyState.commandMap.findSystemCommand("Style")
        self.theStyle.setinfo(backgroundColor = (245,245,245), foregroundColor = (200,70,70))
        self.theStyle.execute()
        
        self.theAction = behavior_editing.AddActionCommand("LOCK")
        self.theAction.execute()
    
    def undo(self):
        self.theAction.undo()
        self.theStyle.undo()
        

#end class LockCommand

class UnlockCommand(commands.CommandObject):
    def name(self): 
        return "UNLOCK"
                    
    def execute(self):
        start, end = archyState.mainText.getSelection('selection')
        
        self.theAction = behavior_editing.RemoveActionCommand("LOCK")
        self.theAction.execute()

        self.theAction2 = behavior_editing.RemoveActionCommand("FORM LOCK")
        self.theAction2.execute()
        
        self.theStyle = archyState.commandMap.findSystemCommand("Style")
        self.theStyle.setinfo(backgroundColor = (255,255,255), foregroundColor = (0,0,0))
        self.theStyle.execute()
        
    def undo(self):
        self.theStyle.undo()
        self.theAction2.undo()
        self.theAction.undo()
        



# -- End Normal Lock --




# -- Start System Lock --

class SystemLockAddCommand(LockAddCommand):
    def behaviorName(self):
        return "SYSTEM LOCK"

class SystemLockDeleteCommand(LockDeleteCommand):
    def behaviorName(self):
        return "SYSTEM LOCK"
        
class SystemLockStyleCommand(LockStyleCommand):
    def behaviorName(self):
        return "SYSTEM LOCK"


class SystemLockCommand(commands.CommandObject):
    def name(self):
        return "System Lock"

    def execute(self):
        selStart, selEnd = archyState.mainText.getSelection('selection')
        
        self.theStyle = archyState.commandMap.findSystemCommand("Style")
        self.theStyle.setinfo(backgroundColor = (245,245,245), foregroundColor = (200,70,70))
        self.theStyle.execute()
        
        self.theAction = behavior_editing.AddActionCommand("SYSTEM LOCK")
        self.theAction.execute()
    
    def undo(self):
        self.theAction.undo()
        self.theStyle.undo()
        
class SystemUnlockCommand(commands.CommandObject):
    def name(self): 
        return "System Unlock"
                    
    def execute(self):
        start, end = archyState.mainText.getSelection('selection')
        
        self.theAction = behavior_editing.RemoveActionCommand("SYSTEM LOCK")
        self.theAction.execute()
        
        self.theStyle = archyState.commandMap.findSystemCommand("Style")
        self.theStyle.setinfo(backgroundColor = (255,255,255), foregroundColor = (0,0,0))
        self.theStyle.execute()
        
    def undo(self):
        self.theStyle.undo()
        self.theAction.undo()

# -- End System Lock --



# -- Start Form Lock --

class FormLockAddCommand(LockAddCommand):
    def behaviorName(self):
        return "FORM LOCK"

    
    def execute(self):
        self.origCursor = archyState.mainText.getCursorPos()
        moveOver = 0
        self.history = []
        
        startPos, endPos = self.findExtent(archyState.mainText)
        
        archyState.mainText.setCursor(endPos+1)
        
        addText = archyState.commandMap.findSystemCommand("AddText")
        addText.setinfo(self.newText, self.newTextStyle)
        addText.execute()
        self.history.append(addText)
    

class FormLockDeleteCommand(LockDeleteCommand):
    def behaviorName(self):
        return "FORM LOCK"
        
class FormLockStyleCommand(LockStyleCommand):
    def behaviorName(self):
        return "FORM LOCK"
        

class FormLockCommand(commands.CommandObject):
    def name(self):
        return "Form Lock"

    def execute(self):
        self.theStyle = archyState.commandMap.findSystemCommand("Style")
        self.theStyle.setinfo(backgroundColor = (245,245,245), foregroundColor = (200,70,70))
        self.theStyle.execute()
        
        self.theAction = behavior_editing.AddActionCommand("FORM LOCK")
        self.theAction.execute()
    
    def undo(self):
        self.theAction.undo()
        self.theStyle.undo()
        
# -- End Form Lock --

# -- Start Initial Document Character Lock --


class InitialDocumentCharacterLockCommand(commands.CommandObject):
    def name(self):
        return "InitialDocumentLock"

    def execute(self):
        self.theStyle = archyState.commandMap.findSystemCommand("Style")
        self.theStyle.setinfo(backgroundColor = (245,245,245), foregroundColor = (200,70,70))
        self.theStyle.execute()
        
        self.theAction = behavior_editing.AddActionCommand("INITIAL DOCUMENT CHARACTER LOCK")
        self.theAction.execute()
    
    def undo(self):
        self.theAction.undo()
        self.theStyle.undo()
        
# -- End Initial Document Character Lock --

# -- Start Final Document Character Lock --         

class FinalDocumentCharacterLockDeleteCommand(LockDeleteCommand):
    def behaviorName(self):
        return "FINAL DOCUMENT CHARACTER LOCK"
        
class FinalDocumentCharacterLockStyleCommand(LockStyleCommand):
    def behaviorName(self):
        return "FINAL DOCUMENT CHARACTER LOCK"

class FinalDocumentCharacterLockCommand(commands.CommandObject):
    def name(self):
        return "FinalDocumentLock"

    def execute(self):
        selStart, selEnd = archyState.mainText.getSelection('selection')
        
        self.theAction = behavior_editing.AddActionCommand("FINAL DOCUMENT CHARACTER LOCK")
        self.theAction.execute()
    
    def undo(self):
        self.theAction.undo()
        self.theStyle.undo()
        
# -- End Final Document Character Lock --


SYSTEM_COMMANDS = [InitialDocumentCharacterLockCommand, FinalDocumentCharacterLockCommand, FormLockCommand]
COMMANDS = [LockCommand, UnlockCommand]
BEHAVIORS = []

BEHAVIORS.append( {'name':"LOCK", 'add' : LockAddCommand, 'delete' : LockDeleteCommand, 'style' : LockStyleCommand} )
BEHAVIORS.append( {'name':"SYSTEM LOCK", 'add' : SystemLockAddCommand, 'delete' : SystemLockDeleteCommand, 'style' : SystemLockStyleCommand} )
BEHAVIORS.append( {'name':"FORM LOCK",  'add' : FormLockAddCommand, 'delete' : FormLockDeleteCommand, 'style' : FormLockStyleCommand} )
BEHAVIORS.append( {'name':"INITIAL DOCUMENT CHARACTER LOCK",    'add' : FormLockAddCommand, 'delete' : FormLockDeleteCommand, 'style' : FormLockStyleCommand} )
BEHAVIORS.append( {'name':"FINAL DOCUMENT CHARACTER LOCK",  'delete' : FinalDocumentCharacterLockDeleteCommand, 'style' : FinalDocumentCharacterLockStyleCommand} )

