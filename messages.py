# messages.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# This module implements a message priority-queue. The queue keeps track of what messages get displayed when.
# There are three message priorities: instant, normal, and persistant.
# -  Instant messages appear as soon as they are queued and displace any other instant messages. This means that there is at most one instant message in the queue at any time.
# -  Normal messages appear in the order that they are queued. The next message gets displayed (if not in a quasimode) on the next key press.
# -  Persistant messages last until (and including) the next command-induced quasimode. This is useful for transparent messages that explain the selection schemes (like search and replace, and spellcheck).
# --- --- ---

from archy_state import archyState


class MessageQueue:
    def __init__(self):
        self.leap = ""
        self.command = ""
        self.instantList = []
        self.normalList = []
        self.persistantList = []

    def addInstantMessage(self, message):
        self.instantList.append(message)

    def addNormalMessage(self, message):
        self.normalList.append(message)
        
    def addPersistantMessage(self, message):
        self.persistantList = []
        self.persistantList.append(message)


messageQueue = MessageQueue()

def _makeVisible():
    archyState.quasiModeText.clear()
    archyState.quasiModeTextViewer.setVisibility(1)
    
def _makeInvisible():
    archyState.quasiModeText.clear()
    archyState.quasiModeTextViewer.setVisibility(0)

def display():
    global messageQueue
    
    _makeVisible()

    message = ''
    
    if messageQueue.leap <> '':
        message += messageQueue.leap
    elif len(messageQueue.persistantList) > 0:
        message += messageQueue.persistantList[0]

    if messageQueue.command <> '':
        message += messageQueue.command
    
    elif len(messageQueue.normalList) > 0:
        message += messageQueue.normalList[0]

    if len(messageQueue.instantList) > 0:
        message += messageQueue.instantList.pop(0)

    archyState.quasiModeText.addTextAtCursor(message)

def hide():
    global messageQueue

    _makeInvisible()

    if len(messageQueue.normalList) > 0:
        display()
        messageQueue.normalList.pop(0)

    if len(messageQueue.persistantList) > 0:
        display()
    
    

def unqueue(target = ''):
    global messageQueue

    if target == 'persistant':
        if len(messageQueue.persistantList) > 0:
            messageQueue.persistantList.pop(0)
            if messageQueue.leap == "":
                hide()

    if target == 'instant':
        messageQueue.instantList = []
    
    if target == 'normal':
        if len(messageQueue.normalList) > 0:
            messageQueue.normalList.pop(0)

    if target == 'leap':
        messageQueue.leap = ""
    
    if target == 'command':
        messageQueue.command = ""


def queue(message, priority = 'normal'):
    global messageQueue
    
    if   priority == 'instant':
        messageQueue.addInstantMessage(message)
        display()
    elif priority == 'normal':
        messageQueue.addNormalMessage(message)
        
    elif priority == 'persistant':
        message += '\n'
        messageQueue.addPersistantMessage(message)

    elif priority == 'leap':
        messageQueue.leap = message
        display()

    elif priority == 'command':
        messageQueue.command = message
        display()

        
def addToMessage(toAdd, target = ''):
    global messageQueue

    if target == 'leap':
        messageQueue.leap += toAdd
    
    if target == 'command':
        messageQueue.command += toAdd

    display()
    
def removeFromMessage(numToRemove, target = ''):
    global messageQueue
    
    if target == 'leap':
        messageQueue.leap = messageQueue.leap[:-numToRemove]
    
    if target == 'command':
        messageQueue.command = messageQueue.command[:-numToRemove]

    display()

