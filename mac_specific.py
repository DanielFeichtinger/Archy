# mac_specific.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: mac_specific.hpy,v 1.11 2005/04/01 22:22:32 varmaa Exp $"

# This module is the Macintosh (OS X) implementation of the
# [os]_specific modules.

# --------------------------
# Clipboard
# --------------------------

# MacOS clipboard integration without dependencies, taken from
# http://www.macdrifter.com/2011/12/python-and-the-mac-clipboard.html

import subprocess

def getClipboard():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = p.wait()
    data = p.stdout.read()
    return data

def setClipboard(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    retcode = p.wait()


# --------------------------
# Key bindings
# --------------------------

# We need to guarantee that keybindings are set appropriately.
# We here establish some accessible constants that key.py will
# call when establishing keybindings.

Start_LEAP_Forward_Keybinding        = 'right alt\\' 
End_LEAP_Forward_Keybinding          = 'right alt/' 
LEAP_Forward_Select_Keybinding       = 'left alt\\'
Start_LEAP_Backward_Keybinding       = 'left alt\\'
End_LEAP_Backward_Keybinding         = 'left alt/'
LEAP_Backward_Select_Keybinding      = 'right alt\\'


Start_Command_Keybinding             = 'left ctrl\\'
End_Command_Keybinding               = 'left ctrl/'

Delete_Keybinding                    = 'backspace\\'

Creep_Left_Keybinding                = 'left\\'
Creep_Right_Keybinding               = 'right\\'

# --------------------------
# Fonts
# --------------------------

Default_Font = {'size' : 16, 'font' : 'sans'}
Quasimode_Font = {'size' : 30, 'font' : 'sans', 'outline': 1}
