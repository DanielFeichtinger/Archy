# text_layers.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

VERSION = "$Id: archy_state.hpy,v 1.1 2005/04/04 04:04:54 andrewwwilson Exp $"

# This module holds all text layers

# --------------------------
# Module imports
# --------------------------


class ArchyState:
    def __init__(self):
        self.screenSurface = None
        
        self.mainText = None
        self.mainTextViewer = None
        self.quasiModeText = None
        self.quasiModeTextViewer = None
        
        self.whitespaceVisible = False
        self.preselectionVisible = False
        
        self.stylePool = None
        
        self.commandMap = None
        self.commandHistory = None
        
        self.keyState = None
        self.userDirectory = None

# This is the primary initialization function that sets up the various text layers.
    def init(self, screen):
        import autorepeat
        self.autorepeater = autorepeat.Autorepeater()

        import commands
        self.commandMap = commands.CommandMap()
        self.commandHistory = commands.CommandHistory()
        
        import key
        self.keyState = key.GlobalState()
        
        
        import style
        self.stylePool = style.StylePool()
        
        self.bindToScreen(screen)
        self._initMainTextLayer()
        self._initQuasiModeTextLayer()
        
        self.keyState.start()
        self.loadContent()
    
    def bindToScreen(self, screen = None):
        self.screenSurface = screen
# TO DO: initialize text viewers and documents

    def releaseScreen(self):
        self.screenSurface = None
# TO DO: suspend blitting to self.screen

    def showWhitespace(self):
        self.whitespaceVisible = True
    def hideWhitespace(self):
        self.whitespaceVisible = False
    def showPreselection(self):
        self.preselectionVisible = True
    def hidePreselection(self):
        self.preselectionVisible = False

    def _initMainTextLayer(self):
        print "init MainTextLayer"
        
        import text_abstract
        import text_viewer
        self.mainText = text_abstract.HumaneDocumentText()
        self.mainTextViewer = text_viewer.HumaneDocumentTextViewer(self.mainText, self.screenSurface)

    def _initQuasiModeTextLayer(self):
        winSize = self.screenSurface.getSize()

        import text_abstract
        import text_viewer
        print "init quasiModeTextLayer"
        self.quasiModeText = text_abstract.CommandMessageText()
        qmtWidth, qmtHeight = winSize[0]/1.15, winSize[1]
        qmtPosX, qmtPosY = (winSize[0]-qmtWidth), 0 
        self.quasiModeTextViewer = text_viewer.CommandMessageViewer(self.quasiModeText, self.screenSurface, [qmtWidth, qmtHeight])
        self.quasiModeTextViewer.setPosition([qmtPosX, qmtPosY])

        import platform_specific

        quasiModeStyle = self.stylePool.newStyle(**platform_specific.Quasimode_Font)
        self.quasiModeText.styleArray.setDefaultStyle(quasiModeStyle)

    def createInitialContent(self):
        import commands
        import platform_specific
        mainTextStyle = self.stylePool.newStyle(**platform_specific.Default_Font)
        self.mainText.styleArray.setDefaultStyle(mainTextStyle)

        self.mainText.addTextAtCursor("`")

        import html_parser
        html_parser.insertHTMLFile("initial_document.txt")

        cursPos = self.mainText.getCursorPos()
        self.mainText.setSelection('preselection', cursPos, cursPos)
        self.mainText.createNewSelection(cursPos,cursPos)
        
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( '`D E L E T I O N S ')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "\n")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('Select')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LOCK')
        self.commandHistory.executeCommand( cmd )

        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "E N D   O F   D E L E T I O N S ")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "\n")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('Select')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LOCK')
        self.commandHistory.executeCommand( cmd )
        
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "`E M A I L ")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "\n")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('Select')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LOCK')
        self.commandHistory.executeCommand( cmd )
        
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "E N D   O F   E M A I L ")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "\n")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('Select')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LOCK')
        self.commandHistory.executeCommand( cmd )

        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "`E M A I L   S E T T I N G S ")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "\n")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('Select')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LOCK')
        self.commandHistory.executeCommand( cmd )

        cmd = self.commandMap.findSystemCommand('NEW EMAIL SERVER')
        self.commandHistory.executeCommand( cmd )
    
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "E N D   O F   E M A I L   S E T T I N G S ")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "\n")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('Select')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LOCK')
        self.commandHistory.executeCommand( cmd )

        cmd = self.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( "``````")
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('FinalDocumentLock')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('LEAP backward to:')
        cmd.setinfo( '``````')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('InitialDocumentLock')
        self.commandHistory.executeCommand( cmd )
        cmd = self.commandMap.findSystemCommand('CreepRight')
        self.commandHistory.executeCommand( cmd )
        
        cmd = self.commandMap.findSystemCommand('CLEAR UNDO HISTORY')
        self.commandHistory.executeCommand( cmd )
        
        
        commands.save_and_load.saveState()

    def loadContent(self):
        import commands
        response = commands.save_and_load.loadState()
        if response == "Humane Document file does not exist.":
            print "There was no Humane Document; using the default text."
            self.createInitialContent()
        elif response == "Error loading Humane Document.":
            print "The Humane Document did not load correctly.  Please open the file in a text editor, and recover any text you need.  Then delete the Humane Document file, and restart Archy."
            raise SystemExit()
        elif response == "Loaded file correctly.":
            print "The Humane Document seemed to load correctly."



archyState = ArchyState()
