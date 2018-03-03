# glyph.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: glyph.hpy,v 1.53 2005/04/04 04:04:51 andrewwwilson Exp $"

# --------------------------
# Module imports
# --------------------------

import surfaces
# TO DO: maybe remove the import?
import style
from archy_state import archyState

# --------------------------
# The 'Glyph' Abstract class
# --------------------------

# Glyphs are visual objects, defined by their appearance.  In abstract form, this means a glyph has a height, a width, and a rendering method.

# For efficiency purposes, the Glyph does not have accessor methods to retrieve its metrics information.  Instead, the following attributes (which should be used as read-only) should be defined by any Glyph instance: height, width, ascent, descent.

class Glyph:
    def __init__(self):
        pass

    def render(self):
        pass

# --------------------------
# The 'GlyphPool' Class
# --------------------------

class GlyphPool:
    def __init__(self):
        self.glyphDict = {}

    def makeGlyph(self, char, styleID):


        if char == '\n':
            new_glyph = NewlineGlyph(styleID)
        elif char == ' ':
            new_glyph = SpaceGlyph(styleID)
        elif char == '\t':
            new_glyph = TabGlyph(styleID)

        elif ord(char) == 31:
            new_glyph = AltKeyGlyph(styleID)
        elif ord(char) == 20:
            new_glyph = BackspaceKeyGlyph(styleID)
        elif ord(char) == 30:
            new_glyph = CapslockKeyGlyph(styleID)
        elif ord(char) == 29:
            new_glyph = TildeKeyGlyph(styleID)
        elif ord(char) == 28:
            new_glyph = ReturnKeyGlyph(styleID)
        elif ord(char) == 27:
            new_glyph = DownKeyGlyph(styleID)
        elif ord(char) == 19:
            new_glyph = UpKeyGlyph(styleID)
        elif ord(char) == 21:
            new_glyph = LeftKeyGlyph(styleID)
        elif ord(char) == 22:
            new_glyph = RightKeyGlyph(styleID)

        else:
            new_glyph = FontGlyph(char, styleID)

        self.glyphDict[(char, styleID)] = new_glyph
        return new_glyph        

    def getGlyph(self, char, styleID):
        key = (char, styleID)
        try:
            return self.glyphDict[key]
        except KeyError:
            return self.makeGlyph(char, styleID)

# Here we declare our global flyweight pool for glyphs.

globalGlyphPool = GlyphPool()

# --------------------------
# The 'Font' Class
# --------------------------

import pygame.font
#print pygame.font.get_fonts()

class Font:

# ANTIALIAS determines whether we want to draw font glyphs antialiased or not.

    ANTIALIAS = 1

    def __init__(self, styleID):
        pool = archyState.stylePool
        styleObj = pool[styleID]

        self.fontName = styleObj.get('font')
        self.size = styleObj.get('size')
        self.bold = styleObj.get('bold')
        self.italic = styleObj.get('italic')
        self.fgcolor = styleObj.get('foregroundColor')
        self.bgcolor = styleObj.get('backgroundColor')
        self.outline = styleObj.get('outline')
        
        import pygame.font
        
        self._font = pygame.font.SysFont( self.fontName, self.size, self.bold, self.italic )
        
# The following instance variable will be a flyweight pool of characters for this font.

        self._characters = {}

    def getAscent(self):
        return self._font.get_ascent()

    def getDescent(self):
        #return 0
        return self._font.get_descent()

    def getLineSize(self):
        return self._font.get_linesize()

    def getHeight(self):
        return self._font.get_height()

    def getSize(self, char):
        if self.outline:
            self.render(char)
            return self._characters[char].getSize()
        else:
            return self._font.size(char)

    def render(self, char):
        if not self._characters.has_key(char):
            try:
                if self.outline:
                    import pygame.font
                    
                    theFont = pygame.font.SysFont( self.fontName, self.size-3, self.bold, self.italic )
                    charSurf = outlineText(theFont, char, self.fgcolor)
                else:
                    charSurf = self._font.render(char, self.ANTIALIAS, self.fgcolor, self.bgcolor)

