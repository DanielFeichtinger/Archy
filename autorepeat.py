# autorepeat.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# --------------------------
# Keyboard auto-repeat
# --------------------------
from archy_state import archyState
import pygame
import platform_specific
from pygame_run import BUMGARNER_KEY_REPEAT_TIMER_EVENT

# This constant controls how many times a key must be pressed before pygame's keyboard auto-repeat is activated.
AUTOREPEAT_NUMTIMES_START = 3
# Biggest interval between key presses in seconds
# for these presses to trigger autorepeat. Floating number.
AUTOREPEAT_INTERVAL_START_SECS = 1.0

# The repeat rate (in ms) of keyboard autorepeat, once it has been enabled.
AUTOREPEAT_INTERVAL = 50
AUTOREPEAT_INITIAL_DELAY = 250

from pygame.locals import *
NON_AUTOREPEATED_KEYS = [\
    K_NUMLOCK,
    K_CAPSLOCK,
    K_SCROLLOCK,
    K_RSHIFT,
    K_LSHIFT,
    K_RCTRL,
    K_LCTRL,
    K_RALT,
    K_LALT,
    K_RMETA,
    K_LMETA,
    K_LSUPER,
    K_RSUPER,
    K_MODE]


# In the following class, keyboard auto-repeat is implemented such that a user must press the same key 2 times and on the 3rd should hold it down for more than 100 ms to auto-repeat (for the rationale behind this, see THI, pg. 185).
class Autorepeater:
    """This class implements keyboard auto-repeat such that the user must press
    the same key down a certain number of times before auto-repeat mode is
    enabled.    Once the user presses a different key, auto-repeat mode is
    disabled."""

    def __init__(self):
        self.autoRepeatEnabled = 0
        self.autoRepeatCount = 0
        self.autoRepeatKeycode = 0
        self.autoRepeatKeyChar = ''
        self.autoRepeatInitialDelayPassed = 0
        self.didAutoRepeat = 0
        self.lastKeypressTime = 0.0
        self.inCommandQuasimode = 0

# This method is called whenever the main event loop receives an event of type BUMGARNER_KEY_REPEAT_TIMER_EVENT.  It essentially simulates a keypress.

    def onBumgarnerKeyRepeatEvent(self):

# The following are two methods used to figure out if this event got to us too late, i.e., that the user is no longer holding down the auto-repeated key.

        if not self.autoRepeatEnabled:
            return
        if not pygame.key.get_pressed()[self.autoRepeatKeycode]:
            return

        if not self.autoRepeatInitialDelayPassed:
            self.autoRepeatInitialDelayPassed = 1
            pygame.time.set_timer(BUMGARNER_KEY_REPEAT_TIMER_EVENT, AUTOREPEAT_INTERVAL)
            self.autoRepeatCount = 0
        for keyEvent in ('down', 'up'):
            archyState.keyState.keypress(self.autoRepeatKeycode, self.autoRepeatKeyChar, keyEvent)
            self.didAutoRepeat = 1

    def enableAutoRepeat(self):
        """Enables keyboard auto-repeat."""
        
        pygame.time.set_timer(BUMGARNER_KEY_REPEAT_TIMER_EVENT, AUTOREPEAT_INITIAL_DELAY)
        self.autoRepeatInitialDelayPassed = 0
        self.autoRepeatEnabled = 1

    def disableAutoRepeat(self):
        """Disables keyboard auto-repeat."""

        pygame.time.set_timer(BUMGARNER_KEY_REPEAT_TIMER_EVENT, 0)
        self.autoRepeatCount = 0
        self.autoRepeatEnabled = 0
        self.didAutoRepeat = 0

    def newKeyPressed(self, keycode, keyChar):
        """Called when a key is pressed that isn't the same as the key that
        was last pressed."""
        self.autoRepeatCount = 1
        self.autoRepeatKeycode = keycode
        self.autoRepeatKeyChar = keyChar

# Enabling the autorepeat on the keyDown does not work. It must be a characteristic of the
# pygame.key.set_repeat() function to set the repeat on the next keystroke. However, disabling
# auto-repeat works on the keyDown.

    def onKeyDown(self, keycode, keyChar):
        """Counts the keys and disables auto-repeat based on the key that was just pressed down."""

        repeatLeapAgain = self.inCommandQuasimode and ((keycode == platform_specific.LEAP_Forward_Key) or (keycode == platform_specific.LEAP_Backward_Key))

        #Typing k\/ k\/ Command \/ k\ should not start autorepeat
        if keycode == platform_specific.Command_Key:
            self.inCommandQuasimode = 1
            self.disableAutoRepeat()
        elif keycode not in NON_AUTOREPEATED_KEYS or repeatLeapAgain:
            import time
            if self.autoRepeatKeycode == keycode and time.time() - self.lastKeypressTime < AUTOREPEAT_INTERVAL_START_SECS:
                self.autoRepeatCount += 1
                if self.autoRepeatCount >= AUTOREPEAT_NUMTIMES_START:
                    self.enableAutoRepeat()
            else:
                self.disableAutoRepeat()
                self.newKeyPressed(keycode, keyChar)
            self.lastKeypressTime = time.time()

        archyState.keyState.keypress(keycode, keyChar, 'down')

    def onKeyUp(self, keycode):
        """Enable autorepeat if the repeat count is over the threshold."""

        if keycode == platform_specific.Command_Key:
            self.inCommandQuasimode = 0

        if self.autoRepeatEnabled and self.autoRepeatKeycode == keycode:
            if self.didAutoRepeat:
                self.disableAutoRepeat()
            else:
                self.disableAutoRepeat()
                self.autoRepeatCount = 2
        
        archyState.keyState.keypress(keycode, '', 'up')

