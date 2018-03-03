# generic_os.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: generic_os.hpy,v 1.8 2005/04/01 22:22:31 varmaa Exp $"

# This module is the generic implementation of the [os]_specific
# modules.  It contains defaults for any unimplemented platform-specific
# code and data Archy needs.

# There are a number of platform-specific modules to be handled.

# --------------------------
# Clipboard
# --------------------------

# We need to establish functions for setting and retrieving the contents of
# the OS clipboard.

# This is very platform-specific and there isn't really any
# platform-independent way of interacting with the underlying OS's
# clipboard mechanism, or for that matter, knowing whether the
# underlying OS even has a clipboard.

# Since wxPython is available on several platforms, however, we'll
# attempt to import it and use it if it's there.

def getClipboard():
    try:
        from wxPython import wx
    except:
        return "This feature is unavailable on this platform."
    wx.wxTheClipboard.Open()
    clipdata = wx.wxTextDataObject()
    success = wx.wxTheClipboard.GetData(clipdata)
    text = clipdata.GetText()
    wx.wxTheClipboard.Close()
    if not isinstance(text, basestring):
        text = "Clipboard does not contain string data."
    return text

def setClipboard(text):
    try:
        from wxPython import wx
    except:
        return False
    wx.wxTheClipboard.Open()
    clipdata = wx.wxTextDataObject()
    clipdata.SetText(text)
    success = wx.wxTheClipboard.SetData(clipdata)
    wx.wxTheClipboard.Close()
    return success

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

Start_Command_Keybinding             = 'caps lock\\'
End_Command_Keybinding               = 'caps lock/'

Delete_Keybinding                    = 'backspace\\'

Creep_Left_Keybinding                = 'left\\'
Creep_Right_Keybinding               = 'right\\'

# --------------------------
# Fonts
# --------------------------

# This is the default font for main text entry.

Default_Font = {'size' : 16, 'font' : 'sans'}

# The default font used in the translucent display that contains text
# for the command and leap quasimodes, system messages, and so on.

Quasimode_Font = {'size' : 24, 'font' : 'sans'}

# --------------------------
# Other functions
# --------------------------

# This function is called immediately after a key-down event is received
# for the Caps Lock key; it is meant to "undo" the OS-level caps lock
# mode change that occurs (usually indicated by an LED on the user's
# keyboard) whenever Caps Lock is pressed.

def unstickCapsLock():
    pass

# This function is a hook that is called immediately when Archy starts
# up, before its state is initialized.

def startup_hook():
    pass

# This function is a hook that is called immediately when Archy shuts
# down, just before it exits to the underlying operating system.

def shutdown_hook():
    pass

# This function returns the current screen size of the desktop.  If
# this can't be determined or is not applicable, return None.

def get_screen_size():
    pass