# Note here that if the character is invalid and SDL TTF can't render the glyph, we'll just insert a '?' character for now, so that Archy doesn't crash.

            except:
                charSurf = self._font.render('?', self.ANTIALIAS, self.fgcolor, self.bgcolor)

            self._characters[char] = surfaces.PygameSurface(surface= charSurf)#surfaces.PygameSurface(surface = )
            
        return self._characters[char]

# --------------------------
# The 'FontPool' Class
# --------------------------

# The following class implements a flyweight pool for fonts.

class FontPool:
    def __init__(self):
        self._fontPool = {}

    def getFont(self, styleID):
        if not self._fontPool.has_key(styleID):
            self._fontPool[styleID] = Font(styleID)
        return self._fontPool[styleID]
        
def outlineText(font, char, color):
    """This outline text function is based on code by Pete Shinners"""
    offcolor = [c^40 for c in color]
    notcolor = [c^0xFF for c in color]
    
    base = font.render(char, 0, color, notcolor)
    if len(char) == 1 and ord(char) == 32:
        size = base.get_width() + 10, base.get_height()-10
    else:
        size = base.get_width() + 2, base.get_height() + 2
    
    img = pygame.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img

# Here we declare our global flyweight pool for fonts.

globalFontPool = FontPool()

# --------------------------
# The 'FontGlyph' Class
# --------------------------

class FontGlyph(Glyph):

# '__init__()' takes 2 arguments: a character 'char', and a 'styleID'
    
    def __init__(self, char, styleID):
        self._surface = None
        self._char = char
        self._style = styleID
        self._font = globalFontPool.getFont( styleID )
        self.descent = self._font.getDescent()
        self.ascent = self._font.getAscent()
        size = self._font.getSize(self._char)
        self.width = size[0]
        self.height = size[1]
        self.isWhitespace = 0
        self.lineHeight = self._font.getLineSize()
        #print "char=",char, "styleID=", styleID, "lineHeight=", self.lineHeight

    def render(self):
        if self._surface == None:
            self.makeSurface()
        return self._surface

    def makeSurface(self):
        self._surface = self._font.render(self._char)

# --------------------------
# The 'BlankGlyph' class
# --------------------------

# This is just a blank glyph that takes up space but offers no visible characteristics.  Probably the simplest possible kind of glyph.

class BlankGlyph:
    def __init__(self, size):
        self.height = size[1]
        self.width = size[0]
        self.ascent = self.height
        self.descent = 0
        self.lineHeight = self.height
        self._surface = surfaces.PygameSurface(size)
        self._surface.clear()
        self._surface.setBackgroundToTransparent()

    def setGlyphMetrics(self, targetGlyph):
        self.ascent = targetGlyph.ascent
        self.descent = targetGlyph.descent
        self.lineHeight = targetGlyph.lineHeight

    def render(self):
        return self._surface

# --------------------------
# The Document Character Glyph
# --------------------------

# The DocumentCharacterGlyph is a simple Glyph class for document characters.  It keeps a pre-rendered singleton surface containing a bitmap of the document character (as per the spec, it is a gray bar that spans the user's screen) and returns it when called upon.

class DocumentCharacterGlyph(Glyph):
    MARGIN_SIZE = 1
    HEIGHT = 5
    ASCENT = 5
    DESCENT = 0
    COLOR = (175,175,175)
    
    def __init__(self, width=0):
        self._char = "`"
        self.isWhitespace = 0

        self.height = self.HEIGHT
        self.ascent = self.ASCENT
        self.descent = self.DESCENT

        self.setWidth(width)
        self.lineHeight = self.height

