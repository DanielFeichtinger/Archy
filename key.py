# key.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: key.hpy,v 1.97 2005/04/04 17:08:08 bzwebcorp Exp $"

# This is the key.py function which handles individual keystrokes by the user and implements the state machine used to identify commands and other quasimodes in Archy.

# The keyboard module now (9/15/2004) relies on "keybindings" rather than a state machine.

# Advantages of this method:

# * It makes the code easier to read and understand, since
# the keybindings use Jef's keypress notation, the code is much closer
# to "plain english"; previously, the key.py file used a state machine
# with a lot of if-then statements which made it potentially difficult
# to figure out what was going on.  It also made it difficult for one
# state to simply "add on to" another state's behavior (e.g.,
# UppercaseTextEntry 'builds on' LowercaseTextEntry), which resulted in
# duplicate code.

# * In the state-based model, there was no way to inherit behavior from 
# another state, so certain states had to duplicate code from other 
# states; when said code was not duplicated, bugs occurred. As such, the 
# switch to keybindings has removed a number of bugs in the key module.

# * It does away with extraneous states; for instance, the old 
# UppercaseTextEntry state was just a "stepping stone" to the Leap states 
# and had no other functionality than to duplicate the 
# behavior of the LowercaseText state.

# * It makes the code easier to modify; whenever we want to add/change
# a keybinding (for instance, see Jef's discussion on trying out the Alt
# key as a 'shift' type key for the command quasimode), we can just add
# or change a keybinding in "plain english" (through the use of Jef's
# keypress notation) instead of dealing with if-then statements.

# * It will make it easier to define different keybinding
# "configuration files" for different keyboards--for instance, the
# standard keyboard vs. the LEAP keyboard.  If we wanted to, we could
# even define other configuration files for specific layouts of
# keyboards, although this could complicate things for the end-user.

# Disadvantages of this method:

# * The keyboard module isn't a state machine anymore, which in some
# ways could make things harder to debug if something goes wrong; you
# can't just look at one function/class method and know for a fact that
# it represents the exact state the keyboard module is in.

# * There's a certain amount of infrastructure that had to be added to
# support the parsing of strings like "left shift\ space\ space/" and
# the recording of keystrokes, which adds to the complexity of the code
# (although, in tradeoff, it reduces the complexity of the Quasimodes
# that actually assign the keybindings).



# --------------------------
# Module imports
# --------------------------

from archy_state import archyState
import messages
import commands
import archy_globals
import platform_specific

# We need traceback for the error handling.
import traceback

# --------------------------
# Keypress action constants
# --------------------------

# The following are keypress action constants and represent the type of key event that has occurred.

DOWN = 'down'
UP = 'up'

# Convert the pygame keycode into a notation similar to THI based upon the pygame.key.name() function.

def convertToNotation((keycode, downOrUp)):
    import pygame

    keyName = pygame.key.name(keycode)
    if downOrUp == 'up':
        keyAction = '/'
    else:
        keyAction = '\\'
    return keyName + keyAction

# --------------------------
# Text editing functions
# --------------------------

def addToText(unicodeString):
    command_object = archyState.commandMap.findSystemCommand( 'AddText')
    command_object.setinfo(unicodeString)
    archyState.commandHistory.executeCommand(command_object)
    mT = archyState.mainText
    selStart, selEnd = mT.getSelection('selection')
    mT.removeOverlappingOldSelections(selStart,selEnd)

def creepLeft():
    messages.hide()
    command_object = archyState.commandMap.findSystemCommand( 'CreepLeft' )
    archyState.commandHistory.executeCommand(command_object)

def creepRight():
    messages.hide()
    command_object = archyState.commandMap.findSystemCommand( 'CreepRight' )
    archyState.commandHistory.executeCommand(command_object)

def scrollUp():
    messages.hide()
    archyState.mainTextViewer.scrollUp()

def scrollDown():
    messages.hide()
    archyState.mainTextViewer.scrollDown()

def deleteText():
    messages.hide()
    command_object = commands.text_editing.DeleteTextCommand()
# TO DO: alter once thread structure is laid out; call
    #archyThread.commandHistory.executeCommand( command_object )
    archyState.commandHistory.executeCommand(command_object)

# --------------------------
# The Keybindings class
# --------------------------

