# spellcheck.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# --------------------------
# Module imports
# --------------------------

import commands
from archy_state import archyState

import behavior_editing

import messages

import behavior

# --- --- ---

# --------------------------
# Abstract spell-checking interface and related functions
# --------------------------

# The following class defines an abstract Archy interface for spell-checking.  Implementations of this interface may use a variety of spell-checking mechanisms, whether they be provided via external library, internet, or implemented "from scratch".

class AbstractSpellChecker:

# The following method takes a single misspelled word and returns a python list containing suggestions of proper spellings for the word.

    def suggest(self, word):
        raise NotImplementedError()

# The following method adds the given word to the spellchecker's dictionary.

    def addToDictionary(self, word):
        raise NotImplementedError()

# The following method returns true if the given word exists in the spellchecker's dictionary, false otherwise.

    def check(self, word):
        raise NotImplementedError()

# The following function returns an instance of an object that implements the methods defined by AbstractSpellChecker.

# NOTE: for now, we just return a spell checker for the Win32 ASpell library, since that's the only implementation we have.  In the future, we may add other spell-checking interfaces, at which point this function should be changed (and we should probably add a new function called setSpellChecker()).

def getSpellChecker():
    import aspell
    return aspell.ASpellSpellChecker()

# --------------------------
# Spellcheck-related commands
# --------------------------

class SpellcheckStyle(behavior.StyleCommand):
    def behaviorName(self):
        return "SPELLCHECK"

    def execute(self):
        pass
        
        
class SpellcheckModify(behavior.AddCommand):
    def behaviorName(self):
        return "SPELLCHECK"

    def execute(self):
        mT = archyState.mainText
        spRange = self.findExtent(mT)

        oldSel = mT.getSelection('selection')

        mT.setSelection('selection', *spRange)
        self.removeSP = RemoveSpellcheckCommand()
        self.removeSP.execute()
        messages.unqueue('persistant')

        mT.setSelection('selection', *oldSel)

    def undo(self):
        self.removeSP.undo()
    

class SpellcheckFocus(behavior.FocusCommand):
    def behaviorName(self):
        return "SPELLCHECK"

    def execute(self):
        mT = archyState.mainText
    
        storage = self.getStorage(archyState.mainText)
        if not storage:
            return

        word = storage.getWord()
        
        if storage.getSuggestions() <> []:
            suggestions = storage.getSuggestions()
        else:
            c = getSpellChecker()
            suggestions = c.suggest(word.lower())[:8]
            storage.setSuggestions(suggestions)

        
        suggestions = filter(lambda c:c[0].islower(), suggestions)[:8]

        if word[0].isupper():
            suggestions = map(lambda w:w.title(), suggestions)

        numberedSuggestions = zip(range(1, len(suggestions)+1), suggestions)
        
        for num, sug in numberedSuggestions:
            replaceCommand = AbstractReplaceCommand()
            
            replaceCommand.setName(num)
            replaceCommand.setSuggestion(sug)
            replaceCommand.setRange( self.findExtent(mT) )
            
            archyState.commandMap.unregisterCommand(replaceCommand)
            archyState.commandMap.registerCommand(replaceCommand)
        
        replaceCommand = AbstractReplaceCommand()   
        replaceCommand.setName("K")
        replaceCommand.setSuggestion(word)
        replaceCommand.setRange( self.findExtent(mT) )
            
        archyState.commandMap.unregisterCommand(replaceCommand)
        archyState.commandMap.registerCommand(replaceCommand)
        
        learnCommand = AbstractLearnCommand()
        learnCommand.setName("LEARN")
        learnCommand.setWord(word)
        learnCommand.setWordRange( self.findExtent(mT) )

        archyState.commandMap.unregisterCommand(learnCommand)
        archyState.commandMap.registerCommand(learnCommand)

        message = ' '.join(map(lambda ns:'%s-%s' % (ns[0], ns[1]), numberedSuggestions))
        message += '\n%s - %s' % ("K", "Keeps the word")
        message += '\n%s - %s' % ("LEARN", "Learns word")
        messages.queue(message, 'persistant')
        messages.display()

class SpellcheckUnfocus(behavior.UnfocusCommand):
    def behaviorName(self):
        return "SPELLCHECK"

    def execute(self):
        messages.unqueue('persistant')

class SpellcheckStorage:
    def __init__(self):
        self.word = ""
        self.suggestions = []

    def behaviorName(self):
        return "SPELLCHECK"

    def setWord(self, word):
        self.word = word
    
    def getWord(self):
        return self.word

    def setSuggestions(self, suggestions):
        self.suggestions = suggestions

    def getSuggestions(self):
        return self.suggestions


class AbstractLearnCommand(commands.CommandObject):
    cmdName = ''
    word = ''
    wordRange = []

    def clone(self):
        clonedCommand = AbstractLearnCommand()
        clonedCommand.cmdName = self.cmdName
        clonedCommand.word = self.word
        clonedCommand.wordRange = self.wordRange
        return clonedCommand

    def name(self):
        return self.cmdName

    def setName(self, name):
        self.cmdName = str(name)

    def setWord(self, word):
        self.word = word

    def setWordRange(self, wordRange):
        self.wordRange = wordRange

    def execute(self):
        c = getSpellChecker()
        c.addToDictionary(self.word)

        mT = archyState.mainText
        oldSel = mT.getSelection('selection')
        mT.setSelection('selection', *self.wordRange)
        
        self.removeSP = RemoveSpellcheckCommand()
        self.removeSP.execute()

        mT.setSelection('selection', *oldSel)

        
        foundNext = 0
        pos = mT.getCursorPos()
        start = pos

        while not foundNext and pos < mT.getLength() and abs(pos-start)<2000:
            if mT.behaviorArray.hasAction("SPELLCHECK", pos):
                foundNext = 1
            else:
                pos += 1
        
        messages.unqueue('persistant')

        if foundNext <> 0:
            mT.setCursor(pos)
            mT.setSelection('selection', mT.cursorPosInText)
            messages.display()

    def undo(self):
        self.removeSP.undo()


