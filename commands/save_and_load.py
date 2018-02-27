# save_and_load.py
# The Raskin Center for Humane Interfaces (RCHI) 2004

# This work is licensed under the Creative Commons
# Attribution-NonCommercial-ShareAlike License. To view 
# a copy of this license, visit 
# http://creativecommons.org/licenses/by-nc-sa/2.0/ 

# or send a letter to :

# Creative Commons
# 559 Nathan Abbott Way
# Stanford, California 94305, 
# USA.

# Questions to: Aza Raskin 
# aza@uchicago.edu

# This file saves and loads the following information:

# The Text
# Style Information
# Style Pool 
# Behavior list
# Cursor Location
# Selection Location
# Command History and Position in History
# Setting List


# The state information is saved in a gzip.GzipFile class. This compresses
# the command history (which takes the vast majority of space) to be about 
# 50-60 bytes per command object. 

# A text file which has just the text content without formatting info is also
# saved at the end of a session (QUIT command).

# --------------------------
# Module imports
# --------------------------

import commands
from archy_state import archyState
from os import path

import cPickle

# --------------------------
# Global variables
# --------------------------

# This is the filename to which Archy's state information will be stored.

outputFile = path.join(archyState.userDirectory, 'Humane Document')

# The changeQueue is a list of all the changes that have been made to the state of Archy since it was last incrementally saved.

changeQueue = []

# --------------------------
# Incremental save functionality
# --------------------------

# The following function logs a change to the state of Archy.

def logChange(command):
    changeQueue.append(command)
    
    maybeSaveBackup()

# The following function saves all the queued changes to the state of Archy to disk.

def saveChanges():
    import gzip
    global changeQueue

    if len(changeQueue) == 0:
        return
    #f = gzip.GzipFile(outputFile,'a')
    f = open(outputFile, 'a')
    cPickle.dump(changeQueue, f)
    f.close()
    changeQueue = []

# The following function applies a list of changes to the state of Archy.

def _applyChanges(changeList):
    for command in changeList:
        print "Applying change: %s" % str(command)
        try:
            command.redo()
            archyState.commandHistory.addToHistory(command, incrementalSave=0)
        except:
            print "error in the command:",command.name()
            raise
        #print "in apply changes:", command.name()

# The following two functions take a list and either compresses it or decompresses it. It takes advantage of the fact that the behaviorArray and styleArray generally have long ranges of same-valued entries. Savings vary, but for short files are in the 2 orders of magnitude range.

def compressList(theList):
    compressed_list = []
    last_i = theList[0]
    same_i_count = 1
    for i in theList[1:]:
        if i == last_i:
            same_i_count += 1
        else:
            compressed_list.append((same_i_count, last_i))
            same_i_count = 1
            last_i = i
    compressed_list.append((same_i_count, last_i))
    return compressed_list

def decompressList(compressedArray):
    decompressed_list = []
    for i_count, i in compressedArray:
        decompressed_list.extend([i] * i_count)
    return decompressed_list

# --------------------------
# Text-only backup functionality
# --------------------------

# The following code provides functionality for saving the text content of Archy, in events where Archy crashes and the Humane Document becomes corrupt beyond repair.

# Currently, the backup mechanism works as follows:

# .  1) Whenever the user makes a change to their document (or just issues a command), a counter is incremented.
# .  2) Once this counter reaches MAX_CHANGES_PER_BACKUP, a backup file is saved.

# A backup file is named "_humane_text_<A>.txt", where "<A>" is a consecutively increasing integer.  Once TEXT_MAX_BACKUPS have been made, the oldest one is deleted, so that at most only TEXT_MAX_BACKUPS may exist at any given time.

TEXT_MAX_BACKUPS = 20

TEXT_BACKUP_PREFIX = path.join(archyState.userDirectory, "_humane_text_")
TEXT_BACKUP_SUFFIX = ".txt"

TEXT_BACKUP_FILENAME = "%s%s%s" % (TEXT_BACKUP_PREFIX, "%010d", TEXT_BACKUP_SUFFIX)

