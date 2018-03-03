# commands/aspell/__init__.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# This module provides an Archy spellcheck interface to Gary Bishop's Pyrex-based GNU aspell API wrapper.

# More information about this wrapper can be found from his Python mailing list post from May 24, 2004:

# http://mail.python.org/pipermail/python-list/2004-May/222117.html

# --------------------------
# Module imports
# --------------------------

from aspell import *
import commands.spellcheck

# --------------------------
# The Archy interface to aspell
# --------------------------

# This is the directory where aspell's dictionary files reside.

DEFAULT_ASPELL_PREFIX = "./commands/aspell"

# This is the spellcheck interface.

class ASpellSpellChecker(commands.spellcheck.AbstractSpellChecker):
    def __init__(self):
        self.checker = aspell.spell_checker(prefix=DEFAULT_ASPELL_PREFIX)

    def suggest(self, word):
        return self.checker.suggest(word)

    def addToDictionary(self, word):
        self.checker.add_to_personal(word)

    def check(self, word):
        return self.checker.check(word)
