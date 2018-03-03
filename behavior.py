# behavior.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: behavior.hpy,v 1.17 2005/04/03 05:16:33 azaraskin Exp $"

import copy
# Until the bugs get sorted out, use a regular list.
#import run_length_list

# Needed Pools:
# 1) The Command Pool for the raw Add, Style, and Delete commands. Each
# raw command will be assigned an integer.
# 2) The Action Pool. Each action is a set of three integers indicating
# which commands from the Command Library define the action.
# 3) The Behavior Pool. Each behavior is a ordered set of integers
# indicating which actions build the behavior.

# A benefit of this system is the need to store the raw command objects
# only once; There is little duplication of information and uneccesary
# structure.
# The Command Pool may be one level of abstraction too many. I do not
# think that particular building block commands will be used more than
# once with any great frequency (with, perhaps, the NOOP case). However,
# for now I will use the Command Pool for storing the building block
# commands for simplicity of structure.

class Pool:
    def __init__(self):
        self.pool = []

    def getElementID(self, elem):
        try:
            return self.pool.index(elem)
        except ValueError:
            self.pool.append(elem)
            return len(self.pool)-1

    def get(self, ID):
        return self.pool[ID]

class ActionPool(Pool):
    def __init__(self, behaviorPool):
        self.pool = []
        self.commandPool = Pool()
        self._bPool = behaviorPool

    def getActionID(self, **actionCommands):
        action = []
        for key in self._bPool._bArray.keys:
            if key in actionCommands.keys():
                action.append(actionCommands[key])
            else:
                action.append(None)

        action = tuple(action)
        return self.getElementID(action)

    def getCommands(self, ID):
        action = self.pool[ID]
        commands = []
        for i in range(len(self._bPool._bArray.keys)):
            commands.append(action[i])

        return tuple(commands)

    def show(self):
        print self.pool
        print self.commandPool.pool

class BehaviorPool(Pool):
    def __init__(self, bArray):
        self.pool = []
        self._bArray = bArray
        self.actionPool = ActionPool(self)

    def getActionID(self, **args):
        return self.actionPool.getActionID(**args)

    def getBehaviorID(self, actionIDs):
        if type(actionIDs) == int:
            actionIDs = [actionIDs]
        return self.getElementID(actionIDs)

    def getBehavior(self, ID):
        return copy.deepcopy(self.pool[ID])

    def merge(self, oldID, newAction):
        newBehavior = copy.deepcopy(self.getBehavior(oldID))
        newBehavior.insert(0, newAction)
        return self.getBehaviorID(newBehavior)

# For a number of reasons we store command instances in the command pool
# instead of command objects. However, when we remove a command we do
# not care what particular instance it was, we just care about its
# command object type. Thus we need to compare commandInstance.__class__
# attributes.
# TODO:
# If a remove removes an action entirely from the text (say one locks a
# word and then unlocks it [remember that an action is dependent upon
# the particular instance of the commands]) that action persists in the
# action pool. It shouldn't.
    def remove(self, oldID, actionToRemove):
        newBehavior = self.getBehavior(oldID)

        try:
            newBehavior.remove(actionToRemove)
        except ValueError:
            pass #the action is not a part of the behavior
            #print "  value error: could not remove", actionToRemove
        return self.getBehaviorID(newBehavior)

    def has(self, oldID, action):
        theBehavior = self.getBehavior(oldID)

        actionVector = []
        for com in action:
            actionVector.append(com.__class__)

        for i in theBehavior:
            action = self.actionPool.getCommands(i)
            testVector = []
            for com in action:
                testVector.append(com.__class__)
            if testVector == actionToRemoveVector:
                return 1

        return 0

    def show(self):
        self.actionPool.show()
        print self.pool
           

# --- --- ---

class AbstractCommand:
    def __init__(self):
        pass

    def behaviorName(self):
        pass

    def execute(self):
        pass

    def undo(self):
        pass

    def stopBit(self):
        return 0

    def getStorage(self, mT):
        return mT.behaviorArray.getStorage(self.behaviorName(), mT.getCursorPos())

    def findExtent(self, mT):
        return mT.behaviorArray.findActionExtent(self.behaviorName(), mT.getCursorPos())

class AddCommand(AbstractCommand):
    def __init__(self, newText = None, newTextStyle = None):
        self.newText = newText
        self.newTextStyle = newTextStyle

class StyleCommand(AbstractCommand):
    def setStyleDictionary(self, dict):
        self.theStyle = dict

class DeleteCommand(AbstractCommand):
    pass

class FocusCommand(AbstractCommand):
    pass

class UnfocusCommand(AbstractCommand):
    pass
# --- --- ---

# --- --- ---

# --------------------------
# The BehaviorArray class
# --------------------------

