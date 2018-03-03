# quit.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

from archy_state import archyState
import commands
import sys

# --- --- ---
class QuitCommand(commands.CommandObject):

  def name(self):
    return "QUIT"

  def recordable(self):
    return 0

# sys.exit() will raise a SystemExit exception.
# Make sure any try: .. except: will properly handle this.

  def execute(self):
    print "QuitCommand.execute(): command history size=", len(archyState.commandHistory._history)
    commands.save_and_load.saveState()
    sys.exit()

#end class QuitCommand

# The SIMULATE CRASH command is a debugging command that causes Archy to quit
# without performing a full state save (incremental save data is still
# stored, however, so no data is lost).  This can be useful in testing
# the incremental save system, among other things.

class SimulateCrashCommand(commands.CommandObject):
  def name(self):
    return "SIMULATE CRASH"

  def recordable(self):
    return 0

  def execute(self):
    print "SimulateCrashCommand.execute()"
    sys.exit()

  def undo(self):
    pass

#end class SimulateCrashCommand

COMMANDS = [QuitCommand]
BEHAVIORS = []

def init():
  import debug

  if debug.DEVELOPER_MODE:
    COMMANDS.append(SimulateCrashCommand)
