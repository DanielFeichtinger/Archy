# calc.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# This module implements the CALC and UNCALC commands.
# --------------------------
# Module imports
# --------------------------
import commands
import behavior_editing
from archy_state import archyState
import behavior
# -----------------
# The CALC Command
# -----------------

# TODO: This CALC command is not the same as the one in the spec; it only permits the evaluation of strict Python expressions (not statements, such as "a = 1+2") and the result of the evaluation simply replaces the selected text (it does not "box" the selected text and make it possible to run UNCALC on the selection).  It simply moves the currently selected text to the deletions document and inserts the result of the evaluation in its place and selects it.
        

class CalcAddCommand(behavior.AddCommand):
    def behaviorName(self):
        return "CALC"

class CalcDeleteCommand(behavior.DeleteCommand):
    def behaviorName(self):
        return "CALC"

class CalcStyleCommand(behavior.StyleCommand):
    def behaviorName(self):
        return "CALC"


class CalcStorage:
    def __init__(self):
        self.exp = ''

    def behaviorName(self):
        return "CALC"

    def setExpression(self, exp):
        self.exp = exp
    
    def getExpression(self):
        return self.exp



class CalcCommand(commands.CommandObject):
    def name(self):
        return 'CALC'
    
    def paste_output(self, text):           
        self.addText = archyState.commandMap.findSystemCommand("AddText")
        self.addText.setinfo(text)
        self.addText.execute()

    def delete_selection(self):
        self.deleteText = archyState.commandMap.findSystemCommand("DeleteText")
        self.deleteText.execute()

# Here we create a dictionary of global variables/functions that can be referenced by an expression that is to be evaluated by the CALC command.
    def __make_global_dict(self):
        import math
        global_dict = {}
        for symbol in math.__dict__.keys():
            if not symbol.startswith("__"):
                global_dict[symbol] = math.__dict__[symbol]
        return global_dict

    def eval_python_expression(self, text):
        error_string = None
        
        try:
            result = eval(text, self.__make_global_dict())
            result = str(result)
        except:
            import traceback
            import sys
            
            type, value, tb = sys.exc_info()
            error_string = traceback.format_exception_only(type, value)[-1]
        if error_string:
            return error_string
        else:
            return result

    def execute(self):
        textRange = archyState.mainText.getSelection('selection')
        selectedText = archyState.mainText.textArray.getSubString(*textRange)
        self.delete_selection()

        LOCAL_VARS = self.__make_global_dict()

        text = selectedText.replace('\r', '\n')
        had_traling_return = False
        if text[-1] == '\n': had_traling_return = True
        result = u''
        for line in text.split('\n'):
            try:
                result += unicode(eval(line, {}, LOCAL_VARS))
                result += u'\n'
            except:
                try:
                    exec line in {}, LOCAL_VARS
                except:
                    pass
                result += (line+u'\n')
            
        if not had_traling_return: result = result[:-1]
        self.paste_output( result )
        
# Since there is no uncalc, there is no need for the CALC command to do behavior stuff.


        #storage = CalcStorage()
        #storage.setExpression(selectedText)
        #archyState.mainText.behaviorArray.setStorage("CALC", storage)
        #self.theAction = behavior_editing.AddActionCommand("CALC")
        
        #self.theStyle.execute()
        #self.theAction.execute()

    def undo(self):
        #self.theStyle.undo()
        self.addText.undo()
        self.deleteText.undo()
#end class CalcCommand

class UncalcCommand(commands.CommandObject):
    def name(self):
        return "UNCALC"
    
    def execute(self):
        textRange = archyState.mainText.getSelection('selection')
        
        theMin, theMax = textRange
        
        calcPos = archyState.mainText.behaviorArray.firstActionInRange("CALC", *textRange)
        while calcPos:
            calcRange = archyState.mainText.behaviorArray.findActionExtent("CALC", calcPos)
            storage = archyState.mainText.behaviorArray.getStorage("CALC", calcPos)

            originalExpression = storage.getExpression()
            
            archyState.mainText.setSelection('selection', *calcRange)

            self.theAction = behavior_editing.RemoveActionCommand("CALC")
            self.theAction.execute()
            
# TO DO: When UnCalc is restored, the two commands need to use the find command technique.
            #archyState.commandMap.findSystemCommand("AddText")
            #text_editing.DeleteTextCommand().execute()
            #text_editing.AddTextCommand(originalExpression).execute()
            
            addedStart, addedEnd = archyState.mainText.getSelection('selection')
            theMin = min(theMin, addedStart)
            theMax = max(theMax, addedEnd)
            
            calcPos = archyState.mainText.behaviorArray.firstActionInRange("CALC", *textRange)
        
        archyState.mainText.setSelection('selection', theMin, theMax)
        
    def undo(self):
        print "To be implemented"
            
            


COMMANDS = [CalcCommand, UncalcCommand]
BEHAVIORS = [ {'name':"CALC",  'add': CalcAddCommand, 'delete': CalcDeleteCommand, 'style': CalcStyleCommand  } ]

