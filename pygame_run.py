# pygame_run.py
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

VERSION = "$Id: pygame_run.hpy,v 1.80 2005/04/04 04:04:52 andrewwwilson Exp $"

# --------------------------
# Module imports
# --------------------------

import commands

import pygame
from pygame.locals import *

import audio    
import surfaces
import threading

# The archyState contains all of the global singletons (such as mainText, stylePool, commandMap, etc.)
from archy_state import archyState

# The following imports are only here so that modulefinder can locate them when py2exe is run.
import webbrowser, calendar, drawing_surface, text_abstract, text_viewer

# --------------------------
# Module constants
# --------------------------

CURSOR_TIMER_EVENT = 30
CURSOR_TIMER_INTERVAL = 175

# Bumgarner repeat - approach for autorepeat when autorepeat is triggered by two presses of the key
# and holding it down third time. Named by the name of man of that name who invented it.
BUMGARNER_KEY_REPEAT_TIMER_EVENT = 31

TUTORIAL_MOVIE_EVENT = 32

# This is the size of the Archy window (when in windowed mode); the assigned value here is used only if we can't determine the screen size of the user's desktop.

WINDOWED_SCREEN_SIZE = (640,480)

# This is the resolution the screen is set to when Archy is in fullscreen mode.

FULLSCREEN_SCREEN_SIZE = None

# --------------------------
# Module global variables
# --------------------------

screen = None
mouse_visibility = None
fullscreen_mode = None
user_directory = None

# --------------------------
# Screen drawing
# --------------------------

def draw_screen():
    global screen

    if archyState.mainTextViewer.isChanged() or archyState.quasiModeTextViewer.isChanged():
        archyState.mainTextViewer.render()
        archyState.quasiModeTextViewer.render()
        archyState.quasiModeTextViewer.draw()
        
        # TODO: This is a hack to allow the tutorial to draw the on-screen keyboard
        commands.tutorial.draw(screen)

        pygame.display.flip()


# --------------------------
# Event handling
# --------------------------

def post_tutorial_event(movie, event):
    e = pygame.event.Event( TUTORIAL_MOVIE_EVENT, movie=movie, event_data=event )
    pygame.event.post( e )

def handle_event(e):
    if e.type == CURSOR_TIMER_EVENT:
        archyState.mainTextViewer.toggle_cursor_display()

    elif e.type == BUMGARNER_KEY_REPEAT_TIMER_EVENT:
        archyState.autorepeater.onBumgarnerKeyRepeatEvent()

    elif e.type == TUTORIAL_MOVIE_EVENT:
        if commands.tutorial.is_tutorial_running():
            e.movie.handle_tutorial_event(e.event_data)

    elif e.type == KEYDOWN:
        if commands.tutorial.is_tutorial_running():
            commands.tutorial.stop_tutorial()

        if e.key == K_CAPSLOCK:
            import platform_specific
            platform_specific.unstickCapsLock()
        
        keyChar = e.unicode.replace('\r', '\n')
        archyState.autorepeater.onKeyDown(e.key, keyChar)

    elif e.type == KEYUP:
        archyState.autorepeater.onKeyUp(e.key)

    elif e.type == MOUSEBUTTONDOWN:
        print e.pos

    elif e.type == VIDEORESIZE:
        win = pygame.display.set_mode(e.size, RESIZABLE)
        archyState.mainText.setSize(e.size)
        archyState.mainText.textViewer.startLine.wordWrap(mainText.screen.get_size()[0])
        archyState.mainText.moveCursor(0)
        archyState.mainTextViewer.render()

    elif e.type == QUIT:
        quit = commands.quit.QuitCommand()
        quit.execute()

    draw_screen()

# --------------------------
# Pygame initialization
# --------------------------

def init_pygame():
    pygame.init()

    import version
    pygame.display.set_caption("Archy - build %d" % version.get_build_number() )

    determine_resolutions()
    set_application_icon()
    init_pygame_fonts()

# This function determines the size of Archy's window when in windowed mode, and the resolution of the screen when Archy is in fullscreen mode.  The exact values depend on whether we can determine the resolution of the user's desktop.

def determine_resolutions():
    import platform_specific
    global WINDOWED_SCREEN_SIZE, FULLSCREEN_SCREEN_SIZE

    screen_size = platform_specific.get_screen_size()

    if (screen_size != None):
        FULLSCREEN_SCREEN_SIZE = screen_size
        WINDOWED_SCREEN_SIZE = [ int( screen_size[0] * 0.75 ), int( screen_size[1] * 0.75 ) ]
    else:
        # Set fullscreen res to the highest available.
        FULLSCREEN_SCREEN_SIZE = pygame.display.list_modes()[0]

ICON_FILE = "icons/archy.ico"

def set_application_icon():
    icon_img = pygame.image.load( ICON_FILE )
    icon_img.set_colorkey(0)
    pygame.display.set_icon( icon_img )

BUILTIN_FONTS = [ \
    [ 'sans',       0, 0, 'Vera.ttf' ],
    [ 'sans',       1, 0, 'VeraBd.ttf' ],
    [ 'sans',       0, 1, 'VeraIt.ttf' ],
    [ 'sans',       1, 1, 'VeraBI.ttf' ],
    [ 'serif',      0, 0, 'VeraSe.ttf' ],
    [ 'serif',      1, 0, 'VeraSeBd.ttf' ],
    [ 'monospace',  0, 0, 'VeraMono.ttf' ],
    [ 'monospace',  1, 0, 'VeraMoBd.ttf' ],
    [ 'monospace',  0, 1, 'VeraMoIt.ttf' ],
    [ 'monospace',  1, 1, 'VeraMoBI.ttf' ],
]

