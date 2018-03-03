# tutorial.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
import commands.save_and_load
from archy_state import archyState
import time
import messages
import keyboard
import archy_globals

import threading
import key 
import audio

global force_exit_event
force_exit_event = threading.Event()
force_exit_event.clear()
global is_running_event
is_running_event = threading.Event()
is_running_event.clear()

START_TAG = "`**- TUTORIAL START -**`"
END_TAG   = "`**- TUTORIAL END -**`"

# --- --- ---

def stop_tutorial():
    import time
    force_exit_event.set()
    while force_exit_event.isSet():
        time.sleep(0.01)

def is_tutorial_running():
    return is_running_event.isSet()

class Movie(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sound = audio.getSound('commands/tutorial/keyclick.wav')
        self.sound.set_volume(.1)
        self.history = {}

    def setHistory(self, time, event):
        while self.history.has_key(time):
            time = time + 0.001
        self.history[time] = event

    def key(self, key, event, time):
        self.setHistory( time, ('key', key, event) )

    def function(self, com, time):
        self.setHistory( time, ('function', com) )

    def end(self, time):
        self.setHistory( time, ('end',) )

    def movekeyboard(self, pos, time):
        self.setHistory( time, ('kb', pos) )

    def scroll(self, linesToScroll, time):
        self.setHistory( time, ('scroll', linesToScroll) )

    def doScroll(self, linesToScroll):
        scrollUp = linesToScroll > 0
        linesToScroll = abs(linesToScroll)
        up_key = keyboard.translate('up')
        down_key = keyboard.translate('down')

        for i in range(linesToScroll):
# Note: If we use archyState.mainTextViewer.scrollUp()/scrollDown() then Bad Things occur when UNDO commands are issued during a tutorial script. This is because the lines referred to in the command objects are not respected when they are changed via mainTextViewer.scrollUp method? Todo: Figure out why Bad Things happen (in particular in line 559 in text_viewer.py in renderLines: linePos = self.lineYPositions[line] we get
# KeyError: <line.Line instance at 0x011B40F8>
            if scrollUp:
                archyState.keyState.keypress(up_key, '', 'down')
                archyState.keyState.keypress(up_key, '', 'up')
            else:
                archyState.keyState.keypress(down_key, '', 'down')
                archyState.keyState.keypress(down_key, '', 'up')

    def doMoveKeyboard(self, pos):
        x, y = pos.split(',')
        keyboard.setKeyboardXPos(int(x))
        keyboard.setKeyboardYPos(int(y))

    def doKey(self, keystroke, event):
        keyboard.show(keystroke)

        if type(keystroke) == int:
            keyValue = keystroke
            keystroke = ''
        else:
            keyValue = ord(keystroke)

        if event == "press":
            is_upper = archy_globals.apply_shift_key_to_character(keystroke) == keystroke
            if is_upper: archyState.keyState.right_shift = 'down'

            self.sound.stop()
            self.sound.play()

            if keyboard.isModifier(keyValue):
                keyboard.addModifier(keyValue)

            archyState.keyState.keypress(keyValue, keystroke, "down")
            archyState.keyState.keypress(keyValue, keystroke, "up")

            if is_upper: archyState.keyState.right_shift = 'up'
        elif event == "_unpress":
            keyboard.show('')
            if keyboard.isModifier(keyValue):
                keyboard.unshowLeap()
        elif event == "show":
            keyboard.addModifier(keyValue)
        elif event == "unshow":
            keyboard.removeModifier(keyValue)
        elif event == "down" or event == "up":
            archyState.keyState.keypress(keyValue, keystroke, event)
            if event == "down":
                keyboard.addModifier(keyValue)
                self.sound.stop()
                self.sound.play()
            if event == "up":
                keyboard.removeModifier(keyValue)

    def doFunction(self, func):
        func()
    
    def onDone(self, func):
        self.onDoneFunc = func

    def doOnDone(self):
        self.onDoneFunc()

    def handle_tutorial_event(self, event):
        name = event[0]
        if name == 'key':
            self.doKey(event[1], event[2])
        elif name == 'function':
            self.doFunction(event[1])
        elif name == 'kb':
            self.doMoveKeyboard(event[1])
        elif name == 'scroll':
            self.doScroll(event[1])
        elif name == 'end':
            stop_tutorial()

    def start(self):

# Here we do some necessary things in the main Archy thread (required for thread safety) before spawning our new movie thread.

        force_exit_event.clear()
        is_running_event.set()

# We need to abort any special quasimode Archy may currently be in, since the movie expects us to be in a "standard" state of main text entry when it begins.

        archyState.keyState.abortCurrentQuasimode()

        threading.Thread.start(self)

    def run(self):
        times = self.history.keys()
        times.sort()
        start_time = time.time()
        elapsed_time = 0.0

        keyboard.show()

        for t in times:
            force_exit_event.wait(t-elapsed_time)

            if force_exit_event.isSet():
                break
            event = self.history[t]

            import pygame_run
            pygame_run.post_tutorial_event(self, event)

            elapsed_time = time.time() - start_time
        # end for

# At this point, either we've been told by the main Archy thread that we need to quit (meaning that the user has probably pressed a key in the middle of the tutorial), or we've run out of events to dispatch.   If the latter is the case, then we need to wait around for the main Archy thread to tell us to quit.

        force_exit_event.wait()

# At this point, our thread has exclusive control of Archy's state, since the main Archy thread is waiting for the force_exit_event event to be cleared.  Therefore, we must be certain to clear this event at the *very end* of this function, and no sooner--lest we give up our exclusive control of Archy's state and throw thread safety out the window.

        keyboard.hide()

        self.doOnDone()

        commands.save_and_load.saveState()

        is_running_event.clear()
        force_exit_event.clear()

def draw(screen):
    keyboard.render(screen)


class ExampleParser:
    def __init__(self, fileName):
        self.basePath = 'commands/tutorial/'

        text = open(self.basePath+fileName, 'r').read()
        text = text.split('%%')[1:]
        
        self.name   = text[0].split('=')[1].strip()
        self.sound  = text[1].split('=')[1].strip()
        self.title  = text[2].split('=')[1].strip()
        self.text   = text[3].split('=')[1].strip()
        self.boardPos   = text[4].split('=')[1].strip()
        self.script = text[5].splitlines()[1:]

        self.soundtrack = audio.getSound(self.basePath+self.sound)

        self.original_command_history_length = len(archyState.commandHistory._history)

        self.setupExample()
        self.movie = self.setupMovie()

# Actually runs the example.
    def execute(self):
        self.soundtrack.play()
        self.movie.start()

    def setupExample(self):
        manyReturns = '\n' * 30
        global START_TAG, END_TAG
        textToAdd = '%s%s\n%s\n\n%s%s%s' % (START_TAG, manyReturns, self.title, self.text, manyReturns, END_TAG)

        x, y = self.boardPos.split(',')
        keyboard.setKeyboardYPos(int(y))
        keyboard.setKeyboardXPos(int(x))

        self.start_leap = commands.cursor.LeapForwardCommand('`')
        self.start_leap.execute()
        commands.text_editing.AddTextCommand(textToAdd).execute()
        commands.cursor.LeapBackwardCommand(self.title).execute()
        commands.cursor.LeapForwardCommand("\n\n").execute()
        commands.cursor.CreepLeftCommand().execute()
        commands.text_editing.SelectCommand().execute()

        mv = archyState.mainTextViewer
        mv.recenterOnCursor()
        

# ExampleParser.cleanupExample

# Delete all the example text and resets the command history to its original state.
# Move the cursor back to the original position by undoing the first leap. This may not refresh
# the Text viewer under certain conditions. So we will explictly refresh it. Recentering the cursor is
# brute force and breaks encapsulation but we will deal with this later.
# [Todo:]

# Reconsider the encapsulation issues on the recenterOnCursor() call.

# Also, using globalState from here seems a violation of encapsulation.

    def cleanupExample(self):
        global START_TAG, END_TAG

        keyboard.resetModifiers()
        archyState.keyState.setToTextEntry()
        commands.cursor.LeapBackwardCommand(START_TAG).execute()
        commands.cursor.LeapForwardCommand(END_TAG).execute()
        for i in range(len(END_TAG)-1):
            commands.cursor.CreepRightCommand().execute()
        commands.text_editing.SelectCommand().execute()

        deleteCmd = commands.text_editing.DeleteTextCommand()
        deleteCmd.setinfo(useDeletionsDocument = 0)
        deleteCmd.execute()
        
        self.start_leap.undo()

        mv = archyState.mainTextViewer
        try:
            mv.recenterOnCursor()
        except:
            print "Thread Failure: Attempting to recenter the screen at an inappropriate time"
        self.soundtrack.stop()
        archyState.commandHistory._history = archyState.commandHistory._history[:self.original_command_history_length]
        archyState.commandHistory._lastCommandIndex = self.original_command_history_length-1

        messages.queue('Example '+self.name+' Finished', 'instant')

    DEFAULT_PRESS_LENGTH = 0.8

    def setupMovie(self):
        movie = Movie()
        press_len = self.DEFAULT_PRESS_LENGTH
        
        for line in self.script:
            if line == '': continue
            time, info, evttype = line.split('\t')
            time = float(time)

            if   evttype in ['press', 'down', 'up', 'show', 'unshow']:
                key = keyboard.translate(info)
                movie.key(key, evttype, time)
                if evttype == 'press': 
                    movie.key(key, '_unpress', time + press_len)

            elif evttype in ['command', 'meta']:
                if info == 'undo':
                    movie.function(commands.UndoCommand().execute, time)
                if info == 'end':
                    movie.end(time)

            elif info in ['kb']:
                pos = evttype
                movie.movekeyboard(pos, time)

            elif info in ['scroll']:
                linesToScroll = int(evttype)
                movie.scroll(linesToScroll, time)

            elif info in ['press len']:
                press_len = float(evttype)

        movie.onDone(self.cleanupExample)
        return movie


class LeapEx6Command(commands.CommandObject):
    def name(self):
        return "EX6"

    def execute(self):
        ExampleParser('ex6.txt').execute()

    def undo(self):
        pass

class LeapEx5Command(commands.CommandObject):
    def name(self):
        return "EX5"

    def execute(self):
        ExampleParser('ex5.txt').execute()

    def undo(self):
        pass

class LeapEx4Command(commands.CommandObject):
    def name(self):
        return "EX4"

    def execute(self):
        ExampleParser('ex4.txt').execute()

    def undo(self):
        pass

class LeapEx3Command(commands.CommandObject):
    def name(self):
        return "EX3"

    def execute(self):
        ExampleParser('ex3.txt').execute()

    def undo(self):
        pass

class LeapEx2Command(commands.CommandObject):
    def name(self):
        return "EX2"

    def execute(self):
        ExampleParser('ex2.txt').execute()

    def undo(self):
        pass

class LeapEx1Command(commands.CommandObject):
    def name(self):
        return "EX1"

    def execute(self):
        ExampleParser('ex1.txt').execute()

    def undo(self):
        pass

COMMANDS = []
BEHAVIORS = []
COMMANDS.append(LeapEx6Command)
COMMANDS.append(LeapEx5Command)
COMMANDS.append(LeapEx4Command)
COMMANDS.append(LeapEx3Command)
COMMANDS.append(LeapEx2Command)
COMMANDS.append(LeapEx1Command)


