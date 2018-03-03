# behavior_editing.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
from archy_state import archyState


# --- --- ---

class AbstractActionCommand(commands.CommandObject):
    def __init__(self,behaviorName):
        self.actionVector = archyState.mainText.behaviorArray.getBehavior(behaviorName)
        self.action = archyState.mainText.behaviorArray.behaviorPool.getActionID(**self.actionVector)
        self.actions = None

        behaviorEquiv = archyState.mainText.behaviorArray.getBehaviorEquivalence(behaviorName)
        if behaviorEquiv:
            self.actions = map(lambda c: archyState.mainText.behaviorArray.behaviorPool.getActionID(**c), behaviorEquiv)
        
    def actionManipulation(self):
        raise "Specific action manipulation was not implemented."

    def execute(self):
        self.textRange = archyState.mainText.getSelection('selection')
        
        self.behaviorString = archyState.mainText.behaviorArray.getSubString(*self.textRange)
        self.actionManipulation()

    def undo(self):
        start, end = self.textRange
        archyState.mainText.behaviorArray.replaceBehaviors(self.behaviorString, start)



class AddActionCommand(AbstractActionCommand):
    def actionManipulation(self):
        #print "action vector", self.actionVector
        archyState.mainText.behaviorArray.addActionInRange(self.action, *self.textRange)
        
        
        
class RemoveActionCommand(AbstractActionCommand):   
    def actionManipulation(self):
        if self.actions:
            for id in self.actions:
                archyState.mainText.behaviorArray.removeActionInRange(id, *self.textRange)
        else:
            archyState.mainText.behaviorArray.removeActionInRange(self.action, *self.textRange)



