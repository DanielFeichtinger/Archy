# mac_specific.py
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
# --- --- ---

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

# Start_LEAP_Forward_Keybinding        = 'left shift\\ space\\'
# End_LEAP_Forward_Keybinding          = 'left shift/'
# LEAP_Forward_Select_Keybinding       = 'right shift\\'
# Start_LEAP_Backward_Keybinding       = 'left shift\\ return\\'
# End_LEAP_Backward_Keybinding         = 'left shift/'
# LEAP_Backward_Select_Keybinding      = 'right shift\\'
Start_LEAP_Forward_Keybinding        = 'right meta\\' 
End_LEAP_Forward_Keybinding          = 'right meta/' 
LEAP_Forward_Select_Keybinding       = 'left meta\\'
Start_LEAP_Backward_Keybinding       = 'left meta\\'
End_LEAP_Backward_Keybinding         = 'left meta/'
LEAP_Backward_Select_Keybinding      = 'right meta\\'



# Start_Command_Keybinding             = 'left meta\\'
# End_Command_Keybinding               = 'left meta/'
Start_Command_Keybinding             = 'caps lock\\'
End_Command_Keybinding               = 'caps lock/'

Delete_Keybinding                    = 'backspace\\'

Creep_Left_Keybinding                = 'left\\'
Creep_Right_Keybinding               = 'right\\'

# --------------------------
# Fonts
# --------------------------

Default_Font = {'size' : 16, 'font' : 'sans'}
Quasimode_Font = {'size' : 30, 'font' : 'sans', 'outline': 1}