# This is the base class for quasimodes of the key module.  It offers a simple mechanism for creating so-called "keybindings" in which some action is taken upon the completion of a user gesture.  The notation used for a keybinding is similar to Raskin's notation as outlined in the Archy spec (LEAP to "NOTATION OF KEYS").

class Keybindings:
    def __init__(self):
        self._bindings = {}

    def get_dict(self):
        return self._bindings

    def nullAction(self):
        pass

    def addKeybinding(self, keyStr, action):
        if action == None:
            action = self.nullAction
        self._bindings[keyStr] = action

    def removeKeybinding(self, keyStr):
        if keyStr in self._bindings:
            del self._bindings[keyStr]


# --------------------------
# KeyboardState
# --------------------------

# A KeyboardState class represents an the state of the keyboard.The state of the keyboard can be ordinary text entry, leap quasimode or command quasimode, where either leap or command keys are pressed down while typing. See THI pp. 55 for a definition of a quasimode.

# The KeyboardState class has-A set of keyBindings.  Changed from a inheritence relationship between KeyboardState and Keybindings to a object composition relationship.

class KeyboardState:
    """This base abstract class represents a particular quasimode
    for Archy."""

    def __init__(self, parent):
        self.parent = parent
        self.current_keybindings = Keybindings()
        self.createKeybindings(self.current_keybindings)

    def createKeybindings(self, keybindings_dict):
        raise NotImplementedError()

    def onEnter(self):
        pass

    def onExit(self):
        pass

    def onAbort(self):
        self.onExit()
    
    def keypress(self, keycode, unicode, action):
        """This is the main method for a Quasimode object;
        whenever a key event occurs and Archy is in this
        quasimode, this method is called."""

        raise NotImplementedError()

    def tryKeybinding(self, keyStr):
        keybindings_dict = self.current_keybindings.get_dict()
        if keybindings_dict.has_key(keyStr):
            action = keybindings_dict[keyStr]
            action()
            return 1
        return 0

# --- --- ---
# A Note on Defining the bindings for a KeyBindings class and KeyboardState classes
# Han Kim Oct 7 2004

# The addKeyBindings must be executed for each KeyboardState object when
# it is created for a keystroke sequence to be associated with a function call. 

# It is important to remember that in Python even the 
# __init__(self) methods are virtual methods. So the base class's __init__
# does not automatically get called as in the case of C++ constructors.

# Here is an error I had made :

# LeapBase is the base class of LeapForward and LeapBackward. I had put a call to 
# addKeyBindings("backspace\\", self.delete) in LeapBase.createKeybindings(), expecting
# the LeapForward and LeapBackward to somehow call the LeapBase.createKeybindings() 
# when either LeapForward.createKeybindings() or LeapBackward.createKeyBindings()
# are called. However, the design as of Oct 7 2004 requires that each object define
# ALL of its keybindings in its createKeybindings() method.

# It may be worth a discussion whether the KeyboardState.__init__() function should
# be modified so that the .createKeybindings() of the parents should also be called.
# That way, base class keybindings can be truly inherited.

# Addendum: The LeapForward and LeapBackward classes now manually call their parent class' createKeybindings() method.

# --------------------------
# The Main Text Entry Quasimode
# --------------------------

# This function sets up keybindings for editing text

def createTextEditBindings(keybindings_dict):
    keybindings_dict.addKeybinding(platform_specific.Delete_Keybinding, deleteText)
    keybindings_dict.addKeybinding(platform_specific.Creep_Left_Keybinding, creepLeft)
    keybindings_dict.addKeybinding(platform_specific.Creep_Right_Keybinding, creepRight)
    keybindings_dict.addKeybinding('up\\', scrollUp)
    keybindings_dict.addKeybinding('down\\', scrollDown)


class MainTextEntry(KeyboardState):
    """Quasimode for normal text entry. This is the base, default
    quasimode that Archy starts out in."""

