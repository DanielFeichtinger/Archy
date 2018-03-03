# run.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# --------------------------
# Module imports
# --------------------------

from archy_state import archyState

import commands
import imp
import imputil
import sys
import os

# --------------------------
# Global constants
# --------------------------

# The following string is a delimiter for modules in Meta-Python.  It does not include the initial document character ("`").

MODULE_DELIMITER = "module "
MODULE_DOCUMENTS_START = "\nM O D U L E   D O C U M E N T S\n"
MODULE_DOCUMENTS_END = "\nE N D   O F   M O D U L E   D O C U M E N T S\n"

# The following string defines the name of the user commands directory, where user-written commands are stored.

MODULES_DIR = "modules"

# The following strings are prefixes for the "fake filenames" assigned to code objects that represent different kinds of user-written code in Archy.

USER_WRITTEN_MODULE_PREFIX = "<user-written module: "
USER_WRITTEN_CMD_PREFIX = "<user-written command: "
SELECTED_TEXT_PREFIX = "<selected text @ "

# --------------------------
# Global variables
# --------------------------

# 'modules' is a global dictionary that keeps track of what Meta-PY modules have been defined.  The keys are strings corresponding to module names, and the values are the text (python code) that comprises each module.

modules = {}

# 'modules_loaded' is a global list that keeps track of what Meta-PY modules have been loaded.  Each element in the list is a string corresponding to a module name.

# We need to keep track of this information so that when we're done with the RUN command, we release all Meta-PY modules that were loaded in that invocation of RUN.  If we don't do this, our custom importer won't be called when previously-loaded Meta-PY modules are imported (because the python interpreter will find them in sys.modules), which means that a user's changes to said modules after their first use by RUN would never show up.

modules_loaded = []

# 'imp_manager' is an instance of imputil.ImportManager and provides an import hook that allows us to provide our own custom importer.

imp_manager = None
old_stdout = sys.stdout
old_stderr = sys.stderr

# --- --- ---
# FUNCTION _get_delimited_range( start_marker, end_marker) 
# Returns start and end indices of a range of text delimited by the start_marker and end_marker, not including the markers.

# It is used to find the contents between "module documents".. "end of module documents" and the contents between "command script documents" .. "end of command script documents"

def _get_delimited_range(start_marker, end_marker):

    tA = archyState.mainText.textArray

    startPos = tA.find(start_marker, 0)
    startPos += len(start_marker)
    endPos = tA.find(end_marker, startPos)
    endPos -= 1

    return startPos, endPos

# --- --- ---
# FUNCTION _get_delimited_text( start_marker, end_marker )
# Return the text that is enclosed between the start and end markers.
# Does not include the markers themselves.

def _get_delimited_text(start_marker, end_marker):
    start_pos, end_pos = _get_delimited_range(start_marker, end_marker)
    tA = archyState.mainText.textArray
    delimited_text = tA.getSubString(start_pos, end_pos)
    return delimited_text

# --- --- ---
# FUNCTION named document iterator
# Finds all documents that start with a special delimiter and name. Used to find all
# "module" and "script command" documents

# TODO: Although this is fine for small segments of text, it will probably not scale well when the text before the current selection is several hundred kilobytes.  If the RUN command becomes slow, consider faster implementations of this function and/or its caller.

def named_document_iterator(text, delimiter):
    documents = text.split("`")

    for doc in documents:
        first_cr = doc.find('\n')
        if doc.startswith(delimiter):
            name = doc[len(delimiter):first_cr]
            yield name, doc

#end textModulesIterator

# --------------------------
# Running MPY Code
# --------------------------
def restore_stdout():
    import sys
    sys.stdout = old_stdout
    sys.stderr = old_stdout

# This is the primary function that parses and executes mpy code, returning the output of the code as a string.  We just redirect standard output and error to a string buffer and execute the code using a CodeRunner object.

def get_mpy_output(codeRunner):
    import StringIO
    import sys

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    if imp_manager == None:
        install_mpy_importer()
        uninstall_custom_importer = 1
    else:
        uninstall_custom_importer = 0

    s = StringIO.StringIO()
    aborted_command_exception = None
    try:
        sys.stdout = s
        sys.stderr = s
        codeRunner.execute()
    except commands.AbortCommandException, e:
        aborted_command_exception = e
    except:
        print_mpy_traceback()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if uninstall_custom_importer:
        uninstall_mpy_importer()

    output_text = s.getvalue()
    s.close()

