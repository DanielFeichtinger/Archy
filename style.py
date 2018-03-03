# style.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: style.hpy,v 1.16 2005/04/04 04:04:53 andrewwwilson Exp $"

import copy

NOT_FOUND = -1



# -------------------------------------
# Style Class
# -------------------------------------

# There are two types of objects used for controlling styling.

# The style object:

# When a "style" is created via the newStyle function, it returns an
# integer which encodes all of the information about how a particular
# character will look (font, size, bolded-ness, color, etc.). Any
# information not specifically set during the creation of a "style"
# defaults to a default value, as defined in the Style class __init__
# function.  Thus, when you set a range of text to a "style" it
# overwrites all previous style settings.

# The styleOverlay object:

# When a styleOverlay is created it returns a dictionary which contains
# all of the appropriate styling information set during
# instantiation. When a style overlay is applied to a range of text,
# only the style information specified by the style overlay is
# changed. Thus, if you had a range of text in multiple fonts and used
# an overlay defined by newStyleOverlay(bold = 1) then you would now
# have a range of text in multiple bold fonts.

class Style:
    def __init__(self):

        self._dict = {}
        self._dict['type'] = "Font"
        self._dict['font'] = "Courier New"
        self._dict['size'] = 16
        self._dict['italic'] = 0
        self._dict['bold'] = 0
        self._dict['underline'] = 0
        self._dict['outline'] = 0
        self._dict['backgroundColor'] = 255,255,255
        self._dict['foregroundColor'] = 0,0,0
        #self._dict['attributes'] = []

    def setAttribute(self, attributeName, value):
        self._dict[attributeName] = value

    def get(self, attributeName):
        if attributeName not in self._dict.keys():
            raise "'%s' is not a style attribute name." % attributeName
        return self._dict[attributeName]

    def listAttributes(self):
        return self._dict.keys()

    def getAttributes(self):
        return self._dict

    def setStyle(self, **args):
        for attribute in args.keys():
            if attribute not in self.listAttributes():
                raise "'%s' is not a style attribute name." % attribute
        
            value = args[attribute]
            self.setAttribute(attribute, value)
#end class


# -------------------------------------
# StylePool
# -------------------------------------


# Style Pool defines the set of styles that are in use throughout
# Archy. As of the Alpha versions, these will be used by StyleContents
# for main text and translucent text layers.

# The idea is to reduce the copies of Style objects in the system
# as in the Flyweight Design Pattern. The StylePool will contain the
# different Style objects that are actually in use.

class StylePool( list ):
    def __init__(self):
        list.__init__(self)
# Add the default style. It gets the special honor of being assigned
# the smallest natural number as an ID number: 0.
        defaultStyle = Style()
        self.append(defaultStyle)
        
    def newStyle(self, **dict):
        #There are two ways for newStyle to be called.
        # 1) A dictionary can be passed in of the form {'font':'Times', 'bold':1}
        #    This form allows for a function to be called as keyword arguments. For
        #    instance, mainText.addText('new text', pos, font='Times', bold=1)
        # 2) A dictionary with a single keyword of 'style' can be passed in. This
        #    allows for a dictionary with the wanted style information to be created
        #    outside of the function call (say for repeated use). For instance
        #    styleDef = {'font':'Times', 'bold':1}
        #    mainText.addText('new text', pos, style = styleDef)

        if dict.has_key('style'): 
            dict = dict['style']
        
        newStyle = Style()
        for key in dict.keys():
            newStyle.setAttribute(key, dict[key])
        style_index = self._findStyle(newStyle)
        if style_index <> NOT_FOUND:
            return style_index

        self.append(newStyle)
        return len(self)-1

    def newStyleOverlay(self, **dict):
        #See the note about the two different methods for calling
        #newStyle(). It applies to this function.
        if dict.has_key('style'): 
            dict = dict['style']
        return dict