# By not defining the __init__ function, KeyboardState.__init__ will be inherited and called.
# In KeyboardState.__init__ the self.createKeyBindings() is called.
# [][][This seems too much of a hack and should be changed to an __init__() that calls
# the parent's __init__() -Han]

    def setCommandQuasimode(self):
        self.parent.setQuasimode(CommandEntry(self.parent))

    def setLeapForward(self):
        self.parent.setQuasimode(LeapForward(self.parent))

    def setLeapBackward(self):
        self.parent.setQuasimode(LeapBackward(self.parent))

    def createKeybindings(self, keybindings_dict):
        createTextEditBindings(keybindings_dict)
        keybindings_dict.addKeybinding(platform_specific.Start_Command_Keybinding, self.setCommandQuasimode)
        keybindings_dict.addKeybinding(platform_specific.Start_LEAP_Forward_Keybinding, self.setLeapForward)
        keybindings_dict.addKeybinding(platform_specific.Start_LEAP_Backward_Keybinding, self.setLeapBackward)


    def keypress(self, keycode, char, upDown):
        self.parent.addToMainText(keycode, char, upDown)


# --------------------------
# The Command Entry Quasimode
# --------------------------

class CommandEntry(KeyboardState):

    def lastLeapBackward(self):
        try:
            archyState.commandHistory.repeatLastLeapBackward()
        except commands.AbortCommandException, e:
            messages.hide()
            messages.queue("%s: %s" % ("LEAP backward again", e.getExplanation()))
            messages.display()
    def lastLeapForward(self):
        try:
            archyState.commandHistory.repeatLastLeapForward()
        except commands.AbortCommandException, e:
            messages.hide()
            messages.queue("%s: %s" % ("LEAP Forward again", e.getExplanation()))
            messages.display()

    def onEnter(self):
        self.parent.showWhitespace()
        self.parent.showPreselection()
        
        message = ''
        if archyState.commandHistory._lastCommand <> None:
            message += 'Last Command: '+ archyState.commandHistory._lastCommand.name() + '\n'
        message += 'Command\n'
        messages.queue(message, 'command')
        self.commandText = ''
        self.suggestText = ''

        import platform_specific
        suggestStyle = platform_specific.Quasimode_Font
        suggestStyle['foregroundColor'] = 90,90,0
        suggestStyle['outline'] = 0
        pool = archyState.stylePool
        self.suggestStyle = pool.newStyle(**suggestStyle)

    def createKeybindings(self,keybindings_dict):
        keybindings_dict.addKeybinding(platform_specific.End_Command_Keybinding, self.leaveQuasimode)
        keybindings_dict.addKeybinding(platform_specific.Delete_Keybinding, self.deleteChar)

    def _executeCommand(self, command, clearDisplay):
        try:
            archyState.commandHistory.executeCommand(command)
            if clearDisplay:
                messages.hide()
        except SystemExit:
            raise
        except commands.AbortCommandException, e:
            messages.hide()
            messages.queue("%s: %s" % (command.name(), e.getExplanation()))
            messages.display()
        except:
            import debug

            error_name = "Command %s did not run properly." % command.name()
            print error_name
            tb_info = debug.get_traceback()
            debug.report_bug(error_name, tb_info)

            messages.hide()
            messages.queue(error_name)
            messages.display()

    def runCommand(self, command):
        commands.save_and_load.saveChanges()
        self._executeCommand(command, clearDisplay=1)
        archyState.commandHistory.setLastCommand(command)

    def runLastCommand(self):
        lastCommand = archyState.commandHistory.getLastCommand()
        if lastCommand == None:
            return
        if lastCommand.name()[:4] == "LEAP":
            if lastCommand.name()[5:13] == 'backward':
                command = archyState.commandMap.findSystemCommand( "Repeat LEAP backward" )
                command.setinfo( lastCommand._target )
            elif lastCommand.name()[5:12] == 'forward':
                command = archyState.commandMap.findSystemCommand( "Repeat LEAP forward" )
                command.setinfo( lastCommand._target )
            else:
                command = lastCommand.clone()
        else:
            command = lastCommand.clone()
        self._executeCommand(command, clearDisplay=0)

    def deleteChar(self):
        if len(self.commandText) == 0:
            self.suggestText = ''
            return
        self.commandText = self.commandText[:-1]
        
        self._removeSuggestion()
        messages.removeFromMessage(1, 'command')
        self._addSuggestion()
        