class AbstractReplaceCommand(commands.CommandObject):
    cmdName = ''
    suggestion = ''
    wordRange = []
    
    def clone(self):
        clonedCommand = AbstractReplaceCommand()
        clonedCommand.suggestion = self.suggestion
        clonedCommand.wordRange = self.wordRange
        return clonedCommand
        
    def name(self):
        return self.cmdName
        
    def setName(self, name):
        self.cmdName = str(name)
        
    def setSuggestion(self, sug):
        self.suggestion = sug
        
    def setRange(self, theRange):
        self.wordRange = theRange
        
    def execute(self):
        mT = archyState.mainText
        mT.setSelection('selection', *self.wordRange)
        
        self.removeSpellcheck = RemoveSpellcheckCommand()
        self.delText = archyState.commandMap.findSystemCommand("DeleteText")
        self.addText = archyState.commandMap.findSystemCommand("AddText")
        self.addText.setinfo(self.suggestion)

        self.removeSpellcheck.execute()
        self.delText.execute()
        self.addText.execute()

        foundNext = 0
        pos = mT.getCursorPos()
        start = pos

        while not foundNext and pos < mT.getLength() and abs(pos-start)<2000:
            if mT.behaviorArray.hasAction("SPELLCHECK", pos):
                foundNext = 1
            else:
                pos += 1
        
        messages.unqueue('persistant')

        if foundNext <> 0:
            mT.setCursor(pos)
            mT.setSelection('selection', mT.cursorPosInText)
            messages.display()

            
        
    def undo(self):
        self.addText.undo()
        self.delText.undo()
        self.removeSpellcheck.undo()


class SpellcheckCommand(commands.CommandObject):
    def name(self):
        return "SPELLCHECK"

    def _stripPunctuation(self, x):
        alpha = "abcdefghjiklmnopqrstuvwxyz'ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if x in alpha: return x
        else: return " "

    def _findWordsAndRanges(self, text, textOffset):
        filtered = "".join(map(self._stripPunctuation, text))
        wordList = filter(lambda c:c <> '', filtered.split(' '))

        wordRanges = []
        
        offset = 0
        for word in wordList:
            startPos = text.find(word[0], offset)
            endPos = startPos+len(word)
            wordRanges.append( (textOffset+startPos, textOffset+endPos-1) )
            
            offset = endPos
            
        return wordList, wordRanges
        

    def execute(self):
        self.commandList = []
    
        mT = archyState.mainText
        self.origSel = mT.getSelection('selection')

        text = mT.textArray.getSubString(*self.origSel)
        words, wordRanges = self._findWordsAndRanges(text, self.origSel[0])

        c = getSpellChecker()

        firstWordPos = None
        for word, wordRange in zip(words, wordRanges):
            if c.check(word.lower()) or c.check(word.title()):
                pass
            else:
                mT.setSelection('selection', *wordRange)

                if firstWordPos == None:
                    firstWordPos = wordRange[0]
                
                styleCommand = archyState.commandMap.findSystemCommand("Style")
                styleCommand.setinfo(backgroundColor = (255,100,100))
                styleCommand.execute()
                self.commandList.append( styleCommand )
                
                storage = SpellcheckStorage()
                storage.setWord(word)
                mT.behaviorArray.setStorage("SPELLCHECK", storage)
                actionCommand = behavior_editing.AddActionCommand("SPELLCHECK")
                actionCommand.execute()
                self.commandList.append( actionCommand )
                
                
        
        if firstWordPos <> None:
            mT.setSelection('selection', firstWordPos, firstWordPos)
            mT.setCursor(firstWordPos)
        else:
            messages.queue('No spelling errors found.')
        
        self.commandList.reverse()

    
    def undo(self):
        for com in self.commandList:
            com.undo()
        archyState.mainText.setSelection('selection', *self.origSel)
        

class RemoveSpellcheckCommand(commands.CommandObject):
    def name(self):
        return "REMOVE SPELLCHECK INDICATORS"
        
    def execute(self):
        mT = archyState.mainText
        start, end = mT.getSelection('selection')
        
        self.theAction = behavior_editing.RemoveActionCommand("SPELLCHECK")
        self.theAction.execute()
        
        self.theStyle= archyState.commandMap.findSystemCommand("Style")
        self.theStyle.setinfo(backgroundColor = (255,255,255), foregroundColor = (0,0,0))
        self.theStyle.execute()
        
    def undo(self):
        self.theStyle.undo()
        self.theAction.undo()
        


COMMANDS = [SpellcheckCommand, RemoveSpellcheckCommand]
BEHAVIORS = [ {'name':"SPELLCHECK", 'add' : SpellcheckModify, \
                    'delete' : SpellcheckModify, \
                    'style' : SpellcheckStyle, \
                    'focus' : SpellcheckFocus, \
                    'unfocus' : SpellcheckUnfocus } ]

def init():
    try:
        getSpellChecker()
    except:
        print "Spell-check mechanism unavailable.  Disabling spell-checking commands."
        global COMMANDS
        COMMANDS = []
        return
    print "Spell-check mechanism found.  Enabling spell-checking commands."