# The next function is for internal use within the style module and text_abstract.
# A developer who is writing code that deals with text styles should not have to
# care about the specific implementation outline within this module. They should
# never deal directly with modifying style IDs, for instance. This function is the
# mechanism that modifies an existing style by replacing the appropriate styling
# information with that of the style overlay. The function is smart enough to
# realize if the resulting style has already been used and is carefully about
# minimizing the style pool.

    def mergeStyleWithOverlay(self, oldStyleNum, overlay):
        #Get the style on which the modified style is based and then modify it.
        #We use deepcopy to assure the style variable is not just a pointer
        #to the Style object held in the StylePool list.
        theStyle = copy.deepcopy(self[oldStyleNum])

        for att in overlay:
            theStyle.setAttribute(att, overlay[att])

        #Find if this new style already exists in our list, if it does just return
        #the ID of that style
        style_index = self._findStyle(theStyle)
        if style_index <> NOT_FOUND:
            return style_index

        #Add this as-of-now unique style to our list of styles and return its ID
        #which is its position in the list.
        self.append(theStyle)
        #print "mergeWithStyleOverlay:",overlay
        #print "style pool len=",len(StylePool)
        return len(self)-1

    def _findStyle(self, theStyle):
        for i in range(len(self)):
            if theStyle.getAttributes() == self[i].getAttributes():
                return i
        return NOT_FOUND




# -------------------------------------
# StyleArray Class
# -------------------------------------


# Until the bugs get sorted out, use a regular list.
#from run_length_list import RLE_List

# The next class uses the StylePool[] index numbers as the value assosciated with each position.

class StyleArray:
    def __init__(self, associatedTextArray = None, defaultStyleNumber = 0):
# Until the bugs get sorted out, use a regular list.
        self._styleNumbers = []
        #self._styleNumbers = RLE_List()
        
        self.defaultStyle = defaultStyleNumber
        if associatedTextArray:
            for i in range(associatedTextArray.getLength()):
                    self._styleNumbers.insert(i, defaultStyleNumber)

    def clear(self, associatedTextArray ):
        del self._styleNumbers
# Until the bugs get sorted out, use a regular list.
        self._styleNumbers = []
        #self._styleNumbers = RLE_List()
        if associatedTextArray:
            for i in range(associatedTextArray.getLength()):
                    self._styleNumbers.insert(i, self.defaultStyle)

    def isValidPos(self, pos):
        if 0<= pos and pos < self.getLength():
            return True
        return False

    def setStyleInRange(self, styleID, startPos, endPos):
        #Remember that python uses slices... we don't. We need to add one to the endPos.
        self._styleNumbers[startPos:endPos+1] = [styleID] * (endPos+1-startPos)

    def getDefaultStyle(self):
        return self.defaultStyle

    def setDefaultStyle(self, styleID):
        self.defaultStyle = styleID
        #The slice insures that whatever type of object _styleNumbers is (it might be
        #a re-implementation of list) it will not be replaced by a list object.
        self._styleNumbers[:] = [styleID] * len(self._styleNumbers)

    def getLength(self):
        return len(self._styleNumbers)

    def getStyles(self):
        return self._styleNumbers

    def getCharStyle(self,position):
        if position < 0 or self.getLength()-1 < position:
            return self.defaultStyle
        return self._styleNumbers[position]

    def setCharStyle(self, position, styleID):
        if position < 0 or self.getLength()-1 < position:
            return
        self._styleNumbers[position] = styleID

    def getSubString(self, startPos, endPos):
        return self._styleNumbers[startPos:endPos+1]

    def replaceStyles(self, styleString, insertPos):
        self._styleNumbers[insertPos:insertPos+len(styleString)] = styleString

    def addText(self, newString, insertPos, styleID = None):
        if insertPos < 0 or len(self._styleNumbers)-1 < insertPos :
            insertPos = -1
        if styleID == None:
            if self.getLength() > 0:
                styleID = self.getCharStyle(insertPos)
            else:
                styleID = self.defaultStyle
        self._styleNumbers[insertPos:insertPos] = [styleID] * len(newString)

    def delText(self, start, end):
        if end < start:
            return
        if len(self._styleNumbers) - 1 < start:
            return
        if end < 0:
            return
        if start < 0:
            start = 0
        
        if len(self._styleNumbers) - 1 < end:
            end = len(self._styleNumbers) - 1

        del self._styleNumbers[start:end+1]