# When we leave the CommandEntry quasimode, we will try to run what the user typed while in the quasimode as a command. If it does not work, print a message.
# If it finds it and is successful, then set the globalState's LastCommand.

    def onAbort(self):
        self.parent.hideWhitespace()
        self.parent.hidePreselection()
        messages.unqueue('command')
        messages.hide()

    def onExit(self):
        self.onAbort()

        commandName = self.commandText+self.suggestText
        if commandName == '':
            return
        try:
            command_object = archyState.commandMap.findCommand(commandName)
        except commands.CommandNotFoundError:
            messages.queue("Command %s not found" % commandName, 'instant')
            return

        self.runCommand(command_object)

    def leaveQuasimode(self):
        self.parent.setQuasimode(MainTextEntry(self.parent))

    def _addSuggestion(self):
        if self.commandText == '':
            self.suggestText = ''
            return
        start_code = '-'

        command_list = archyState.commandMap.commandList()

        #Force REDO and UNDO to autocomplete before anything else that begins with U or R.
        u_commands = map(lambda c: c[0] == 'U', command_list)
        u_index = u_commands.index(True)
        command_list.insert(u_index, 'UNDO')

        r_commands = map(lambda c: c[0] == 'R', command_list)
        r_index = r_commands.index(True)
        command_list.insert(r_index, 'REDO')
        
        command_list = start_code+start_code.join(command_list)
        found = command_list.find(start_code+self.commandText)
        if found >= 0:
            self.suggestText = command_list[found+1:].split(start_code)[0][len(self.commandText):]
        else:
            self.suggestText = ""

        messages.addToMessage( self.suggestText, 'command' )
        textLength = archyState.quasiModeText.styleArray.getLength()
        archyState.quasiModeText.styleArray.setStyleInRange(self.suggestStyle, textLength-len(self.suggestText), textLength)

    def _removeSuggestion(self):
        if self.suggestText <> '':
            messages.removeFromMessage(len(self.suggestText), 'command')

    def keypress(self, keycode, unicode, downOrUp):
        import pygame
        if downOrUp == DOWN:
            if len(self.commandText) < 1:
                if keycode in [ord('\n'), ord('\r')]:
                    self.runLastCommand()
                    return
                else:
                    keystroke = convertToNotation( (keycode,downOrUp) )
                    if keystroke == platform_specific.Start_LEAP_Forward_Keybinding:
                        self.lastLeapForward()
                        return
                    if keystroke == platform_specific.Start_LEAP_Backward_Keybinding:
                        self.lastLeapBackward()
                        return
            upper_char_code = unichr(keycode).upper()
            self.commandText += upper_char_code
            
            self._removeSuggestion()
            messages.addToMessage( upper_char_code, 'command' )
            self._addSuggestion()

# --------------------------
# The LEAP Quasimodes
# --------------------------

class LeapBase(KeyboardState):
    """Base abstract class for leaping forwards or backwards."""

    FAILED_LEAP_SOUND_FILE = 'fail.wav'

    def playFailedLeapSound(self):
        import audio
        sound = audio.getSound(self.FAILED_LEAP_SOUND_FILE)
        sound.play()

    def onEnter(self):
        self.parent.showWhitespace()
        self.parent.showPreselection()
        self.origViewMemento = archyState.mainTextViewer.getViewMemento()
        self.doInit()
# Now that left and right shifts are dealt with independently the backspace keybinding must be set in both LeapForward's and LeapBackward's implementation of createKeybindings

    def createKeybindings(self, keybindings_dict):
        #print "LeapBase.createKeyBindings"
        keybindings_dict.addKeybinding(platform_specific.Delete_Keybinding, self.deleteChar)
        keybindings_dict.addKeybinding("tab\\", self.leaveQuasimode)

    def restoreViewSettings(self):
        archyState.mainTextViewer.setViewInformation(self.origViewMemento)

    def onExit(self):
        self.parent.hideWhitespace()
        self.parent.hidePreselection()
        messages.unqueue('leap')
        messages.hide()
        if self.leapCommand.status() == 1:
            archyState.commandHistory.addToHistory(self.leapCommand)
            archyState.commandHistory.setLastCommand(self.leapCommand)
        else:
            self.restoreViewSettings()
            if  self.leapCommand.status() == 0:
                pass
            else:
                messages.queue(self.info, 'instant')
                self.playFailedLeapSound()

    def leaveQuasimode(self):
        self.parent.setQuasimode(MainTextEntry(self.parent))

    def selectText(self):
        selectCmd = archyState.commandMap.findSystemCommand( 'Select' )
        archyState.commandHistory.executeCommand(selectCmd)
        self.leaveQuasimode()