# Upon the instantiation of the first document character, the singleton document character bitmap is created as follows.

    def _makeSurface(self):
        if self.width == 0:
            self._surface = None
            return

        newSurface = surfaces.PygameSurface( (self.width, self.HEIGHT) )
        newSurface.clear()
        grayBarSize = ( self.width - (self.MARGIN_SIZE * 2), self.HEIGHT - (self.MARGIN_SIZE * 1) )
        grayBarPos = ( self.MARGIN_SIZE, self.MARGIN_SIZE )
        newSurface.drawRectangle(grayBarSize, grayBarPos, self.COLOR, 255)
        self._surface = newSurface

    def setWidth(self, width):
        self.width = width
        self._makeSurface()

    def render(self):
        return self._surface

# --------------------------
# The Page Character Glyph
# --------------------------

# Just like the Document Character Glyph, only thinner.

class PageCharacterGlyph(DocumentCharacterGlyph):
    HEIGHT = 2
    ASCENT = 5

# --------------------------
# The Abstract Keyboard Key Glyph
# --------------------------

class AbstractKeyGlyph(Glyph):
    FILE = ''
    
    def __init__(self, width=0):
        self._char = "|"
        self.isWhitespace = 0

        import pygame, os
        base = "keycaps"
        self._surface = surfaces.PygameSurface( surface=pygame.image.load(os.path.join(base,self.FILE)))

        self.height = self._surface.getHeight()
        self.width = self._surface.getWidth()
        self.ascent = self.height-9
        self.descent = 0

        self.lineHeight = self.height

    def render(self):
        return self._surface

class AltKeyGlyph(AbstractKeyGlyph):
    FILE = 'alt.png'

class BackspaceKeyGlyph(AbstractKeyGlyph):
    FILE = 'backspace.png'

class CapslockKeyGlyph(AbstractKeyGlyph):
    FILE = 'capslock.png'

class TildeKeyGlyph(AbstractKeyGlyph):
    FILE = 'tilde.png'

class ReturnKeyGlyph(AbstractKeyGlyph):
    FILE = 'return.png'

class UpKeyGlyph(AbstractKeyGlyph):
    FILE = 'up.png'

class DownKeyGlyph(AbstractKeyGlyph):
    FILE = 'down.png'

class LeftKeyGlyph(AbstractKeyGlyph):
    FILE = 'left.png'

class RightKeyGlyph(AbstractKeyGlyph):
    FILE = 'right.png'

# --------------------------
# The Whitespace Glyph
# --------------------------

# WhitespaceGlyph is an abstract class for whitespace characters such as newlines, spaces, and tabs.  These characters must be handled specially because when the command quasimode is invoked, they change from being "invisible" to being displayed as some sort of symbol.  For instance, space characters are displayed as a centered dot.

# This class provides a framework for such characters by calling upon two template methods, which are implemented by concrete subclasses.  doGenerateInvisibleGlyph() returns a glyph representing the actual "invisible" whitespace character, and doGenerateSymbolSurface() returns a surface representing the symbol to be displayed when command quasimode is active.

class WhitespaceGlyph(Glyph):
    SYMBOL_COLOR = (150, 150, 150)

    symbol_surfaces = {}

    def __init__(self, styleID):
        self._style = styleID
        self.generateInvisibleGlyph()
        self.generateSymbolSurface()
        self._char = self.getChar()
        self.height = self._invis_glyph.height
        self.width = self._invis_glyph.width
        self.ascent = self._invis_glyph.ascent
        self.descent = self._invis_glyph.descent
        self.isWhitespace = 1
        #self.lineHeight = self.height
        self.lineHeight = self._invis_glyph.lineHeight
        
    def generateInvisibleGlyph(self):
        self._invis_glyph = self.doGenerateInvisibleGlyph(self._style)

    def generateSymbolSurface(self):
        size = (self._invis_glyph.width, self._invis_glyph.height)
        symbolKey = (size, self._style)
        if not self.symbol_surfaces.has_key(symbolKey):
            self.symbol_surfaces[symbolKey] = self.doGenerateSymbolSurface(*symbolKey)
        self._symbol_surface = self.symbol_surfaces[symbolKey]

    def doGenerateInvisibleGlyph(self, styleID):
        raise NotImplementedError()

    def doGenerateSymbolSurface(self, size, styleID):
        raise NotImplementedError()

    def render(self):
        # TODO: make isVisible() method for the below class?
        return self._invis_glyph.render()

    def renderWhitespaceSymbol(self):
        return self._symbol_surface