def _get_text():
    mT = archyState.mainText
    return mT.getStyledText(0, mT.getLength()-1)[0]

def _find_latest_filename():
    import glob

    files = glob.glob("%s[0-9]*%s" % (TEXT_BACKUP_PREFIX, TEXT_BACKUP_SUFFIX))
    if len(files) == 0:
        new_number = 0
    else:
        numbers = []
        for filename in files:
            numbers.append(int(filename[len(TEXT_BACKUP_PREFIX):-len(TEXT_BACKUP_SUFFIX)]))
        numbers.sort()
        new_number = numbers[-1] + 1
        if len(numbers) >= TEXT_MAX_BACKUPS:
            import os
            file_to_delete = TEXT_BACKUP_FILENAME % numbers[0]
            print "Deleting text-only backup: %s" % file_to_delete
            try:
                os.unlink(file_to_delete)
            except:
                print "Couldn't delete %s." % file_to_delete
    return TEXT_BACKUP_FILENAME % new_number

def save_text_backup():
    filename = _find_latest_filename()

    print "Saving text-only backup: %s" % filename
    import codecs
    f = codecs.open(filename,'w','utf-8')
    f.write(_get_text())
    f.close()

# The following code provides a mechanism whereby a function can be called whenever a change is made to Archy's state; once the function has been called enough times, a text backup will be made.  No further bookkeeping needs to be done on the part of the caller.

changesSinceLastBackup = 0
MAX_CHANGES_PER_BACKUP = 100

def maybeSaveBackup():
    global changesSinceLastBackup

    changesSinceLastBackup += 1
    if changesSinceLastBackup >= MAX_CHANGES_PER_BACKUP:
        save_text_backup()
        changesSinceLastBackup = 0

# --------------------------
# Absolute state save/restore functionality
# --------------------------

# The following class encapsulates the saving and restoring of Archy's state.  It is created to be pickleable (serializable) so that saving and restoring Archy's state consists merely of pickling/unpickling an instance of this class and calling the appropriate save/restore method.

COMMAND_HISTORY_LIMIT=10000

class _ArchyState:


    def save(self):
        mT = archyState.mainText
        length = mT.getLength()

        #print "\n\nSAVE\n"
        #print "mT.textArray.getLength()",mT.textArray.getLength()
        #print "mT.styleArray.getLength()",mT.styleArray.getLength()
        #print "mT.behaviorArray.getLength()",mT.behaviorArray.getLength()

        self.allText, self.allStyles = mT.getStyledText(0, length-1)
        self.allStyles = compressList(self.allStyles)
        self.mainTextNonContentInfo = mT.getNonContentMemento()
        self.passwordList = mT.passwordList
        self.settingList = mT.settingList
        self.behaviorList = mT.behaviorArray
        self.stylePool = archyState.stylePool

        lastCommandIndex = archyState.commandHistory._lastCommandIndex
        lenCommandHistory = len(archyState.commandHistory._history)

        if lenCommandHistory > COMMAND_HISTORY_LIMIT:

            # figure out the first command
            firstCommandIndex = lastCommandIndex - COMMAND_HISTORY_LIMIT + 1
            if firstCommandIndex < 0:
                firstCommandIndex = 0
            print "first command index =", firstCommandIndex

            # copy commands up to the lastCommandIndex - the last command that was run by the user.
            # there can be extra command objects that were undone and are redoable.
            self.commandHistory = archyState.commandHistory._history[firstCommandIndex : lastCommandIndex+1]
            self.lastCommandIndex = len(self.commandHistory)-1

            if len(self.commandHistory) < COMMAND_HISTORY_LIMIT:
                # there are undone commands that can be redone. we will add them to the saved
                # history
                roomLeft = COMMAND_HISTORY_LIMIT - len(self.commandHistory)
                redoable_commands = archyState.commandHistory._history[ lastCommandIndex+1 : lastCommandIndex + 1 + roomLeft]
                self.commandHistory = self.commandHistory+redoable_commands

            print "saved commandHistory size = ", len(self.commandHistory)
            print "saved lastCommandIndex = ", self.lastCommandIndex
        else:
            self.commandHistory = archyState.commandHistory._history
            self.lastCommandIndex = archyState.commandHistory._lastCommandIndex
        self.lastLeapTarget = archyState.commandHistory._lastLeapTarget
        self.selectionAnchor = archyState.commandHistory.getSelectionAnchor()

        #print "len(self.allText)",len(self.allText)
        #print "len(decompressList(self.allStyles))",len(decompressList(self.allStyles))
        #print "self.behaviorList.getLength()", self.behaviorList.getLength()
        #print "\n\n"

    def restore(self):
        mT = archyState.mainText

        #print "\n\nLOAD\n"
        #print "len(self.allText)",len(self.allText)
        #print "len(decompressList(self.allStyles))",len(decompressList(self.allStyles))
        #print "self.behaviorList.getLength()", self.behaviorList.getLength()

        mT.clear()
        archyState.stylePool = self.stylePool
        addText = commands.text_editing.SimpleAddTextCommand(self.allText, decompressList(self.allStyles))
        addText.execute()

        mT.setNonContentInformation(self.mainTextNonContentInfo)

        archyState.commandHistory._history = self.commandHistory
        archyState.commandHistory._lastCommandIndex = self.lastCommandIndex
        archyState.commandHistory._lastLeapTarget = self.lastLeapTarget
        archyState.commandHistory.setSelectionAnchor(self.selectionAnchor)

        mT.behaviorArray = self.behaviorList
        mT.passwordList = self.passwordList
        mT.settingList = self.settingList

        #print "mT.textArray.getLength()",mT.textArray.getLength()
        #print "mT.styleArray.getLength()",mT.styleArray.getLength()
        #print "mT.behaviorArray.getLength()",mT.behaviorArray.getLength()
        #print "\n\n"

