# mac_specific.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: mac_specific.hpy,v 1.11 2005/04/01 22:22:32 varmaa Exp $"

# This module is the Macintosh (OS X) implementation of the
# [os]_specific modules.

# --------------------------
# Clipboard
# --------------------------

# Currently, we're inheriting the wxPython clipboard routines from
# generic_os, but feel free to add an implementation here that doesn't
# require wxWindows (if one exists).

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