# --------------------------
# The Newline Glyph
# --------------------------

# NewlineGlyph is a concrete subclass of WhitespaceGlyph and implements the display of the newline character.  When not in command quasimode, it is displayed as an ordinary space; when command quasimode is active, it is displayed as a pilcrow (which looks like a backwards "P").

class NewlineGlyph(WhitespaceGlyph):
    symbol_surfaces = {}

    def __generatePilcrowSymbol(self, styleID):
        p_font = globalFontPool.getFont( styleID )
        p_symbol = p_font.render(chr(182))
        p_symbol.setBackgroundToTransparent()
        return p_symbol

    def doGenerateInvisibleGlyph(self, styleID):
        p_symbol = self.__generatePilcrowSymbol(styleID)
        invis_glyph = BlankGlyph(p_symbol.getSize())
        invis_glyph.setGlyphMetrics(FontGlyph(" ", styleID))
        return invis_glyph

    def getChar(self):
        return "\n"

    def doGenerateSymbolSurface(self, size, styleID):
        return self.__generatePilcrowSymbol(styleID)

# --------------------------
# The Space Glyph
# --------------------------

# SpaceGlyph is a concrete subclass of WhitespaceGlyph and implements the display of the space character.  When not in command quasimode, it is displayed as an ordinary space; when command quasimode is active, it is displayed as a centered dot.

class SpaceGlyph(WhitespaceGlyph):
    symbol_surfaces = {}

    DOT_RADIUS = 1
    
    def doGenerateInvisibleGlyph(self, styleID):
        return FontGlyph(" ", styleID)

    def getChar(self):
        return " "

    def doGenerateSymbolSurface(self, size, styleID):
        newSurface = surfaces.PygameSurface( size )
        newSurface.clear()
        newSurface.setBackgroundToTransparent()

        dot_center = (size[0] / 2, size[1] / 2)
        newSurface.drawCircle( dot_center, self.DOT_RADIUS, self.SYMBOL_COLOR )
        return newSurface

# --------------------------
# The Tab Glyph
# --------------------------


# TabGlyph is a concrete subclass of WhitespaceGlyph and implements the display of the tab character.  When not in command quasimode, it is displayed as an ordinary tab; when command quasimode is active, it is displayed as an arrow.

class TabGlyph(WhitespaceGlyph):
    symbol_surfaces = {}

    SPACE_EQUIVALENT = 4
    ARROW_HEIGHT = 2
    ARROW_LENGTH = 4
    ARROW_MARGIN = 1
    WIDTH = 1
    
    def doGenerateInvisibleGlyph(self, styleID):
        return FontGlyph(" "*self.SPACE_EQUIVALENT, styleID)

    def getChar(self):
        return "\t"

    def doGenerateSymbolSurface(self, size, styleID):
        newSurface = surfaces.PygameSurface( size )
        newSurface.clear()
        newSurface.setBackgroundToTransparent()

        start = ( self.ARROW_MARGIN, size[1] / 2)
        end = (size[0] - self.ARROW_MARGIN, size[1] / 2)
        arrowLine1 = ( end[0]-self.ARROW_LENGTH, size[1]/2 + self.ARROW_HEIGHT)
        arrowLine2 = ( arrowLine1[0], size[1]/2 - self.ARROW_HEIGHT)
        newSurface.drawLine( start, end, self.SYMBOL_COLOR, self.WIDTH )
        newSurface.drawLine( arrowLine1, end, self.SYMBOL_COLOR, self.WIDTH )
        newSurface.drawLine( arrowLine2, end, self.SYMBOL_COLOR, self.WIDTH )
        return newSurface