# The following function saves Archy's current state to disk.

# At any one moment, there are at least two complete copies on disk: the
# working copy and the backup.  While writing a new copy there are
# between two and three copies.  For strict safety, we should check for
# an existing .new file.  None such should exist if all has gone
# according to plan.  Specifically, if the disk fills up, the
# cPickle.dump will generate an exception.  Since we don't handle that
# exception right now, that will cause a partially-written .new file to
# exist.  If we find such a file, arguably, we should read as much of it
# in as we can.  On the other hand, what if those changes don't make
# sense without the rest of the file?  Better, instead, to handle a full
# disk better.
# -- Russell Nelson, 11/6/2004

def saveState():
    import os
    import gzip
    
    state = _ArchyState()
    state.save()
    
    save_text_backup()

# First we'll save Archy's state information to a brand new file (NOT the working copy).

    global outputFile
    #f = gzip.GzipFile(outputFile+'.new','w')
    f = open(outputFile+'.new', 'w')
    cPickle.dump(state, f)
    f.close()
    print "saved humane document.new"

# Here we delete the backup file, if it exists.

    try:
        os.unlink(outputFile+'.bak')
    except OSError:
        pass

# Now we'll rename the working copy--if it exists--to the backup file.

    try:
        os.rename(outputFile, outputFile+'.bak')
    except OSError:
        pass

# Now we'll rename the new file we just created so it's the current working copy.

    os.rename(outputFile+'.new', outputFile)
    print "renamed to humane document"
    global changeQueue
    changeQueue = []

# The following function loads Archy state information from disk.  It also loads and then applies any incremental changes previously appended to the state file by the saveChanges() function.

def loadState():
    import gzip
    global outputFile
    #f = gzip.GzipFile(outputFile,'r')
    
    try:
        f = open(outputFile, 'r')
    except:
        return "Humane Document file does not exist."

    try:
        state = cPickle.load(f)

        changeList = []
        while 1:
            try:
                changes = cPickle.load(f)
                changeList.extend(changes)
            except EOFError:
                break
    except:
        return "Error loading Humane Document."

    f.close()

    state.restore()
    _applyChanges(changeList)
    return "Loaded file correctly."