def init_pygame_fonts():
    import pygame.font
    import pygame.sysfont

    sysfonts = pygame.sysfont.Sysfonts
    pygame.sysfont.get_fonts()
    for font in BUILTIN_FONTS:
        
        pygame.sysfont._addfont(name=font[0], bold=font[1], italic=font[2], font='fonts/%s' % (font[3]), fontdict=sysfonts)


def set_mouse_visibility(visibilityFlag):
    global mouse_visibility

    if mouse_visibility == visibilityFlag:
        return

    mouse_visibility = visibilityFlag
    pygame.mouse.set_visible(visibilityFlag)

def get_mouse_visibility():
    return mouse_visibility

def init_archy(fullscreenFlag=0):
    global screen
    global fullscreen_mode

    if fullscreen_mode == fullscreenFlag:
        return

    fullscreen_mode = fullscreenFlag

    if fullscreenFlag:
        set_mouse_visibility(0)
        screen = pygame.display.set_mode(FULLSCREEN_SCREEN_SIZE, FULLSCREEN)
    else:
        set_mouse_visibility(1)
        screen = pygame.display.set_mode(WINDOWED_SCREEN_SIZE)

    margin = 4
    screen.fill([255,255,255])
    screen_surface = surfaces.PygameSurface(surface=screen.subsurface([[margin,0], [screen.get_width()-2*margin,screen.get_height()]]))
    archyState.init(screen_surface)
    print(user_directory)

    #Because the text documents have been entirely reinitialized the cursorObserver is no longer registered as an observer. If we want focus events to work (see cursor.py) we need to reregister the cursor observer by reinstantiate it.
    cursorObserver = commands.cursor.CursorObserver()

# Performs basic Archy initialization. Can be called from unit tests.
def init_fundamentals():
    init_pygame()
    import platform_specific
    platform_specific.startup_hook()
    audio.init()
    commands.init()
    init_archy()

# The following function sets fullscreen mode on or off.  Unfortunately, this currently involves re-initializing Archy's state; hopefully this won't be the case in the future.

def set_fullscreen_mode(fullscreenFlag):
    init_archy(fullscreenFlag)

def get_fullscreen_mode():
    return fullscreen_mode

def get_fonts():
    return pygame.font.get_fonts()

def name_to_color(colorName):
    return pygame.color.Color(colorName)

# --------------------------
# The main function
# --------------------------

# This is where Archy initializes itself and starts running.

def run_archy():
    process_command_line_arguments()

    import debug
    debug_log = debug.DebugLog('log/debug.log')
    debug_log.install()

    import time
    print "---- Archy session started %s ----" % time.ctime()
    print debug.get_system_info()
    init_fundamentals()

    try:
        main()
    except SystemExit:
        # Archy exited gracefully.
        shutdownServiceThreads()
    except:
        print "---- Abnormal Archy termination ----"
        # Archy exited abnormally.
        shutdownServiceThreads()

        # TODO: We might want to implement a more "graceful" abnormal exit, such as informing the user that a fatal error occurred.
        import debug
        tb_info = debug.get_traceback()
        print tb_info
        debug.report_bug("Abnormal Archy termination", tb_info)

    import platform_specific
    platform_specific.shutdown_hook()

    print "---- Archy session ended %s ----" % time.ctime()
    debug_log.uninstall()


# This function attempts to pre-compile some functions using Psyco to speed things up.  If Psyco isn't available, print a warning message and continue.

def accelerate_functions():
    try:
        import psyco
    except ImportError:
        print "Psyco not found.  Some features may run slowly."
        return

    print "Psyco found, accelerating functions."

    import bmh_search
    import behavior

    psyco.bind(bmh_search.BMHSearchForward)
    psyco.bind(bmh_search.BMHSearchBackward)
    import commands.save_and_load
    psyco.bind(commands.save_and_load.compressList)
    psyco.bind(behavior.BehaviorArray)
    psyco.bind(behavior.BehaviorArray._getBlankCommands)

def process_command_line_arguments():
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-d", "--developer-mode", action="store_true", dest="developer_mode", default=False, help="invoke archy in developer mode (no web-based bug reporting, etc.)")
    parser.add_option("-u", "--user-directory", dest="user_directory", default="tmp", help="invoke archy to store user data in the specified directory (default is tmp/)")
    options, args = parser.parse_args()
    import debug
    debug.DEVELOPER_MODE = options.developer_mode
    archyState.userDirectory = options.user_directory

def main():
    startupServiceThreads()

    # Set up the cursor timer.
    pygame.time.set_timer(CURSOR_TIMER_EVENT, CURSOR_TIMER_INTERVAL)
    cursorObserver = commands.cursor.CursorObserver()
    while 1:
        # Block for an event.
        e = pygame.event.wait()
        handle_event(e)

        # Handle any remaining events that happen to be queued...
        for e in pygame.event.get():
            handle_event(e)
        #end for
    #end while

def startupServiceThreads():
    #start the email threads
    import email_thread
    email_thread.incomingThread.start()
    email_thread.outgoingThread.start()
    email_thread.server_settings_changed.clear()
    email_thread.check_mail_now.clear()
    email_thread.is_incoming_mail.clear()
    email_thread.is_outgoing_mail.clear()

def shutdownServiceThreads():
    #stop the email threads
    import email_thread
    email_thread.system_quit.set()
    email_thread.is_outgoing_mail.set()
    email_thread.check_mail_now.set()

# --------------------------
# Module initialization
# --------------------------

if __name__ == '__main__':
    run_archy()

