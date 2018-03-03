# win_specific.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: win_specific.hpy,v 1.16 2005/04/01 22:22:33 varmaa Exp $"

# This module is the Windows implementation of the [os]_specific modules.

# --------------------------
# Clipboard
# --------------------------

# We need to establish functions for setting and retrieving the contents of
# the OS clipboard.

def getClipboard():
    import win32clipboard
    import win32con
    
    win32clipboard.OpenClipboard()
    try:
        text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    except TypeError:
        text = "Clipboard does not contain string data."
    win32clipboard.CloseClipboard()

    return text

def setClipboard(text):
    import win32clipboard

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()

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

Default_Font = {'size' : 12, 'font' : 'sans'}
Quasimode_Font = {'size' : 40, 'font' : 'sans', 'outline':1}

# --------------------------
# Other functions
# --------------------------

def unstickCapsLock():
    import win32api
    import win32con

    # Simulate a key up
    win32api.keybd_event( win32con.VK_CAPITAL, 0x45, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0 );
    # simulate a key down
    win32api.keybd_event( win32con.VK_CAPITAL, 0x45, win32con.KEYEVENTF_EXTENDEDKEY, 0 );       

def get_screen_size():
    import win32api
    import win32con

    xsize = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    ysize = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    return (xsize, ysize)
