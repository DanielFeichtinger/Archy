# commands/__init__.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# --------------------------
# An overview of the commands module
# --------------------------

# All user actions are represented by Command objects.

# Command objects have properties:

# - name()
# - recordable()

# Command objects have the methods:

# - execute()
# - undo()
# - redo()

# A commandMap holds all the commands that the user 
# can initiate. Command objects that are not in the 
# commandMap can be used from other parts of the system(including
# other command objects), but can not be run by the user from
# the command quasimode.

# The AddText and DeleteText are examples of Command objects that will
# be run from key.py but are not available to the command quasimode.

# The commandHistory holds a list of previously executed command objects.
# By calling commandHistory[last].undo() the last action can be undone.

# --------------------------
# The Command Object Abstract Class
# --------------------------

# Define the interface for a command object

class CommandObject:
    def __init__(self):
        pass

# Define the name of a command
    def name(self):
        print "CommandObject.name: An abstract CommandObject was created or"
        print "the name() method was not defined properly"
        print "for a command object"
        raise "error:CommandObject.name() was called"

    def __str__(self):
        className = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        name = self.name()
        return "%s (%s)" % (className, name)

    def recordable(self):
        #Should this default to the standard value of true? Almost all commands will be recordable... On the other hand, defaults are dangerous entities. I am worried, though, that if we do not have this default to the normally correct value, programming in Archy will start to seem like having to program in Java-- a lot of unnecessary house work that needs to be completed before one gets down to business.
        return True
        
    def stopBit(self):
        #This is used by the behaviorial section of the code. For consistency, because this function exists for behavior replacement commands it should exist here. This way one can always call commandInstance.stopBit() without worrying whether it is extant.
        return 0

    def clone(self):
        return self.__class__()

    def execute(self):
        print "CommandObject.execute: An abstract CommandObject was created or"
        print "the execute() method was not defined properly"
        print "for a command object"
        raise "error:CommandObject.execute() was called"

    def undo(self):
        print "CommandObject.undo: An abstract CommandObject was created or"
        print "the undo() method was not defined properly"
        print "for a command object"
        raise "error:CommandObject.undo() was called"

    def redo(self):
        self.execute()

#end class CommandObject






# --------------------------
# The Command Map
# --------------------------

# Command names that are registered with commandObject subclass instances through registerCommand() can be run from the command quasimode even without runnable modules in the text.    These commands form a core of primitives.

# An alternative design to consider when the "Programming in Archy" specifications are fully implemented is to define the core commands as modules in the same manner as the user defined commands. Even the core commands will be defined within the text of Archy rather than as outside files.

# The following function registers a Command object with the Command Map.

class CommandMap( dict ):
    def __init__(self, ArchyState = None):
        dict.__init__(self)
        self.registerHardCodedCommands()

    def registerHardCodedCommands( self ):
        for i in HARDCODED_COMMANDS:
            self.registerCommand( i() , 'user' )
        for i in HARDCODED_SYSTEM_COMMANDS:
            self.registerCommand( i() , 'system' )

    def registerCommand(self, cmd, type = 'user' ):
        commandName = cmd.name()
        if self.has_key(commandName):
            raise "Tried to register two different objects with same command name ="+commandName
        self[commandName] = { 'cmd': cmd, 'type': type }

    def unregisterCommand(self, cmd):
        commandName = cmd.name()
        if self.has_key(commandName):
            del self[commandName]

# TO DO: isCommand -> isUserCommand
    def isCommand(self, cmd):
        commandName = cmd.name()
        return self.has_key(commandName)            
    def isUserCommand(self, cmd):
        return ( self.has_key(commandName) and self[commandName]['type']=='user' )
    
# The following function returns an alphabetically sorted list of the names of Command objects currently registered with the Command Map.
    
    def commandList(self):
        toReturn = []
        for i in self.keys():
            if self[i]['type'] == 'user': toReturn.append(i)
# TO DO: these next two lines need to be revamped; we want to move this code into here directly.
        import commands.run
        toReturn.extend( commands.run.getUserCommandList() )
        toReturn.sort()
        return toReturn

# The following function attempts to find and return the Command object with the given name in the Command Map; if the Command object can't be found, a CommandNotFoundError exception is raised.

    def findCommand(self, commandText):
        if ( self.has_key(commandText) and self[commandText]['type'] == 'user' ):
            commandObject = self[commandText]['cmd']
            commandClone = commandObject.clone()
            return commandClone
        else:
# TO DO: these next two lines need to be revamped; we want to move this code into here directly.
            import commands.run
            userCommand = commands.run.UserCommandWrapper(commandText)
            try:
                userCommand.validateAndPrepare()
            except CommandNotFoundError:
                raise
            return userCommand
            
    def findSystemCommand(self, commandText):
        if self.has_key(commandText):
            commandObject = self[commandText]['cmd']
            commandClone = commandObject.clone()
            return commandClone
        else:
# TO DO: these next two lines need to be revamped; we want to move this code into here directly.
            import commands.run
            userCommand = commands.run.UserCommandWrapper(commandText)
            try:
                userCommand.validateAndPrepare()
            except CommandNotFoundError:
                raise
            return userCommand

# The following exception is thrown by findCommand() when it can't find a command.

class CommandNotFoundError(Exception):
    pass


# --------------------------
# The UNDO and REDO commands
# --------------------------

# The UndoCommand and RedoCommand must be defined here, apart from all the
# other commands. These commands must not be placed in the
# commandHistory. Since they must be referenced in functions defined here,
# it is best that they be defined within this module instead of imported.

class UndoCommand(CommandObject):
    def name(self):
        return "UNDO"
        
    def recordable(self):
        return 0

    def execute(self):
        from archy_state import archyState

        if 0 <= archyState.commandHistory._lastCommandIndex:
            archyState.commandHistory._history[archyState.commandHistory._lastCommandIndex].undo()
            archyState.commandHistory._lastCommandIndex = archyState.commandHistory._lastCommandIndex - 1
        else:
            raise AbortCommandException("Nothing to undo!")

    def undo(self):
        pass
#end class UndoCommand

class RedoCommand(CommandObject):
    def name(self):
        return "REDO"
        
    def recordable(self):
        return 0

    def execute(self):
        from archy_state import archyState

        if archyState.commandHistory._lastCommandIndex < len(archyState.commandHistory._history)-1:
            archyState.commandHistory._lastCommandIndex += 1
            archyState.commandHistory._history[archyState.commandHistory._lastCommandIndex].redo()
        else:
            raise AbortCommandException("Nothing to redo!")

    def undo(self):
        pass
#end class RedoCommand


class EmptyCommandHistory(CommandObject):
    def name(self):
        return "CLEAR UNDO HISTORY"
    
    def recordable(self):
        return 0
    
    def execute(self):
        from archy_state import archyState

        lastCommand = archyState.commandHistory._history[-1]
        archyState.commandHistory._history = [ lastCommand ]
        archyState.commandHistory._lastCommandIndex = 0





# --------------------------
# The commandHistory
# --------------------------

# The commandHistory is a "stack" of commands that were executed. Only those commands whose recordable() property returns true are recorded in the commandHistory. I.e., only those commands which are recordable are recorded.

# The last undo-able command is the last command that is added to the History.  This rule implies the following regarding undo and redo sequences:

# Suppose a user executes 4 commands. The commandHistory is [A, B, C, D] where A B C and D are the respective commands. The last command is D.

# If the user undo()es 3 commands D.undo(), C.undo, B.undo() the command history is now
# [A, B`, C`, D`] with the A being the last command. B` C` D` represent commands that were undo()ne and are redoable.

# The user redo()es B` and the command history is how [A, B, C` D`] with B being the last command.

# If at this point, the user executes command E, the history becomes [ A, B, E ]. The commands C` and D` are no longer redo()-able since the context where they occurred (after
# commands A and B) is no longer valid.

# A problem with this design is that once the command history becomes [A, B, E] it is impossible to revert to the state [A, B, C`, D`]. Alternative designs will be considered in the future.


class CommandHistory:
    def __init__(self, ArchyThread = None ):
        self._history = []
        self._lastCommandIndex = -1
        self._lastCommand = None
        self._lastLeapTarget = ""
# ============================================
# selectionAnchor
# Member that records the selection anchor. The anchor is set to the last position leaped or creeped to, or to the cursor position after a selection or deletion of an extended selection.
# This is used to in implementing the following:

# After a Leap or a Creep, user types new text. If user now presses both Leap 
# keys, the newly typed text (between the anchor point created by releasing the 
# Leap key and the last new character typed) should be selected. Use of 
# Backspace key during typing is irrelevant. Example: Leap to comma 
# after "here," type " we are", obtaining "here we are," press both Leap keys, 
# and selection (indicated by brackets) will be "here[ we are],".