# Why do we have a leaveQuasimodeAndSelect method? Because if we did not (and for a while we didn't) then a leap-select gesture (if the keystrokes were similar to LeapForward\ a\/ b\/ c\/ LeapBack\/ LeapForward/) would insert the leap and select commands into the command history in the wrong order-- the select would come before the leap. This caused a lot of trouble, especially because the UNDOs would seem right but then the REDOs would be totally wrong.

    def leaveQuasimodeAndSelect(self):
        self.leaveQuasimode()
        self.selectText()

    def deleteChar(self):
        if self.leapCommand.status() == 0:
            self.playFailedLeapSound()
        else:
            messages.removeFromMessage(1, 'leap')
            try:
                self.leapCommand.delChar()
                if self.leapCommand.status() == 0:
                    # If the target becomes length 0 then return to the original view.
                    self.restoreViewSettings()
            except commands.AbortCommandException, e:
                self.info = e.getExplanation()
                self.restoreViewSettings()
                self.playFailedLeapSound()

    def keypress(self, keycode, unicode, action):
        unicode_from_key = unichr(keycode)
        if action == DOWN:
            if unicode_from_key == u"":
                return
            if self.parent.left_shift == DOWN or self.parent.right_shift == DOWN:
                unicode_from_key = archy_globals.apply_shift_key_to_character(unicode_from_key)

            messages.addToMessage(unicode_from_key, 'leap')
            try:
                self.leapCommand.addChar(unicode_from_key)
                if self.leapCommand.status() == 0:
                    # I do not think an addChar can result in a 0 length target but
                    # it will not hurt to check here. -Han
                    self.restoreViewSettings()
            except commands.AbortCommandException, e:
                self.info = e.getExplanation()
                self.restoreViewSettings()
                self.playFailedLeapSound()

    def doInit(self):
        """Template method for initializing the leap quasimode."""
        raise NotImplementedError()


#end class LeapBase

class LeapForward(LeapBase):
    """Concrete leap quasimode for leaping forward."""
    
    def doInit(self):
        messages.queue('Leap Forward\n', 'leap')
        self.leapCommand = archyState.commandMap.findSystemCommand( 'LEAP forward to:' )
        try:
            archyState.commandHistory.executeCommand(self.leapCommand)
        except commands.AbortCommandException:
            pass

    def createKeybindings(self,keybindings_dict):
        #print "LeapForward.createKeyBindings"
        LeapBase.createKeybindings(self,keybindings_dict)
        keybindings_dict.addKeybinding(platform_specific.End_LEAP_Forward_Keybinding, self.leaveQuasimode)
        keybindings_dict.addKeybinding(platform_specific.LEAP_Forward_Select_Keybinding, self.leaveQuasimodeAndSelect)

class LeapBackward(LeapBase):
    """Concrete leap quasimode for leaping backward."""
    
    def doInit(self):
        messages.queue('Leap Backward\n', 'leap')
        self.leapCommand = archyState.commandMap.findSystemCommand( 'LEAP backward to:' )
        try:
            archyState.commandHistory.executeCommand(self.leapCommand)
        except commands.AbortCommandException:
            pass
        
    def createKeybindings(self,keybindings_dict):
        #print "LeapBackward.createKeyBindings"
        LeapBase.createKeybindings(self,keybindings_dict)
        keybindings_dict.addKeybinding(platform_specific.End_LEAP_Backward_Keybinding, self.leaveQuasimode)
        keybindings_dict.addKeybinding(platform_specific.LEAP_Backward_Select_Keybinding, self.leaveQuasimodeAndSelect)

# --------------------------
# The keystroke recorder
# --------------------------

# The keystroke recorder records keypresses and creates from them a sequence which can be represented in the same notation as the one used for keybindings in the Keybindings class and the Archy spec (LEAP to "NOTATION OF KEYS" in the spec).    It can then match the key sequence the user has entered to any keybinding in a given quasimode, and will execute the keybinding's action if a match occurs.

class KeyRecorder:

# MAX_PRESSES is a constant that defines the length of the key recorder's recording buffer, in keystrokes.  For instance, the keystroke sequence "Shift\ Space\ Space/ Shift/" has a keystroke length of 4.

    MAX_PRESSES = 5

    def __init__(self):
        self._presses = []

    def record(self, keycode, downOrUp):
        if len(self._presses) == self.MAX_PRESSES:
            self._presses.pop(0)
        self._presses.append((keycode, downOrUp))

    def matchKeybinding(self, currentQuasimode):
        matchStart = 0
        lenOfPresses = len(self._presses)

        while matchStart < lenOfPresses:

# Build the match string self._presses[matchStart : length of presses ]
# Check if it matches any of the current Quasimode state's bindings

            matchString = ""
            for i in range(matchStart,lenOfPresses):
                key_and_direction = self._presses[i]
                key_name = convertToNotation(key_and_direction)
                if i > matchStart:
                    key_name = ' '+ key_name
                matchString = matchString + key_name
            #now matchString = str( self._presses[matchStart:])
            #print "matchString="+matchString
            if currentQuasimode.tryKeybinding(matchString):
                return 1

            matchStart = matchStart + 1
        return 0

# --------------------------
# Global state singleton
# --------------------------

# This class encapsulates the state of the keyboard for Archy.

# A note on shift keys and CAPS lock problems:

# Han Kim Oct 18 2004
# Updated by Atul Varma - Nov 12 2004

# Archy is now "immune" to the modality of the Caps Lock key.   This was achieved in the following way:

# (1) Any alphabetic keys that arrive are always converted to their lower-case representations. This way, even if Caps Lock is active or a Shift key is held down, the character Archy receives is always lowercase.

# (2) Whenever a shift key is pressed or depressed, the key.globalState object sets its left_shift or right_shift property to UP or DOWN.

# (3) Any active QuasiMode can examine these properties of the globalState to determine whether it wants to make the character uppercase or not.    For instance, MainTextEntry now has code that detects whether one of the shift keys is pressed; if so, it inserts an uppercase version of the character entered.

# It should also be noted that the LED of the Caps Lock key will operate independently of Archy on some keyboards (the modified SDL.dll accesses the keyboard in exclusive mode which prevents the operating-system-wide caps lock state from being modified on many keyboards, but not all).   Eventually, we will try to find some kind of solution that allows Archy to restore the original OS-wide-state of the caps lock key when it is switched out to another application, so that when a user uses Caps Lock as their command quasimode key, they won't their caps lock mode activated, to their annoyance, when they switch applications.

class GlobalState:
    """This singleton represents the current state of the key
    module, and controls various keyboard properties that aren't
    specific to particular quasimodes--for instance, the keyboard
    auto-repeat settings."""

    def __init__(self):
        self.quasimode = None
        self.keyRecorder = KeyRecorder()
        self.left_shift = UP
        self.right_shift = UP

    def start(self):
        print "about to set quasimode to main text entry"
        self.setQuasimode(MainTextEntry(self))
        messages.hide()

    def abortCurrentQuasimode(self):
        if self.quasimode != None:
            self.quasimode.onAbort()
        self.quasimode = None
        self.setQuasimode(MainTextEntry(self))
        
    def setQuasimode(self, quasimode):
        """Sets the current Archy quasimode to the given
        Quasimode instance."""
        if self.quasimode != None:
            self.quasimode.onExit()
        self.quasimode = quasimode
        self.quasimode.onEnter()

    def keypress(self, keycode, unicode, downOrUp):
        """Method called whenever a key is pressed in Archy."""
        unicode = archy_globals.remove_shift_key_from_character(unicode)

        self.keyRecorder.record(keycode, downOrUp)

        import pygame
        if keycode == pygame.constants.K_LSHIFT:
            self.left_shift = downOrUp
        elif keycode == pygame.constants.K_RSHIFT:
            self.right_shift = downOrUp

        if not self.keyRecorder.matchKeybinding(self.quasimode):
            #print "GlobalState.keypress:unicode=", unicode, downOrUp
            self.quasimode.keypress(keycode, unicode, downOrUp)

    def setToTextEntry(self):
        self.setQuasimode(MainTextEntry(self))

    def showWhitespace(self):
        archyState.showWhitespace()

    def hideWhitespace(self):
        archyState.hideWhitespace()

    def showPreselection(self):
        archyState.showPreselection()

    def hidePreselection(self):
        archyState.hidePreselection()

    def addToMainText(self, keycode, char, upDown):
        if upDown == DOWN:
            messages.hide()
            if char != "":
                if self.left_shift == DOWN or self.right_shift == DOWN:
                    char = archy_globals.apply_shift_key_to_character(char)
                addToText(char)
