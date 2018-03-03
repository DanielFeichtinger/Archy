# platform_specific.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: platform_specific.hpy,v 1.3 2005/04/01 22:22:32 varmaa Exp $"

# This module represents code and data for Archy that can change
# depending on the particular platform (operating system and hardware)
# the program is running on.  Intrinsically, this module contains no
# such code and data, but instead serves as a "proxy" for other modules
# that contain platform-specific code and data.

# --------------------------
# Module initialization
# --------------------------

# First, the entire namespace from the generic_os module is imported
# into this module.  Think of generic_os as a module that contains the
# default, or "base" platform-specific code and data.

from generic_os import *

# Now, the platform's identity is determined.  If a module
# containing platform-specific data exists for the platform, that
# module's namespace is then imported into this module.

# In effect, all platforms "inherit" from the generic_os module, so a
# platform-specific module only need contain information that overrides
# the default information contained in generic_os.

import platform
current_os = platform.system()

if current_os in ["Windows", "Microsoft Windows"]:
    from win_specific import *
elif current_os == "Darwin":
    from mac_specific import *
elif current_os == "Linux":
    from linux_specific import *

# Now we need to use the current definitions to pre-generate some other definitions that Archy needs. (Yes, this is a bad hack.)

# We need to find a way to reverse-map the name of a key to its virtual key code.  Pygame doesn't offer a function to do this, so we'll use the brute-force approach.

# Note that if a key code can't be found for the given keybinding, this function returns None; this may cause errors later on in Archy, but this is preferable to raising an exception, because we don't want the importing of this module to raise an exception.

def _get_keycode_from_keybinding(keybinding):
    # NOTE: The keybinding must represent only one key.

    key_name = keybinding[:-1]
    import pygame
    keyboard_constants = [getattr(pygame.constants, const) for const in pygame.constants.__dict__.keys() if const.startswith("K_")]
    for const in keyboard_constants:
        if pygame.key.name(const) == key_name:
            return const
    return None

Command_Key = _get_keycode_from_keybinding( Start_Command_Keybinding )
LEAP_Forward_Key = _get_keycode_from_keybinding( Start_LEAP_Forward_Keybinding )
LEAP_Backward_Key = _get_keycode_from_keybinding( Start_LEAP_Backward_Keybinding )
if (not Command_Key or not LEAP_Forward_Key or not LEAP_Backward_Key):
    print "Warning: one of control keys was not recognized correctly"