# Now, if the user were to hit the delete key and type " they are" and press both Leap keys,
# the user should obtain "here[ they are],".
# =============================================
        self._selectionAnchor = 0
        
    def setSelectionAnchor(self,pos):
        self._selectionAnchor = pos
    
    def getSelectionAnchor(self):
        return self._selectionAnchor
        
# The following function adds the given command to the command history.
# If incrementalSave is false, then the command isn't registered as a change to Archy's state for the purposes of journaling/incremental saving--this should only happen when the journaling mechanism itself is calling this function.
    def addToHistory(self, command, incrementalSave=True):
        if incrementalSave and (command.recordable() or command.name() in ['UNDO', 'REDO']):
            import commands.save_and_load
            commands.save_and_load.logChange(command)

# Unrecordable commands should never be added into the history. For example, some commands which are not recordable are SAVE, LOAD, UNDO, and REDO.
        if not command.recordable():
            return

        #print "adding to history:", command.name()
        self._lastCommandIndex += 1
        self._history = self._history[0:self._lastCommandIndex]
        self._history.append(command)
        commandName = command.name()
        if commandName.startswith("LEAP forward to:") or commandName.startswith("LEAP backward to:"):
            try:
                self._lastLeapTarget = command._target
            except:
                #command was misnamed to look like a LEAP command
                pass


    def setLastCommand(self,command):
        import copy
        self._lastCommand = copy.copy(command)

# The following function attempts to execute the given Command object.  If that is successful, the Command object is added to the command history.
    def executeCommand(self, commandObject):
        commandObject.execute()
        self.addToHistory(commandObject)

    def getLastCommand(self):
        return self._lastCommand

    def repeatLastLeapForward(self):
        if self._lastLeapTarget <> "":
            from archy_state import archyState
            newLeap = archyState.commandMap.findSystemCommand("Repeat LEAP forward")
            newLeap.setinfo(self._lastLeapTarget)
            self.executeCommand(newLeap)
    
    def repeatLastLeapBackward(self):
        if self._lastLeapTarget <> "":
            from archy_state import archyState
            newLeap = archyState.commandMap.findSystemCommand("Repeat LEAP backward")
            newLeap.setinfo(self._lastLeapTarget)
            self.executeCommand(newLeap)


# --------------------------
# The AbortCommandException exception
# --------------------------

# The following exception should be thrown by any command that would like to "exit gracefully" when it encounters some condition that prevents it from proceeding.  For instance, the REDO command throws this exception when there is no command to redo.

# Raising an AbortCommandException should result in the following:

# (1) The command raising it should not be inserted into the command history; therefore, it cannot be undone or redone.

# (2) The explanation given to the exception's constructor should be displayed as a transparent message and inserted into the Messages Document.

class AbortCommandException(Exception):
    def __init__(self, explanation):
        Exception.__init__(self, explanation)
        self.explanation = explanation

    def getExplanation(self):
        return self.explanation

import os

HARDCODED_COMMANDS = [ UndoCommand, RedoCommand, EmptyCommandHistory ]
HARDCODED_BEHAVIORS = []
HARDCODED_SYSTEM_COMMANDS = []

# --------------------------
# Module initialization
# --------------------------

# This init function should be called before anything in this module is used.  It sets up the individual command sub-modules and registers the commands and behaviors contained in them.

def init():

# Get all files in the commands folder which end in '.py'...

    postfix = ".py"
    pythonFiles = [x for x in os.listdir('commands') if x[-len(postfix):]==postfix]
    del pythonFiles[pythonFiles.index('__init__.py')]

    modules = []
    for file in pythonFiles:
        modules.append( file[: - len(postfix) ] )
    modules.append('tutorial')

# Now import each of the command modules (and hence the commands)...

    for moduleName in modules:
        module = __import__(moduleName, globals())

        try:
            module.init()
        except AttributeError:
            pass

        try:
            HARDCODED_COMMANDS.extend( module.COMMANDS )
        except AttributeError:
            pass

        try:
            HARDCODED_BEHAVIORS.extend( module.BEHAVIORS )
        except AttributeError:
            pass

        try:
            HARDCODED_SYSTEM_COMMANDS.extend( module.SYSTEM_COMMANDS )
        except AttributeError:
            pass