# A python print always adds a carriage return. This is the desired behavior for the print command (or at expected python behavior) except for the last print called. The last carriage return places the cursor one line below where it should be. However, as many people were quick to point out, removing that last return introduces a boundary condition which cannot be apriori known to either python programmers or new users.

    if aborted_command_exception != None:
        raise aborted_command_exception
    else:
        return output_text

# --- --- ---
# The following function prints a traceback for user-written Meta-Python code.  It differs from a standard traceback printout in that it removes any entries in the stack trace that exist before the MPY code, as these stack trace entries won't be relevant to the user who is trying to debug the code they wrote.

def print_mpy_traceback():
    import traceback
    
    type, value, traceback_obj = sys.exc_info()
    stack_trace_entries = traceback.extract_tb(traceback_obj)
    found_user_code_in_traceback = 0
    for i in range(len(stack_trace_entries)):
        if stack_trace_entries[i][0].endswith(".py") or stack_trace_entries[i][0].endswith(".pyc"):
            continue
        else:
            found_user_code_in_traceback = 1
            break

# If we didn't find the user code anywhere in the traceback, we'll assume a syntax error occurred during the compilation of the user code, in which case the user code filename will be contained in the exception information.

    if found_user_code_in_traceback:
        error_output = traceback.format_list(stack_trace_entries[i:])
    else:
        error_output = []
    error_output += traceback.format_exception_only(type, value)
    error_output = "Traceback (most recent call last):\n" + "".join(error_output)
    print error_output,

# --- --- ---
# A CodeRunner object is a Command pattern that executes python code.

class CodeRunner:
    def execute(self):
        raise NotImplementedError()

# The RunCodeRunner is a CodeRunner object for the RUN command; it grabs the code to run from the current selection and runs it.

class RunCodeRunner(CodeRunner):
    def execute(self):
        mT = archyState.mainText
        textRange = mT.getSelection('selection')
        selectedText = mT.textArray.getSubString(*textRange)

        execute_code_in_documents(selectedText, '%s%d>' % (SELECTED_TEXT_PREFIX, textRange[0]))

# --- --- ---
# The TextCodeRunner is a CodeRunner object for user-written commands in the COMMANDS document.  It is given text to run upon initialization, and executes the code upon execution.

class TextCodeRunner(CodeRunner):
    def __init__(self, textToRun, fakeFilename):
        self.fakeFilename = fakeFilename
        self.textToRun = textToRun

    def execute(self):
        code = compile(self.textToRun, self.fakeFilename, 'exec')
        execute_top_level_code(code)



# --- --- ---
# Here we define a function that keeps track of all the modules that exist in the given text, keeping them on-hand for importing by MPY code.

def register_modules(text):         
    global modules

    modules = {}

    for name, doc in named_document_iterator(text, MODULE_DELIMITER):
        modules[name] = "#" + doc # comment out first line - module delimiter

# --- --- ---
def execute_code_in_documents(text, fakeFilename):
    """Executes all loose python code in the given string,
    which may contain multiple documents."""
    
# First, we'll split the Meta-PY text into its separate PY documents.

    documents = text.split("`")

# Now, we go through the documents and figure out which ones contain 'loose code' to be executed.

    docsToRun = []

    for doc in documents:
        first_cr = doc.find('\n')
        if doc.startswith(MODULE_DELIMITER):
            pass
        else:
            code = compile("#" + doc, fakeFilename, 'exec')
            docsToRun.append(code)

# Now we execute all the loose code we found.

    for d in docsToRun:
        execute_top_level_code(d)

# --- --- ---
# The following function executes python code in its own "brand new" global scope, as though it were top-level code.

# Note that because the code is being executed as though it is at the top level, the global and local dictionaries passed to the "exec" statement are identical.

def execute_top_level_code(text):
    globals_and_locals = {}

    exec text in globals_and_locals

# -----------------
# Custom Importer Setup
# -----------------

# Previously, Archy used Python's imputil module to provide a custom hook for importing modules from the user's humane document.  However, imputil was a little inscrutable and complex in its usage and this area required a lot of documentation, because the imputil module itself was hardly documented at all.  It also hadn't been updated in years, which was puzzling.

