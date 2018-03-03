# setup.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005
#
# $Id: setup.py,v 1.10 2005/04/01 23:19:43 azaraskin Exp $
#
# This is a distutils setup script that can be used to do a number of
# setup-related tasks with Archy.  It's used as follows:
#
#   python setup.py <target-name>
#
# where <target-name> is a string identifying what kind of setup
# operation you want to perform.
#
# Please see the following URL for more information on distutils:
#
#   http://www.python.org/doc/current/dist/
# -----------------------------------------------------------------

from distutils.core import setup
import glob
import os

# --------------------------
# Base data files
# --------------------------
#
# These data files should accompany any distribution of Archy.

BASE_DATA_FILES = [
    ("", ["initial_document.txt", "fail.wav"]),
    ("commands", glob.glob("commands/*.py")),
    ("commands/tutorial", glob.glob("commands/tutorial/*.py")),
    ("commands/tutorial", glob.glob("commands/tutorial/*.wav")),
    ("commands/tutorial", glob.glob("commands/tutorial/*.ogg")),
    ("commands/tutorial", glob.glob("commands/tutorial/*.png")),	
    ("commands/tutorial", glob.glob("commands/tutorial/*.txt")),
    ("fonts", glob.glob("fonts/*.ttf")),
    ("keycaps", glob.glob("keycaps/*.png")),
    ("icons", glob.glob("icons/*.png")),
    ]

# Files to be distributed only with source tarballs, etc.
SOURCE_DATA_FILES = [
    ("", ["poplib_2_4.py"]),
    ("", [glob.glob("*.py")]),
    ("commands/aspell", glob.glob("commands/aspell/*.py")),
    ]

# Python files that are executable scripts.
BASE_SCRIPTS = [
    'archy.py',
    ]

# --------------------------
# SetupParams class
# --------------------------
#
# This is just an empty class that substitutes for a dictionary, for
# convenience purposes.  Ultimately, its attributes will be passed as
# keyword arguments to the distutils setup() function.

class SetupParams:
    pass

# --------------------------
# Base setup initialization
# --------------------------

setupParams = SetupParams()
setupParams.name = 'Archy'
setupParams.options = {}
setupParams.data_files = BASE_DATA_FILES
setupParams.scripts = BASE_SCRIPTS

# --------------------------
# Determine and write version information
# --------------------------

import version
version.write_build_file()
print "Operating on Archy version %s." % version.get_full_version()
print "Wrote build information file (%s)." % version.BUILD_FILE
print

setupParams.data_files.append( ("", [version.BUILD_FILE]) )
setupParams.version = version.get_version()

# --------------------------
# command 'py2exe':
# Build a Windows Executable
# --------------------------
#
# Note that py2exe is required to run this target.  It can be
# retrieved from http://py2exe.sourceforge.net/.
#
# The windows executable version of Archy will be placed in the 'dist'
# directory.

def on_command_py2exe():
    import py2exe

    print "Preparing to build a Windows Executable of Archy."

    print "---------"
    print "NOTICE: If this setup script crashes, you may need to modify"
    print "the 'extra_DLLs' variable inside this script file."
    print "---------"

    excludes = ['AppKit', 'Foundation', 'objc', 'mac_specific', 'wx', 'wxPython']

    includes = ['xml.sax.expatreader']

    packages = ['commands', 'commands.tutorial', 'encodings', 'xml']

    # These are extra DLLs needed by the installer, which
    # modulefinder/py2exe may not be able to find.  These files also
    # aren't included with the CVS distribution of Archy, so they may
    # point to paths that don't exist on your computer!  If this script
    # file crashes, you may have to modify some of these pathnames or
    # place the DLLs in their expected locations.

    extra_DLLs = []

    aspell_files = [
        ("commands/aspell", glob.glob("commands/aspell/*.pyd")),
        ("commands/aspell/data", glob.glob("commands/aspell/data/*.*")),
        ("commands/aspell/dict", glob.glob("commands/aspell/dict/*.*"))
        ]

    setupParams.data_files.append( ("", extra_DLLs) )
    setupParams.data_files.extend( aspell_files )
    
    setupParams.windows = [ { "script": "archy.py", "icon_resources": [(1, "icons/archy.ico")] } ]
    setupParams.options["py2exe"] = \
                                  {"excludes": excludes,
                                   "includes" : includes,
                                   "packages": packages,
                                   "dll_excludes": ["DINPUT8.dll"]}

    # Dynamically generate the InnoSetup installer script.
    
    ISS_DIR = "windows_installer_files"
    ISS_OUT_FILENAME = "archy.iss"
    ISS_IN_FILENAME = "%s.in" % ISS_OUT_FILENAME
    
    print "Generating %s from %s." % (ISS_OUT_FILENAME, ISS_IN_FILENAME)
    f = open(os.path.join(ISS_DIR, ISS_IN_FILENAME), "r")
    text = f.read()
    f.close()

    text = text.replace( "$BUILD$", str(version.get_build_number()) )
    text = text.replace( "$VERSION$", str(version.get_version()) )
    text = """; WARNING: This file is automatically generated by setup.py; if you want to modify it, change %s instead.\n\n""" % (ISS_IN_FILENAME) + text
    
    f = open(os.path.join(ISS_DIR, ISS_OUT_FILENAME), "w")
    f.write(text)
    f.close()
    
# --------------------------
# command: 'py2app'
# Build a Mac OS X APP
# --------------------------
#
# Note that py2app is required to run this command.  It can be
# retrieved from http://pythonmac.org/packages/.
#
# The OS X executable version of Archy will be placed in the
#'dist' directory.

def on_command_py2app():
    import py2app

    print "Preparing to build a OS X APP of Archy."

    excludes = []

    includes = ['xml.sax.expatreader']

    packages = ['encodings', 'xml']

    setupParams.app = ['archy.py']

    setupParams.options["py2app"] = { \
        "excludes": excludes,
        "includes" : includes,
        "packages": packages
        }

# On a command other than the ones covered above...
def on_command_other():
    setupParams.data_files.extend( SOURCE_DATA_FILES )
    
import sys

if len(sys.argv) > 1:
    if sys.argv[1] == 'py2exe':
        on_command_py2exe()
    elif sys.argv[1] == 'py2app':
        on_command_py2app()
    else:
        on_command_other()
        
setup( **setupParams.__dict__ )

