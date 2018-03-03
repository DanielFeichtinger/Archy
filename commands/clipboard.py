# clipboard.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# This module provides functionality that interfaces with the system clipboard on various operating systems, and uses said functionality to implement the COPYIN and COPYOUT commands.
# --------------------------
# Module imports
# --------------------------
import commands
# --------------------------
# Clipboard-interfacing functions
# --------------------------
def onClipboardNotCompatibleFormat():
       raise commands.AbortCommandException("Clipboard does not contain text data.")

def getClipboard():
    import platform_specific

    text = platform_specific.getClipboard()

    if not isinstance(text, basestring):
           onClipboardNotCompatibleFormat()
    try:
        text = unicode(text)
    except:
        text = unicode(text, 'iso-8859-1')
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    return text

def setClipboard(text):
    import platform_specific
    try:
        import os

        text = str(text)
        text = text.replace("\n", os.linesep)
        platform_specific.setClipboard(text)
        return True
    except:
        return False

# --------------------------
# The COPYIN Command
# --------------------------
class CopyinCommand(commands.CommandObject):
    def __init__(self):
        commands.CommandObject.__init__(self)
        self.addText = None
        
    def name(self):
        return "COPY IN"
    def execute(self):
        from archy_state import archyState
        if self.addText == None:
            text = getClipboard()
            self.addText = archyState.commandMap.findSystemCommand("AddText")
            self.addText.setinfo(text)
        self.addText.execute()
    def undo(self):
        self.addText.undo()
# --------------------------
# The COPYOUT Command
# --------------------------
class CopyoutCommand(commands.CommandObject):
    def name(self):
        return "COPY OUT"
    def recordable(self):
        return 0
    
    def execute(self):
        from archy_state import archyState
        textRange = archyState.mainText.getSelection('selection')
        selectedText = archyState.mainText.textArray.getSubString(*textRange)
        setClipboard(selectedText)
    def undo(self):
        pass
# --------------------------
# Module Initialization
# --------------------------

COMMANDS = [CopyinCommand, CopyoutCommand]
BEHAVIORS = []
