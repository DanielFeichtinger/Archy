import pygame
KEYBOARD = pygame.image.load('commands/tutorial/keyboard.png')
KEYBOARD.set_alpha(190)
import platform_specific

VISIBLE = 0
SHOWNKEY = ''
SHOWNMODIFIERS = []

mapping = {}
qmap = {}
square = (23, 19)

dx = 27
x_offset = 10
y_offset = 11
count = 0
mapping['`'] = mapping['~'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['1'] = mapping['!'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['2'] = mapping['@'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['3'] = mapping['#'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['4'] = mapping['$'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['5'] = mapping['%'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['6'] = mapping['^'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['7'] = mapping['&'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['8'] = mapping['*'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['9'] = mapping['('] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['0'] = mapping[')'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['-'] = mapping['_'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['='] = mapping['+'] = [(x_offset+dx*count,y_offset), square]; count += 1


x_offset = 51
y_offset = 39
count = 0
mapping['q'] = mapping['Q'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['w'] = mapping['W'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['e'] = mapping['E'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['r'] = mapping['R'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['t'] = mapping['T'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['y'] = mapping['Y'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['u'] = mapping['U'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['i'] = mapping['I'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['o'] = mapping['O'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['p'] = mapping['P'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['['] = mapping['{'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping[']'] = mapping['}'] = [(x_offset+dx*count,y_offset), square]; count += 1

count = 0
x_offset = 64
y_offset = 65
mapping['a'] = mapping['A'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['s'] = mapping['S'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['d'] = mapping['D'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['f'] = mapping['F'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['g'] = mapping['G'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['h'] = mapping['H'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['j'] = mapping['J'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['k'] = mapping['K'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['l'] = mapping['L'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping[';'] = mapping[':'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['\'']= mapping['\"'] = [(x_offset+dx*count,y_offset), square]; count += 1

count = 0
x_offset = 80
y_offset = 92
mapping['z'] = mapping['Z'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['x'] = mapping['X'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['c'] = mapping['C'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['v'] = mapping['V'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['b'] = mapping['B'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['n'] = mapping['N'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['m'] = mapping['M'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping[','] = mapping['<'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['.'] = mapping['>'] = [(x_offset+dx*count,y_offset), square]; count += 1
mapping['?'] = mapping['/'] = [(x_offset+dx*count,y_offset), square]; count += 1

mapping['\n'] = mapping['\r'] = mapping['\t'] = [(368,64), (36,17)]

k = pygame.constants

mapping[' '] = [(146,121), (277-146, 15)]
mapping[k.K_BACKSPACE]  = [(368,11), (405-365, 20)]

qmap[k.K_LALT]      = [(67,119), (47, 18)]
qmap[k.K_RALT]      = [(310,119), (47, 18)]
qmap[k.K_CAPSLOCK]  = [(14,67), (65-14, 17)]
qmap['']        = [(0,0), (0,0)]


KEYBOARD_POS = [50, 0]

TRANS_TABLE = {}
TRANS_TABLE['leapf']    = platform_specific.LEAP_Forward_Key
TRANS_TABLE['leapb']    = platform_specific.LEAP_Backward_Key
TRANS_TABLE['command']  = platform_specific.Command_Key
TRANS_TABLE['delete']   = pygame.constants.K_BACKSPACE
TRANS_TABLE['space']    = ' '
TRANS_TABLE['return']   = '\n'
TRANS_TABLE['left'] = pygame.constants.K_LEFT
TRANS_TABLE['right']    = pygame.constants.K_RIGHT
TRANS_TABLE['up']   = pygame.constants.K_UP
TRANS_TABLE['down'] = pygame.constants.K_DOWN
TRANS_TABLE['tab']  = '\t'

def translate(key_str):
    global TRANS_TABLE

    if len(key_str) > 1:
        return TRANS_TABLE[key_str]
    else:
        return key_str

def setKeyboardYPos(pos):
    global KEYBOARD_POS
    KEYBOARD_POS[1] = pos

def setKeyboardXPos(pos):
    global KEYBOARD_POS
    KEYBOARD_POS[0] = pos

def getKeyboardPos():
    global KEYBOARD_POS
    return KEYBOARD_POS

def getKeyboardImage():
    global KEYBOARD
    return KEYBOARD


def getStandardKeyPositions():
    global mapping
    return mapping

def getQuasimodeKeyPositions():
    global qmap
    return qmap


def show(key = ''):
    global VISIBLE, SHOWNKEY
    VISIBLE = 1
    SHOWNKEY = key

def hide():
    global VISIBLE, SHOWNKEY, SHOWNMODIFIER
    VISIBLE = 0
    SHOWNKEY = ''
    SHOWNMODIFIER = ''

def visible():
    global VISIBLE
    return VISIBLE

def shownKey():
    global SHOWNKEY
    return SHOWNKEY

def addModifier(mod):
    global SHOWNMODIFIERS
    if mod not in SHOWNMODIFIERS:
        SHOWNMODIFIERS.append(mod)

def removeModifier(mod):
    global SHOWNMODIFIERS
    try:
        del SHOWNMODIFIERS[SHOWNMODIFIERS.index(mod)]
    except:
        pass

def unshowLeap():
    global SHOWNMODIFIERS

    leap_forward = translate('leapf')
    leap_backward = translate('leapb')

    removeModifier(leap_forward)
    removeModifier(leap_backward)


def resetModifiers():
    global SHOWNMODIFIERS
    SHOWNMODIFIERS= []

def shownModifier():
    global SHOWNMODIFIERS
    return SHOWNMODIFIERS

def isModifier(mod):
    return mod in getQuasimodeKeyPositions().keys()

def drawPress(screen, where, size):
    indicator = pygame.Surface(size)
    indicator.fill([200,0,0])
    indicator.set_alpha(110)
    pos = getKeyboardPos()
    screen.blit(indicator, [pos[0]+where[0], pos[1]+where[1]])

def render(screen):
    sMap = getStandardKeyPositions()
    qMap = getQuasimodeKeyPositions()

    pos = getKeyboardPos()
    if visible():
        screen.blit(getKeyboardImage(), pos)

    if shownKey() in sMap.keys():
        if shownKey() in sMap.keys():
            drawPress(screen, *sMap[shownKey()])
        else:
            print "Thread error: Key map dictionary lookup failed"

    for mod in shownModifier():
        if mod in qMap.keys():
            if mod in qMap.keys():
                drawPress(screen, *qMap[mod] )
            else:
                print "Thread error: Modifier key map dictionary lookup failed"