# TODO: This class and the StyleArray class should be subclasses of an
# abstract class. As it stands, there is a good deal of code overlap.
class BehaviorArray:
    def __init__(self, associatedTextArray=None):
        self.keys = ['add', 'delete', 'style', 'focus', 'unfocus', 'storage']
        self.keyType = ['class', 'class', 'class', 'class', 'class', 'instance']
        self.behavior_dict = {}
        self.behavior_equiv = {}
        
        import commands.text_editing
        import commands.style_editing
        self.behaviorPool = BehaviorPool(self)

        self._array = []
# Until the bugs get sorted out, use a regular list.
        #self._array = run_length_list.RLE_List()
# TO DO: this next line should really aboid importing these modules, and instead call on the pool of behaviors
        defaultAction = self.behaviorPool.getActionID(add =commands.text_editing.SimpleAddTextCommand, \
                                        delete = commands.text_editing.SimpleDeleteTextCommand, \
                                        style =commands.style_editing.SimpleStyleCommandAbstract)
        print "DEFAULT ACTION", defaultAction
        self.defaultBehavior = self.behaviorPool.getBehaviorID(defaultAction)
        #As the default behavior is defined first it should have the ID of 0.

        if associatedTextArray:
            for i in range(associatedTextArray.getLength()):
                self._array.insert(i, self.defaultBehavior)
                
        self.registerHardcodedBehaviors()


    def registerHardcodedBehaviors( self ):
        import commands
        for i in commands.HARDCODED_BEHAVIORS:
            if i:
                self.registerBehavior( **i )

# --------------------------------
# Behavior Pool access methods
# --------------------------------

    def registerBehavior(self, **actionCommands):
        if not actionCommands.has_key('name'):
            raise "Trying to register a behavior without a name!"
        behaviorName = actionCommands['name']
        if self.behavior_dict.has_key(behaviorName):
            raise "Trying to register two behaviors with identical names of %s." % (behaviorName)
        newBehavior = []
        for i in range(len(self.keys)):
            if self.keys[i] in actionCommands.keys():
                if   self.keyType[i] == 'class':
                    newBehavior.append(actionCommands[self.keys[i]])
                elif self.keyType[i] == 'instance':
                    newBehavior.append(actionCommands[self.keys[i]]())
            else:
                newBehavior.append(None)
        self.behavior_dict[behaviorName] = newBehavior

    def _toDictForm(self, behaviorVector):
        theBehavior = {}
        for i in range(len(self.keys)):
            theBehavior[self.keys[i]] = behaviorVector[i]
        return theBehavior

    def getBehavior(self, behaviorName):
        return self._toDictForm(self.behavior_dict[behaviorName])

    def setStorage(self, behaviorName, storage):
        if not self.behavior_equiv.has_key(behaviorName):
            self.behavior_equiv[behaviorName] = []
            self.behavior_equiv[behaviorName].append(self._toDictForm(self.behavior_dict[behaviorName]))
        self.behavior_dict[behaviorName][self.keys.index('storage')] = storage
        self.behavior_equiv[behaviorName].append(self._toDictForm(self.behavior_dict[behaviorName]))

    def getBehaviorEquivalence(self, behaviorName):
        if self.behavior_equiv.has_key(behaviorName):
            return self.behavior_equiv[behaviorName]
        else:
            return None

    def behaviorHasAction(self, ID, name):
        #The filter removes the commands which do not have the behaviorName() method.
        #In other words, it removes the default AddText, StyleText, and DeleteText commands
        #which have the name() method because they are full fledged commands.
        behaviorCommands = filter(lambda c:'behaviorName' in dir(c), self._getAllCommands(ID))
        return name in map(lambda c:c().behaviorName(), behaviorCommands)

    def _behaviorOverridesDelete(self, ID):
        for aCommand in self._getBlankCommands(ID, [self.keys.index('delete')] ):
            if aCommand().stopBit():
                return 1
        return 0

    def _behaviorOverridesStyle(self, ID):
        for aCommand in self._getBlankCommands(ID, [self.keys.index('style')]):
            if aCommand().stopBit():
                return 1
        return 0

    def __getstate__(self):
        import commands

        odict = self.__dict__.copy()
        odict['_array'] = commands.save_and_load.compressList( odict['_array'] )
        return odict

    def __setstate__(self, dict):
        import commands

        self.__dict__.update(dict)
        self._array = commands.save_and_load.decompressList(self._array)

    def isValidPos(self, pos):
        return pos >= 0 and pos < len(self._array)

    def addActionInRange(self, action, startPos, endPos):
        for pos in range(startPos, endPos + 1):
            if self.isValidPos(pos):
                 oldBehaviorID = self._array[pos]
                 self._array[pos] = self.behaviorPool.merge(oldBehaviorID, action)

    def removeActionInRange(self, action, startPos, endPos):
        for pos in range(startPos, endPos + 1):
            if self.isValidPos(pos):
                oldBehaviorID = self._array[pos]
                self._array[pos] = self.behaviorPool.remove(oldBehaviorID, action)

    def findActionExtent(self, actionName, pos):
        startPos = pos
        while self.behaviorHasAction(self._array[startPos], actionName):
            startPos -= 1
            if not self.isValidPos(startPos):
                break
        startPos += 1

        endPos = pos
        while self.behaviorHasAction(self._array[endPos], actionName):
            endPos += 1
            if not self.isValidPos(endPos):
                break
        endPos -= 1

        return startPos, endPos

    def getStorage(self, actionName, pos):
        behaviorID = self._array[pos]
        for storage in self._getBlankCommands(behaviorID, [self.keys.index('storage')] ):
            if storage:
                if storage.behaviorName() == actionName:
                    return storage
        return None

    def firstActionInRange(self, actionName, startPos, endPos):
        for i in range(startPos, endPos+1):
            if self.behaviorHasAction(self._array[i], actionName):
                return i
        return None

    def hasAction(self, actionName, pos):
        return self.behaviorHasAction(self._array[pos], actionName)

    def getCommand(self, theCommand, pos):
        behaviorID = self._array[pos]
        f = self.keys.index
        allCommands = self._getBlankCommands(behaviorID, [f('add'),f('delete'),f('style'),f('focus'),f('unfocus')])
        for com in allCommands:
            if com.__class__ == theCommand:
                return com

        raise "Position %d with behavior %d does not have the command %s" % (pos, behaviorID, theCommand)

    def _getBlankCommands(self, ID, toGet):
        commands = []
        actions = self.behaviorPool.getBehavior(ID)
        for actionID in actions:
            for num in toGet:
                commands.append(self.behaviorPool.actionPool.getCommands(actionID)[num])
        commands = filter(lambda c:c <> None, commands)
        return commands

    def _getAllCommands(self, ID):
        f = self.keys.index
        return self._getBlankCommands(ID, [f('add'),f('delete'),f('style'),f('focus'),f('unfocus')])

    def getAddBehavior(self, pos):
        behaviorID = self._array[pos]
        return self._getBlankCommands(behaviorID, [self.keys.index('add')])

    def getStyleBehavior(self, pos):
        behaviorID = self._array[pos]
        return self._getBlankCommands(behaviorID, [self.keys.index('style')])

    def getDeleteBehavior(self, pos):
        behaviorID = self._array[pos]
        return self._getBlankCommands(behaviorID, [self.keys.index('delete')])
