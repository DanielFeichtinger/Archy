# recording.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# This module provides an interface for recording executed Command objects for the purpose of being able to easily undo their changes.

# The primary purpose of this module is to facilitate the development of an API for Archy, although it can certainly be used by other code as well.

# --------------------------
# Global variables
# --------------------------

# This is a stack that keeps track of lists of recorded commands.  Whenever a new recording begins, a new list is pushed onto the stack; whenever the current recording ends, the list is popped off the stack.  Thus the stack only has more than one element in it when a command list is being recorded "inside" the recording of another command list.

__commandRecording = []

# --------------------------
# Recording functions
# --------------------------

# This function starts the recording of a new command list.

def start_recording():
    __commandRecording.append([])

# This function aborts the recording of a new command list and undoes whatever has been recorded so far.

def rollback_recording():
    commandList = stop_recording()
    commandList.undo()

# This function stops the recording of the current command list and returns a RecordedCommandList object that can be used to undo the effects of the recorded commands.

def stop_recording():
    return RecordedCommandList(__commandRecording.pop())

# This function executes the given command and records it.

def execute_and_record_command(command):
    command.execute()
    __commandRecording[-1].insert(0, command)

# --------------------------
# RecordedCommandList class
# --------------------------

# This simple class just encapsulates a list of previously executed Command objects with functionality that undoes the effects of the Command objects.

class RecordedCommandList:
    def __init__(self, commandList):
        self.commandList = commandList

    def redo(self):
        for i in range(len(self.commandList)-1, -1, -1):
            self.commandList[i].execute()

    def undo(self):
        for command in self.commandList:
            command.undo()
