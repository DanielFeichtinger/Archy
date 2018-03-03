# html_parser.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: html_parser.hpy,v 1.5 2005/04/04 04:04:51 andrewwwilson Exp $"

# This is a temporary module that parses a simple subset of HTML for the purposes of formatting the initial document.  It offers very little error-handling functionality and is not undoable; in the future, it may be used as the basis for the style component of the XML-parsing module.

# Currently, this implementation supports the parsing of the following HTML; any tags or attributes not used in this example are NOT supported by the engine.

# ----

# <DOCUMENT>
# <FONT FACE="Arial" SIZE="24">This is <B>arial</B>.  <FONT COLOR="#0000FF">this is blue</FONT>.</FONT>

# <FONT FACE="Courier New">This <I>is</I> <FONT BGCOLOR="#FF0000">Courier</FONT>.</FONT>

# <BEHAVIOR TYPE="LOCK">This is locked text.</BEHAVIOR>

# Other valid behavior types include 'FINAL DOCUMENT CHARACTER LOCK', 'INITIAL DOCUMENT CHARACTER LOCK', 'SYSTEM LOCK', and 'FORM LOCK'.

# </DOCUMENT>

# ----
from archy_state import archyState

import xml.sax

def htmlColorToTuple(color):
    """Convert a HTML-style color (e.g., "#AABBCC") to a color tuple (e.g., (5,10,255)."""

    components = ( color[1:3], color[3:5], color[5:7] )
    colors = []
    for c in components:
        colors.append( eval( "0x%s" % c ) )
    return tuple(colors)

def getCurrentStyle():
    curPos = archyState.mainText.getCursorPos()
    dummy, styles = archyState.mainText.getStyledText( curPos, curPos )
    styleID = styles[0]

    return archyState.stylePool[styleID]._dict

def setStyle(overlayDict):
    archyState.mainText.setStyleOverlay( overlayDict, archyState.mainText.getCursorPos() )

def getCursorPosition():
    return archyState.mainText.getCursorPos()

def setBehavior(behaviorName, start, end):
    actionVector = archyState.mainText.behaviorArray.getBehavior(behaviorName)
    action = archyState.mainText.behaviorArray.behaviorPool.getActionID(**actionVector)

    archyState.mainText.behaviorArray.addActionInRange(action, start, end)

def addText(text):
    text = preprocessRawText(text)
    archyState.mainText.addTextAtCursor(text)

def addImage(filename):
    import pygame
    newSurface = pygame.image.load(filename)

    imageString = pygame.image.tostring( newSurface, "RGBA")

    styleDict = { 'type':'Image', 'size':100, 'start size':100, \
               'image size':newSurface.get_size(), 'rotate':0, 'image data': imageString}

    currStyle = getCurrentStyle()
    setStyle(styleDict)
    addText('|')
    setStyle(currStyle)

def preprocessRawText(text):
    import xml.sax.saxutils

    text = xml.sax.saxutils.unescape(text)

    text = text.replace('[alt]', chr(31))
    text = text.replace('[backspace]', chr(20))
    text = text.replace('[capslock]', chr(30))
    text = text.replace('[tilde]', chr(29))
    text = text.replace('[return]', chr(28))
    text = text.replace('[down]', chr(27))
    text = text.replace('[up]', chr(19))
    text = text.replace('[left]', chr(21))
    text = text.replace('[right]', chr(22))
    return text

def insertHTMLFile(filename):
    handler = HumaneDocumentContentHander()
    xml.sax.make_parser()
    xml.sax.parse(filename, handler)

class Attributes:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def update(self, attribs):
        self.__dict__.update(attribs.__dict__)

    def apply(self):
        setStyle(self.__dict__)

class BehaviorsStack:
    def __init__(self):
        self.stack = []

    def push(self, name):
        start = getCursorPosition()
        self.stack.append((name, start))

    def pop(self):
        name, start = self.stack.pop()
        end = getCursorPosition()
        setBehavior(name, start, end)

class AttributesStack:
    def __init__(self):
        baseAttribs = Attributes( **getCurrentStyle() )
        self.stack = [baseAttribs]

    def push(self, attribs):
        import copy

        newAttribs = copy.deepcopy( self.stack[-1] )
        newAttribs.update( attribs )
        self.stack.append( newAttribs )
        newAttribs.apply()

    def pop(self):
        self.stack.pop()
        attribs = self.stack[-1]
        attribs.apply()

class HumaneDocumentContentHander(xml.sax.handler.ContentHandler):
    def startDocument(self):
        self.attribStack = AttributesStack()
        self.behStack = BehaviorsStack()

    def endDocument(self):
        pass

    def _startFontElement(self, attrs):
        newAttribs = Attributes()
        if attrs.has_key("FACE"):
            newAttribs.font = attrs["FACE"]
        if attrs.has_key("SIZE"):
            newAttribs.size = int(attrs["SIZE"])
        if attrs.has_key("COLOR"):
            newAttribs.foregroundColor = htmlColorToTuple(attrs["COLOR"])
        if attrs.has_key("BGCOLOR"):
            newAttribs.backgroundColor = htmlColorToTuple(attrs["BGCOLOR"])
        self.attribStack.push(newAttribs)

    def _startBoldElement(self):
        self.attribStack.push( Attributes(bold=1) )

    def _startItalicElement(self):
        self.attribStack.push( Attributes(italic=1) )

    def _startImgElement(self, attrs):
        addImage(attrs["SRC"])

    def startElement(self, name, attrs):
        if name == "FONT":
            self._startFontElement(attrs)
        elif name == "B":
            self._startBoldElement()
        elif name == "I":
            self._startItalicElement()
        elif name == "IMG":
            self._startImgElement(attrs)
        elif name == "BEHAVIOR":
            self.behStack.push(attrs['TYPE'])

    def endElement(self, name):
        if name in ["FONT", "B", "I"]:
            self.attribStack.pop()
        elif name == "BEHAVIOR":
            self.behStack.pop()

    def characters(self, content):
        addText(content)
