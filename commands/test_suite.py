# tutorial.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
import commands.save_and_load
from archy_state import archyState
import time
import archy_globals

import threading
import key 
import pygame

from tutorial import force_exit_event
from tutorial import is_running_event

# --- --- ------ --- ------ --- ------ --- ------ --- ------ --- ------ --- ---

TRANS_TABLE = {}
TRANS_TABLE['leapf']    = pygame.constants.K_RALT
TRANS_TABLE['leapb']    = pygame.constants.K_LALT
TRANS_TABLE['command']  = pygame.constants.K_CAPSLOCK
TRANS_TABLE['delete']   = pygame.constants.K_BACKSPACE
TRANS_TABLE['space']    = ' '
TRANS_TABLE['return']   = '\n'
TRANS_TABLE['left'] = pygame.constants.K_LEFT
TRANS_TABLE['right']    = pygame.constants.K_RIGHT
TRANS_TABLE['up']   = pygame.constants.K_UP
TRANS_TABLE['down'] = pygame.constants.K_DOWN
TRANS_TABLE['tab']  = '\t'

def translate(key_str):
    global TRANS_TABLE

    if len(key_str) > 1:
        return TRANS_TABLE[key_str]
    else:
        return key_str
def stop_tutorial():
    import time
    force_exit_event.set()
    while force_exit_event.isSet():
        time.sleep(0.01)

def is_tutorial_running():
    return is_running_event.isSet()
# --- --- ------ --- ------ --- ------ --- ------ --- ------ --- ------ --- ---

class Movie(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
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

    def blank(self, time):
        self.setHistory( time, ('blank') )

    def comparePoint(self, text, time):
        self.setHistory( time, ('compare',text, time) )

    def doCompare(self, text, time):
        import os
        try:
            log_file = open( os.path.join("commands", "test","test.log"), 'a' )
        except:
            log_file = open( os.path.join("commands", "test","test.log"), 'w' )
        newText, throwAwayStyles = archyState.mainText.getStyledText(0, len(text)-1 )
        if newText == text:
            log_file.write( "Time %s , successful compare.\n" % (time) )
        else:
            log_file.write("Bad compare at time %s ; Expected then predicted.\n" % (time) )
            log_file.write( text )
            log_file.write( newText )
        log_file.close()


    def doKey(self, keystroke, event):
        if type(keystroke) == int:
            keyValue = keystroke
            keystroke = ''
        else:
            keyValue = ord(keystroke)

        if event == "press":
            is_upper = archy_globals.apply_shift_key_to_character(keystroke) == keystroke
            if is_upper: 
                archyState.keyState.right_shift = 'down'
            
            archyState.keyState.keypress(keyValue, keystroke, "down")
            archyState.keyState.keypress(keyValue, keystroke, "up")

            if is_upper: 
                archyState.keyState.right_shift = 'up'
        elif event == "down" or event == "up":
            archyState.keyState.keypress(keyValue, keystroke, event)

    def doFunction(self, func):
        func()
    
    def onDone(self, func):
        self.onDoneFunc = func

    def doOnDone(self):
        self.onDoneFunc()

    def handle_tutorial_event(self, event):
        name = event[0]
        if name == 'key': self.doKey(event[1], event[2])
        elif name == 'function': self.doFunction(event[1])
        elif name == 'blank': pass
        elif name == 'compare': self.doCompare( event[1], event[2] )
        elif name == 'end': stop_tutorial()
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
        start_time = time.clock()
        elapsed_time = 0.0

        for t in times:
            force_exit_event.wait(t-elapsed_time)

            if force_exit_event.isSet():
                break
            event = self.history[t]

            import pygame_run
            pygame_run.post_tutorial_event(self, event)

            elapsed_time = time.clock() - start_time
        # end for

# At this point, either we've been told by the main Archy thread that we need to quit (meaning that the user has probably pressed a key in the middle of the tutorial), or we've run out of events to dispatch.   If the latter is the case, then we need to wait around for the main Archy thread to tell us to quit.

        force_exit_event.wait()

# At this point, our thread has exclusive control of Archy's state, since the main Archy thread is waiting for the force_exit_event event to be cleared.  Therefore, we must be certain to clear this event at the *very end* of this function, and no sooner--lest we give up our exclusive control of Archy's state and throw thread safety out the window.
        self.doOnDone()

        commands.save_and_load.saveState()

        is_running_event.clear()
        force_exit_event.clear()

class TestParser:
    DEFAULT_PRESS_LENGTH = 0.1

    def __init__(self, fileName):
        import os
        self.basePath = os.path.join('commands','test')

        text = open( os.path.join(self.basePath,fileName), 'r').read()
        text = text.split('%%')[1:]
        
        self.name   = text[0].split('=')[1].strip()
        self.title  = text[1].split('=')[1].strip()
        self.text   = text[2].split('=')[1].strip()
        self.script = text[3].split('\n')[1:]

        self.original_command_history_length = len(archyState.commandHistory._history)

        self.setupExample()
        movie = self.setupMovie()

        movie.start()
    
    def setupExample(self):
        textToAdd = self.text

        self.leap_1 = archyState.commandMap.findSystemCommand("LEAP backward to:")
        self.leap_1.setinfo( 12*'`' )
        self.leap_1.execute()
        
        self.add_text = archyState.commandMap.findSystemCommand("AddText")
        self.add_text.setinfo(textToAdd)
        self.add_text.execute()
        
        self.leap_2  = archyState.commandMap.findSystemCommand("LEAP backward to:")
        self.leap_2.setinfo( 12*'`' )
        self.leap_2.execute()
        

# ExampleParser.cleanupExample

# Delete all the test text and resets the command history to its original state.
# Move the cursor back to the original position by undoing the first leap. This may not refresh
# the Text viewer under certain conditions. So we will explictly refresh it. 
# Reconsider the encapsulation issues on the recenterOnCursor() call.

    def cleanupExample(self):
        archyState.commandMap.findCommand("CLEAR UNDO HISTORY").execute()

        mv = archyState.mainTextViewer
        mv.recenterOnCursor()
        
        import messages
        messages.queue('Test '+self.name+' Finished', 'instant')

    def setupMovie(self):
        movie = Movie()
        press_len = self.DEFAULT_PRESS_LENGTH
        
        for line in self.script:
            if line == '': continue
            time, info, evttype = line.split('\t')
            time = float(time)

            if   evttype in ['press', 'down', 'up']:
                key = translate(info)
                movie.key(key, evttype, time)
                if evttype == 'press': 
                    movie.key(key, '_unpress', time + press_len)

            elif evttype in ['command', 'meta']:
                if info == 'end':
                    movie.blank(time)
            
            elif info in ['press len']:
                press_len = float(evttype)
                
            elif evttype in ['compare']:
                movie.comparePoint( info, time )

        movie.onDone(self.cleanupExample)
        return movie

class Test1Command(commands.CommandObject):
    def name(self):
        return "TEST1"

    def execute(self):
        TestParser('test1.txt')

    def undo(self):
        pass

class TestAddTextCommand(commands.CommandObject):
    def name(self):
        return "TEST2"

    def execute(self):
        TestParser('add_text.test')

    def undo(self):
        pass



#COMMANDS = [Test1Command, TestAddTextCommand]
