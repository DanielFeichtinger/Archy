# system_functions.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
from archy_state import archyState
import string
import pygame_run


class CommandsCommand(commands.CommandObject):
    def name(self):
        return "COMMANDS"
    def execute(self):
        mT = archyState.mainText
        
        
        explanation = '\n\nFor an annotated command list, Leap to the Help Document by leaping to "H [space] E [space] L [space] P", where [space] indicates a tap of the Space Bar. Alternatively, just leap to the command name you wish to know about; use Leap Again until you find the command description.\n\n'
        cmdString = string.join(archyState.commandMap.commandList(), ', ')
        self.addText = archyState.commandMap.findSystemCommand("AddText")
        self.addText.setinfo(explanation+cmdString)
        self.addText.execute()
        

    def undo(self):
        self.addText.undo()

#end class CommandsCommand

class ShowMouseCommand(commands.CommandObject):
    def name(self):
        return "SHOW MOUSE"
        
    def execute(self):
        self.old_state = pygame_run.get_mouse_visibility()
        pygame_run.set_mouse_visibility(1)

    def undo(self):
        pygame_run.set_mouse_visibility(self.old_state)

class HideMouseCommand(commands.CommandObject):
    def name(self):
        return "HIDE MOUSE"
    
    def recordable(self):
        return 0

    def execute(self):
        self.old_state = pygame_run.get_mouse_visibility()
        pygame_run.set_mouse_visibility(0)

    def undo(self):
        pygame_run.set_mouse_visibility(self.old_state)

class FullscreenCommand(commands.CommandObject):
    def name(self):
        return "FULL SCREEN"
    
    def recordable(self):
        return 0
    
    def execute(self):
        if pygame_run.get_fullscreen_mode() == 1:
            raise commands.AbortCommandException("Already in fullscreen mode.")
        pygame_run.set_fullscreen_mode(1)

class UnFullscreenCommand(commands.CommandObject):
    def name(self):
        return "PARTIAL SCREEN"
    
    def recordable(self):
        return 0

    def execute(self):
        if pygame_run.get_fullscreen_mode() == 0:
            raise commands.AbortCommandException("Already in unfullscreen mode.")
        pygame_run.set_fullscreen_mode(0)

class SystemInfoCommand(commands.CommandObject):
    def name(self):
        return "SYSTEM INFO"
    

    def execute(self):
        import debug

        text = debug.get_system_info()
        self.addTextCmd = archyState.commandMap.findSystemCommand("AddText")
        self.addTextCmd.setinfo(text)
        self.addTextCmd.execute()

    def undo(self):
        self.addTextCmd.undo()

class SimulateBuggyCommand(commands.CommandObject):
    def name(self):
        return "SIMULATE BUGGY COMMAND"

    def execute(self):
        nonexistent_function()

    def undo(self):
        pass

COMMANDS = []
BEHAVIORS = []

COMMANDS.append(CommandsCommand )
COMMANDS.append(ShowMouseCommand )
COMMANDS.append(HideMouseCommand )
COMMANDS.append(FullscreenCommand )
COMMANDS.append(UnFullscreenCommand )
COMMANDS.append(SystemInfoCommand )

def init():
    import debug

    if debug.DEVELOPER_MODE:
        COMMANDS.append(SimulateBuggyCommand )
