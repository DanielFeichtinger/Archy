# api.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: api.hpy,v 1.15 2005/04/04 04:04:50 andrewwwilson Exp $"

# This module defines an Application Programming Interface (API) for Archy.  It is useful for the following reasons:

# (1) It serves as a facade to the entire functionality of Archy.  As such, it brings with it all the advantages of a Facade pattern (GoF 1994)--namely, a reduction of client-subsystem coupling.

# (2) It follows from (1) that the API will provide a consistent interface to client code.  While the internal architecture of Archy may change significantly due to refactoring, the API will remain constant and simple, so client code won't need to be changed as Archy's internal architecture changes.

# (3) Because this API will be the only access point user-written code has with Archy, it will be easier to make Archy thread-safe to end-user code; for instance, a simple solution would be to put mutexes around each API call.

# (4) Also because the API will be the only access point user-written code has with Archy, it will be very easy to track changes to Archy's state.  In concert with the commands.recording module, the API allows state changes to be recorded and undone without any extra effort on the part of the user.  As a result, users should never have to write their own "custom" undo routines for their commands unless they need to undo something that Archy doesn't control--for instance, information on a remote web server.

# NOTE: It is assumed that all the API calls are made between calls to commands.recording.startRecording() and commands.recording.stopRecording(), respectively.  This is always the case with user-written code executed via the RUN command and user-written commands.

# In order to create an API function, a few rules must be observed.

# .  * If the API function serves only to read the state of Archy, but not modify it, then nothing special needs to be done.

# .  * If the function *does* modify the state of Archy, the command recorder must have some sort of "breadcrumb" it can follow so it can transparently undo the action if necessary (e.g., if the user executes the UNDO command or the command aborts at some point and the state of Archy needs to be rolled back).  In order to provide this undo information, the API call must encapsulate its modifications to Archy's state in a Command object and pass this command object to the commands.recording.execute_and_record_command() function.  Note also that the Command object must be written in such a way that it observes the following rules:

# .    (TODO: I believe these rules apply for *all* Command objects, whether or not they are used by the API; perhaps we should move this list to the commands/__init__.py module?)

# .    * If something goes wrong in the middle of the Command object's execution, it must undo all changes it has made to the state of Archy so far (so that Archy is in the same state it was in before the Command was executed).

# .    * To preserve the relationship between UNDO and REDO--specifically, that a REDO restore Archy to the state it was in before the previous UNDO--the Command object's execute() method must produce the exact same result every time it is executed, after the first time it is executed.  For instance, a command called "InsertRandomNumber()" that inserts a random number into the text should insert a genuine random number the first time its execute() method is called, but every subsequent call to execute() should produce the same random number that was generated the first time execute() was called.  (TODO: The complexity of this description suggests that it might be a good idea to create a 'redo()' method for the CommandObject which defaults to 'execute()', but which can be overridden for special cases such as "InsertRandomNumber()" in which the reproducibility of the first call to 'execute()' is not guaranteed.  The RedoCommand() will then be modified so that it calls the redo() method of Command objects instead of the execute() method, and this bullet point will become a lot easier to explain.  It should also be noted that command scripts take care of this whole mess automatically, which is yet another one of their benefits.)

# --------------------------
# Module imports
# --------------------------

from commands.recording import execute_and_record_command
from commands import AbortCommandException as AbortException
from archy_state import archyState

# --------------------------
# API calls
# --------------------------

# This function inserts the given string at the current cursor position and selects it.
def insert_text(textString, styleString = None):
    cmd = archyState.commandMap.findSystemCommand( 'AddText')
    cmd.setinfo(textString, styleString)
    execute_and_record_command(cmd)

# This function deletes the current selection; it is equivalent to the user pressing the backspace key.
def delete_selection(addToDeletionsDocument = 1):
    cmd = archyState.commandMap.findSystemCommand( 'DeleteText' )
    cmd.setinfo(addToDeletionsDocument)
    execute_and_record_command(cmd)

# This function executes the command with the given name.  It is the equivalent of the user entering the command quasimode, typing the given string, and leaving the command quasimode.
def run_command(commandName):
# TO DO: Fix this when commandMap is worked out.
    cmd = archyState.commandMap.findCommand(commandName)
    execute_and_record_command(cmd)

# Executes a leap forward to the given target.
def leap_forward(target):
    cmd = archyState.commandMap.findSystemCommand( 'LEAP forward to:')
    cmd.setinfo(target)
    execute_and_record_command(cmd)

# Executes a leap backward to the given target.
def leap_backward(target):
    cmd = archyState.commandMap.findSystemCommand( 'LEAP backward to:' )
    cmd.setinfo(target)
    execute_and_record_command(cmd)

# Executes a creep forward to the given target.
def creep_forward():
    cmd = archyState.commandMap.findSystemCommand( 'CreepLeft')
    execute_and_record_command(cmd)

# Executes a creep backward to the given target.
def creep_backward():
    cmd = archyState.commandMap.findSystemCommand( 'CreepRight')
    execute_and_record_command(cmd)

# Acts like pressing both alt keys down: selects.
def select():
    cmd = archyState.commandMap.findSystemCommand( 'Select')
    execute_and_record_command(cmd)

# This function gets the named selection text.
def get_selection_text(selectionName):
    mT = archyState.mainText
    selRange = mT.getSelection(selectionName)
    return mT.getStyledText(*selRange)

# This function checks to see whether the selection is extended.
def is_selection_extended():
    mT = archyState.mainText
    return mT.isExtendedSelection()
    
# This function checks to see whether the named selection exists.
def selection_exists(selectionName):
    mT = archyState.mainText
    return mT.selectionExists(selectionName)
    
def get_selection(selectionName):
    mT = archyState.mainText
    return mT.getSelection(selectionName)

def set_selection(selectionName, start, end):
    cmd = archyState.commandMap.findSystemCommand( 'SetSelection')
    cmd.setinfo( selectionName, start, end)
    execute_and_record_command(cmd)

def get_cursor():
    mT = archyState.mainText
    return mT.getCursorPos()

def set_cursor(pos):
    cmd = archyState.commandMap.findSystemCommand( 'SetCursor')
    cmd.setinfo(pos)
    execute_and_record_command(cmd)
    
# Returns an n-tuple of selection end tuples 
def get_selection_list():
    mT = archyState.mainText
    return mT.copySelectionList()

# Sets Archy to reflect the given n-tuple of selection end tuples 

def set_selection_list(selections):
    cmd = archyState.commandMap.findSystemCommand( 'SetSelectionList')
    cmd.setinfo(selections)
    execute_and_record_command(cmd)

# Used for setting styling information
# TO DO: fix this dependency
def set_style(**styles):
    import commands.style_editing
    style = commands.style_editing.StyleCommand(**styles)
    execute_and_record_command(style)

# Gets the fonts available on the system
def get_available_fonts():
    import pygame_run
    fontList = pygame_run.get_fonts()
    fontList.sort()
    return map(lambda c:c.title(), fontList)

# Converts a color name to an RBG color
def color_name_to_color(color):
    import pygame_run
    return pygame_run.name_to_color(color)

# Returns a document character
def document_character():
    return '`'

# Returns a page character
def page_character():
    return '~'

# Displays a normal priority transparent message
def show_message(msg):
    import messages
    messages.queue(msg)