# \
    def getFocusBehavior(self, pos):
        behaviorID = self._array[pos]
        return self._getBlankCommands(behaviorID, [self.keys.index('focus')])

    def getUnfocusBehavior(self, pos):
        behaviorID = self._array[pos]
        return self._getBlankCommands(behaviorID, [self.keys.index('unfocus')])

    def behaviorOverridesDelete(self, startPos, endPos):
        for pos in range(startPos, endPos+1):
            if self._array[pos].overridesDelete():
                return 1
        return 0

    def behaviorOverridesStyle(self, startPos, endPos):
        for pos in range(startPos, endPos+1):
            if self._array[pos].overridesStyle():
                return 1
        return 0

    def blankableRanges(self, theBlank, startPos, endPos):
        ranges = []
        lastOverrideBit = 1
        rangeStart = startPos

        for pos in range(startPos, endPos+1):
            if theBlank == "deletable":
                overrideBit = self._behaviorOverridesDelete(self._array[pos])
            if theBlank == "styleable":
                overrideBit = self._behaviorOverridesStyle(self._array[pos])

            if lastOverrideBit == 1 and overrideBit == 0 :
                rangeStart = pos
            if  lastOverrideBit == 0 and overrideBit == 1:
                ranges.append( (rangeStart, pos-1) )
            if overrideBit == 0 and pos == endPos:
                ranges.append( (rangeStart, pos) )

            lastOverrideBit = overrideBit

        return ranges

    def deletableRanges(self, startPos, endPos):
        return self.blankableRanges("deletable", startPos, endPos)

    def styleableRanges(self, startPos, endPos):
        return self.blankableRanges("styleable", startPos, endPos)

    def addText(self, newString, insertPos):
        self._array[insertPos:insertPos] = [self.defaultBehavior] * len(newString)

    def delText(self, start, end):
        if end < start:
            return
        if len(self._array) - 1 < start:
            return
        if end < 0:
            return
        if start < 0:
            start = 0

        if len(self._array) - 1 < end:
            end = len(self._array) - 1

        del self._array[start:end+1]

    def getSubString(self, startPos, endPos):
        behaviorString = []
        for pos in range(startPos, endPos+1):
            behaviorAtPos = self._array[pos]
            behaviorString.append(behaviorAtPos)
        return behaviorString

    def replaceBehaviors(self, behaviorString, insertPos):
        for i in range(0, len(behaviorString)):
            self._array[insertPos + i] = behaviorString[i]

    def getLength(self):
        return len(self._array)
