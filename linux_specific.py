# linux_specific.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: linux_specific.hpy,v 1.1 2005/04/01 22:22:32 varmaa Exp $"

# This module is the Linux implementation of the [os]_specific modules.

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

Start_Command_Keybinding             = 'left super\\'
End_Command_Keybinding               = 'left super/'

Delete_Keybinding                    = 'backspace\\'

Creep_Left_Keybinding                = 'left\\'
Creep_Right_Keybinding               = 'right\\'

# --------------------------
# Other functions
# --------------------------

# Before launching Archy, we need to swap the caps lock and left super
# keys.  Due to the way SDL interprets the caps lock key, it would
# require patching SDL to recognize key-up/key-down events from the caps
# lock key properly.  Because this is cumbersome, we'll instead use
# xmodmap to make the OS think that the caps lock key is the left super
# key while Archy is running (SDL recognizes keyup/keydown events from
# the left super key properly).

# In the future, this process will hopefully be more robust, so that
# Archy can accomplish it without running xmodmap, and so that the key
# mappings can be swapped to their appropriate settings whenever the
# window manager's focus moves in and out of Archy.

# Also note that if you have some kind of xmodmap mapping already in
# place that manipulates the caps lock or left super keys, you may have
# to modify the __XMODMAP_SCRIPT variable below for the key-switching to
# properly occur.

__XMODMAP_SCRIPT = """
    remove Lock = Caps_Lock
    remove mod4 = Super_L
    keysym Super_L = Caps_Lock
    keysym Caps_Lock = Super_L
    add Lock = Caps_Lock
    add mod4 = Super_L
"""

def __swap_caps_lock_and_super_l():
    import os

    temp_filename = "__TEMP_XMODMAP_SCRIPT"
    f = open(temp_filename, "w")
    f.write(__XMODMAP_SCRIPT)
    f.close()

    sys_cmd = 'xmodmap - < %s' % temp_filename
    os.system(sys_cmd)

    os.remove(temp_filename)

def startup_hook():
    __swap_caps_lock_and_super_l()

def shutdown_hook():
    __swap_caps_lock_and_super_l()

