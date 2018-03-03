# surfaces.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: surfaces.hpy,v 1.16 2005/03/21 20:48:22 varmaa Exp $"

import drawing_surface
import text_abstract
import pygame

class PygameSurface(drawing_surface.DrawingSurface):
    def __init__(self, widthHeight=None, surface=None):
        if surface == None:
            widthHeight = ( int(widthHeight[0]), int(widthHeight[1]) )
            self.pygameSurface = pygame.Surface(widthHeight)
        else:
            self.pygameSurface = surface
        self.rect = self.pygameSurface.get_rect()
        self._backgroundColor = [255,255,255]
        #print "I did __init__"

    def getSize(self):
        return self.pygameSurface.get_size()
    
    def getHeight(self):
        return self.pygameSurface.get_height()
        
    def getWidth(self):
        return self.pygameSurface.get_width()

    def setAlpha(self, alpha):
        self.pygameSurface.set_alpha(alpha)

    def setBackgroundColor(self, color):
        self._backgroundColor = color
    
    def clear(self):
        self.pygameSurface.fill( self._backgroundColor)

    def drawCircle(self, center_pos, radius, color):
        pygame.draw.circle(self.pygameSurface, color, center_pos, radius)

    def drawLine(self, start, end, color, width = 1):
        pygame.draw.line(self.pygameSurface, color, start, end, width)

    def drawRectangle(self,widthHeight,xyPos,color,alpha):
        # TODO: This is very slow can can be done more efficiently.
        newSurface = pygame.Surface(widthHeight)
        newSurface.fill(color)
        newSurface.set_alpha(alpha)
        self.pygameSurface.blit(newSurface,xyPos)
    
    def fillRectangle(self,rect, color):
        self.pygameSurface.fill(color, rect)

    def fill(self, color):
        self.pygameSurface.fill( color )

    def setColorKey(self, color):
        self.pygameSurface.set_colorkey(color)

    def setBackgroundToTransparent(self):
        self.pygameSurface.set_colorkey(self._backgroundColor)

    def blitRectangle(self, surface, (ypos,xpos) ):
        self.pygameSurface.blit( surface.pygameSurface, [ypos,xpos] )