# Major problems were encountered with the use of imputil once we tried distributing Archy with py2exe, due to the way that py2exe used ZIP files to import its own modules; put simply py2exe's import mechanism conflicted with imputil's.  After some research, the reason for imputil's recent dormancy and lack of documentation was discovered: a very simple and elegant framework was built-in to Python itself as of release 2.3.  This mechanism is documented quite thoroughly in the following document:

# http://python.fyxm.net/peps/pep-0302.html

# This mechanism is the one Archy currently uses, and it does not conflict with py2exe's import mechanism (most likely because py2exe uses the same mechanism).

def install_mpy_importer():
    """Installs our custom importer."""

    global modules_loaded

    sys.meta_path.append(NewMPYImporter())
    modules_loaded = []

def uninstall_mpy_importer():
    """Uninstalls our custom importer, restoring Python's import
    functionality to its standard behavior."""

    global modules_loaded
    
    sys.meta_path = sys.meta_path[:-1]

    #print "modules loaded ==", modules_loaded

    for module_name in modules_loaded:
        del sys.modules[module_name]
    modules_loaded = []

# -----------------
# Custom Importer Class
# -----------------

# This is the custom importer installed into sys.meta_path; it serves as both a module finder and a module loader.

class NewMPYImporter:
    def _get_module_fake_filename(self, fullname):
        return '%s%s>' % (USER_WRITTEN_MODULE_PREFIX, fullname)

    def _get_code(self, fullname):
        module_code = compile(modules[fullname], self._get_module_fake_filename(fullname), 'exec')
        ispkg = 0
        return ispkg, module_code

    def load_module(self, fullname):
        ispkg, code = self._get_code(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = self._get_module_fake_filename(fullname)
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
        exec code in mod.__dict__
        global modules_loaded
        modules_loaded.append(fullname)
        return mod

    def find_module(self, fullname, path=None):
        if modules.has_key(fullname):
            return self
        else:
            return None

# -----------------
# The RUN Command
# -----------------

# Here we define a class that merely encapsulates the functionality of this module.


class RunCommand(commands.CommandObject):
    def __init__(self):
        commands.CommandObject.__init__(self)
        self.commandList = None

    def name(self):
        return "RUN"

    def getCodeRunner(self):
        """Template method that returns a CodeRunner object for
        the execute() method to use.  This method should be
        overridden by subclasses."""

        return RunCodeRunner()

    def execute(self):
        import api

        module_docs = _get_delimited_text(MODULE_DOCUMENTS_START, MODULE_DOCUMENTS_END)
        register_modules(module_docs)
        commands.recording.start_recording()
        try:
            output_text = get_mpy_output( self.getCodeRunner() )
        except commands.AbortCommandException:
            commands.recording.rollback_recording()
            raise
        if len(output_text) > 0:
            api.insert_text( output_text )
        self.commandList = commands.recording.stop_recording()

    def undo(self):
        self.commandList.undo()

    def redo(self):
        self.commandList.redo()

#end class RunCommand

# -----------------
# Commands Script Document related functions and data
# -----------------

# These are functions and data that deal with the Commands Document.

# The following are the delimiters for the beginning and end of the Commands Document, respectively.

COMMAND_SCRIPTS_START = "\nC O M M A N D   S C R I P T   D O C U M E N T S\n"
COMMAND_SCRIPTS_END = "\nE N D   O F   C O M M A N D   S C R I P T   D O C U M E N T S\n"
COMMAND_SCRIPT_DELIMITER = "command script "
# The following string defines the name of the user commands directory, where user-written commands are stored.

COMMAND_SCRIPTS_DIR = "command_scripts"


# --- --- ---
# The following function finds the commands document and sets its contents to the given text.
# TODO: consider using the DeleteText Command since that will keep the original contents in 
# the deletions document.


def set_marked_documents(start_marker, end_marker, text ):
    mT = archyState.mainText

    start, end = _get_delimited_range(start_marker, end_marker)
    mT.delText(start, end)
    mT.addText(text, start)

# --- --- ---
# FUNCTION write_named_documents( start_marker, end_marker, delimiter_string, directory)
# Write out the documents between start and end marker to the specified directory.
# Each named document in the text that is identified by 
# `
# delimiter string document_name

# will be written as files named : document_name.py in the directory

# Note on newlines, text vs binary files:

# CVS will automatically converts the appropriate new line between the 
# respository and client for text files. Python's file system interface also handles
# newlines correctly for its host OS vs. internal strings. All python strings should use
# Unix newlines. All text files should be text files and NOT marked binary on both
# Windows and Linux systems.

def write_named_documents( start_marker, end_marker, delimiter_string, directory_name):
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    docs = _get_delimited_text(start_marker, end_marker)

    for name, text in named_document_iterator( docs, delimiter_string ):
        filename = "%s/%s.py" % (directory_name, name)
        print "filename=", filename
        file = open(filename, 'w')
        file.write(text)
        file.close()


# --- --- ---

# Function read_named_documents(start_marker, end_marker, directory_name)

# Read all name.py files into the documents marked by start and end markers.

def read_named_documents(start_marker, end_marker, directory_name):
    import os
    
    all_documents = ""
    if not os.path.exists(directory_name):
        print "no directory:",directory_name
        return
    
    allfiles = os.listdir(directory_name)

    for filename in allfiles:
        ext = os.path.splitext(filename)[1]
        if ext == '.py':
            file = open("%s/%s" % (directory_name, filename), 'r')
            text = file.read()
            all_documents += "`%s" % text

    all_documents += "`\n"

    set_marked_documents(start_marker, end_marker, all_documents)

# --- --- ---
# The following Command is just a wrapper for writeUserCommands().

# ToDo: for the undo to work correctly, I think it will have to Load from a particular
# saved file rather than just a load of the most recent save.

class WriteCommandsDocument(commands.CommandObject):
    def name(self):
        return "WRITE COMMANDS"

    def execute(self):
        write_named_documents(MODULE_DOCUMENTS_START, MODULE_DOCUMENTS_END, MODULE_DELIMITER, MODULES_DIR)
        write_named_documents(COMMAND_SCRIPTS_START,COMMAND_SCRIPTS_END, COMMAND_SCRIPT_DELIMITER, COMMAND_SCRIPTS_DIR) 
        print "Commands document written."
        
    def undo(self):
        pass

# --- --- ---
# The following Command is just a wrapper for readUserCommands().

class ReadCommandsDocument(commands.CommandObject):
    def name(self):
        return "READ COMMANDS"

    def execute(self):
        read_named_documents(MODULE_DOCUMENTS_START, MODULE_DOCUMENTS_END, MODULES_DIR)
        read_named_documents(COMMAND_SCRIPTS_START,COMMAND_SCRIPTS_END, COMMAND_SCRIPTS_DIR) 
        print "Commands read."
        
    def undo(self):
        pass

# -----------------
# Retrieving a list of user commands
# -----------------

# The following function returns a list of the names of all available command scripts.

def getUserCommandList():
    import commands

    script_names = []
    command_script_text = _get_delimited_text(COMMAND_SCRIPTS_START,COMMAND_SCRIPTS_END)
    for name, text in named_document_iterator( command_script_text, COMMAND_SCRIPT_DELIMITER ):
        script_names.append(name)

    return script_names

# -----------------
# The User Command Wrapper
# -----------------

# This is a "wrapper" for user-written  command scripts located in the COMMAND SCRIPTS documents.

class UserCommandWrapper(RunCommand):

    def __init__(self, commandName):
        RunCommand.__init__(self)
        self.commandName = commandName

    def clone(self):
        newClone = self.__class__(self.commandName)
        try:
            newClone.validateAndPrepare()
            return newClone
        except:
            raise
    
    def name(self):
        return self.commandName

# The following method checks the meta-document's COMMANDS document to see whether the command name the object was initialized with actually exists; if it does, the command's code is saved.  Otherwise, a CommandNotFoundError is raised.

    def validateAndPrepare(self):
        import commands
        #print "in validateAndPrepare"
        scripts = {}
        command_script_text = _get_delimited_text(COMMAND_SCRIPTS_START,COMMAND_SCRIPTS_END)
        for name, text in named_document_iterator( command_script_text, COMMAND_SCRIPT_DELIMITER ):
            scripts[name] = text

        #print "Modules: %s" % str(modules)
        if not scripts.has_key(self.commandName):
            raise commands.CommandNotFoundError(self.commandName)

        self.commandText = "#" + scripts[self.commandName]
        fakeFilename = "%s%s>" % (USER_WRITTEN_CMD_PREFIX, self.commandName)
        self.codeRunner = TextCodeRunner(self.commandText, fakeFilename)

    def getCodeRunner(self):
        return self.codeRunner

# --------------------------
# The GO TO LAST ERROR Command
# --------------------------

class GoToLastErrorCommand(commands.CommandObject):     
    def name(self):
        return "FIND ERROR"

# TODO: modules and commands are both source code documents. The modules for finding and going to the indices should be easily combined.

    def find_module_start_index(self, modname):
        tA = archyState.mainText.textArray
        index = tA.find("`%s%s" % (MODULE_DELIMITER, modname), 0)
        return index
    # end find_module_start_index

    def find_command_start_index(self, cmdname):
        tA = archyState.mainText.textArray
        index = tA.find("`%s%s" % (COMMAND_SCRIPT_DELIMITER, cmdname), 0)
        return index
    # end find_command_start_index

    def find_line_num_from_index(self, index, line_num):
        tA = archyState.mainText.textArray
        for i in range(line_num-1):
            index = tA.find("\n", index) + 1
        print "Final index: %d" % index
        return index

# This behaves like a LEAP to the index. Cursor and Selection are set to index.
# The preselection anchor is set to the original cursor

# TODO: Discuss what would be an appropriate value for the preselection anchor in this kind of move.

    def move_cursor_to_index(self, index):
        import text_editing

        # self.moveCursor will keep a copy of the original cursor, selections and anchors
        self.moveCursor = text_editing.CursorMovementCommand()
        mT = archyState.mainText
        mT.setCursor(index)
        mT.createNewSelection(index, index)
        mT.setSelection('preselection', index, index )

    def go_to_position_in_module(self, modname, line_num):
        print "Go to position in module: %s, %d" % (modname, line_num)
        index = self.find_module_start_index(modname)
        index = self.find_line_num_from_index(index, line_num)
        self.move_cursor_to_index(index)
    # end position in module

    def go_to_position_in_command(self, cmdname, line_num):
        print "Go to position in command: %s, %d" % (cmdname, line_num)
        index = self.find_command_start_index(cmdname)
        index = self.find_line_num_from_index(index, line_num)
        self.move_cursor_to_index(index)
    # end position in command
        
    def go_to_position_from_index(self, index, line_num):
        print "Go to position from index: %d, %d" % (index, line_num)
        index = self.find_line_num_from_index(index, line_num)
        self.move_cursor_to_index(index)
    # end position in index

    def go_to_position(self, filename, line_num):
        if filename.startswith(USER_WRITTEN_MODULE_PREFIX):
            modname = filename[len(USER_WRITTEN_MODULE_PREFIX):-1]
            self.go_to_position_in_module(modname, line_num)
        elif filename.startswith(USER_WRITTEN_CMD_PREFIX):
            cmdname = filename[len(USER_WRITTEN_CMD_PREFIX):-1]
            self.go_to_position_in_command(cmdname, line_num)               
        elif filename.startswith(SELECTED_TEXT_PREFIX):
            index = int(filename[len(SELECTED_TEXT_PREFIX):-1])
            self.go_to_position_from_index(index, line_num)
        else:
            print "Unrecognizeable filename."
            
    def get_file_traceback_lines(self, text):
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith('  File "'):
                parts = line.split(", ")
                if len(parts) < 2:
                    continue
                filename = parts[0][len('  File "'):-1]
                line_num = int( parts[1][len('line '):] )
                new_lines.append([filename, line_num])
        return new_lines

    def execute(self):
        mT = archyState.mainText
        textRange = mT.getSelection('selection')
        selectedText = mT.textArray.getSubString(*textRange)
        traceback_lines = self.get_file_traceback_lines(selectedText)
        if len(traceback_lines) == 0:
            print "No Python file traceback lines in selection."
            return
        else:
            print traceback_lines
            self.go_to_position(*traceback_lines[-1])
            
    def undo(self):
        self.moveCursor.undo()


# --------------------------
# Module Initialization
# --------------------------


COMMANDS = [GoToLastErrorCommand, RunCommand]
BEHAVIORS = []

