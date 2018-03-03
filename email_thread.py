# email_thread.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import time
import email
import imaplib
import poplib_2_4 as poplib
import smtplib

class ServerError(Exception):
    pass
class UserPasswordError(Exception):
    pass


class EmailServerObject:
    def __init__(self, serverDict = None):
        self._isInitialized = False
        self.setServerInfo( serverDict )

    def _pingServer(self):
        raise NotImplementedError()
        
    def getServerInfo(self):
        return self._serverDict
        
    def setServerInfo(self, newDict = None):
        self._serverDict = newDict
        try:
            self._initializeServer()
        except ServerError():
            pass
        #except:
            #return False
        return True         

    def getMail(self):
        if self._serverDict.has_key('mailboxes'):
            mailboxes = self._serverDict['mailboxes']
        else:
            mailboxes = ['INBOX']
        messages = []
        for i in mailboxes:
            messages += self._getMail( i )
        return messages


    def _isServerInfoValid(self):
        raise NotImplementedError()
    def _initializeServer(self):
        raise NotImplementedError()
    def releaseServer(self):
        raise NotImplementedError()
    def _getMail(self, mailBox = None):
        raise NotImplementedError()
    def _getNewMail(self, sinceTime, mailBox):
        raise NotImplementedError()
    def keepAlive(self):
        raise NotImplementedError()



class IMAPEmail(EmailServerObject):         
    def _isServerInfoValid(self):
        pass
        #raise NotImplementedError()
        
    def _initializeServer(self):
        if self._serverDict == None:
            raise Exception("No server to initialize!")
        if not self._isServerInfoValid:
            raise Exception("Server info is not valid!")
        
        if self._isInitialized:
            self.releaseServer()
        
        if self._serverDict.has_key('SSL') and self._serverDict['SSL']:
            IMAPabstract = imaplib.IMAP4_SSL
        else:
            IMAPabstract = imaplib.IMAP4
        server = self._serverDict['server']
        if self._serverDict.has_key( 'port' ):
            port = self._serverDict['port']
            try:
                newIMAP = IMAPabstract( server , port )
            except:
                #print "exception", 1
                raise ServerError()
        else:
            try:
                newIMAP = IMAPabstract( server )
            except:
                #print "exception", 2
                raise ServerError()
            
        self._IMAP = newIMAP
        try:
            self._IMAP.login( self._serverDict['user'], self._serverDict['password'] )
        except:
            #print "exception",3
            raise UserPasswordError()
        self._isInitialized = True
            
    def releaseServer(self):
        if self._isInitialized:
            self._IMAP.close()
            self._IMAP.logout()
            del self._IMAP
        self._isIntialized = False
        
    def _getMail(self, mailBox = None):
        if mailBox == None:
            mailBox = "INBOX"
        if not self._isInitialized:
            try:
                self._initializeServer()
            except:
                #print "exception",4
                return None
        if self._serverDict.has_key('last checked time'):
            return self._getNewMail( self._serverDict['last checked time'], mailBox)
        else:
            return self._getNewMail( imaplib.Time2Internaldate( time.gmtime(0) ), mailBox)

    def _getNewMail(self, sinceTime, mailBox):
        self._IMAP.select( mailBox )
        toSearchFor = sinceTime[:12]+sinceTime[-1:]
        #if toSearchFor == imaplib.Time2Internaldate( time.localtime())[:12] +'"':
        if 1:
            toSearchFor = "UNSEEN"
        else:
            toSearchFor = "(SINCE "+toSearchFor + ")"
        typ, data = self._IMAP.search( None, toSearchFor )
        messages = []
        for num in data[0].split():
            typ, data = self._IMAP.fetch(num, 'RFC822')
            message = email.message_from_string( data[0][1] )
            messages.append(message)
        messages.reverse()

        self._serverDict['last checked time'] = imaplib.Time2Internaldate( time.localtime() )
        return messages
        
    def keepAlive(self):
        if self._isInitialized:
            try:
                self._IMAP.noop()
            except:
                #print "exception",5
                self._isInitialized = False
        
class POPemail(EmailServerObject):
    def _initializeServer(self):
        if self._serverDict == None:
            raise Exception("No server to initialize!")
        if not self._isServerInfoValid:
            raise Exception("Server info is not valid!")
        
        if self._isInitialized:
            self.releaseServer()
        
        if self._serverDict.has_key('SSL') and self._serverDict['SSL']:
            POPabstract = poplib.POP3_SSL
        else:
            POPabstract = poplib.POP3
        server = self._serverDict['server']
        if self._serverDict.has_key( 'port' ):
            port = self._serverDict['port']
            try:
                newPOP = POPabstract( server , port )
            except:
                #print "exception",6
                raise ServerError()
        else:
            try:
                newPOP = POPabstract( server )
            except:
                #print "exception",7
                raise ServerError()
            
        self._POP = newPOP
        try:
            self._POP.user( self._serverDict['user'] )
            self._POP.pass_( self._serverDict['password'])
        except:
            #print "exception",8
            raise UserPasswordError()
        self._isInitialized = True
            
    def releaseServer(self):
        if self._isInitialized:
            self._POP.quit()
        self._isIntialized = False
        
    def _getMail(self, noPOPmailboxes):
        if not self._isInitialized:
            try:
                self._initializeServer()
            except:
                #print "failed server start-POP"
                return None
        return self._getNewMail()

    def _getNewMail(self):
        messages = []
        for i in range( len(self._POP.list()[1]) ):
            #print "another message"
            rawText = ""
            for j in self._POP.retr(i+1)[1]:
                rawText += (j+"\n")
            messages.append( email.message_from_string(rawText) )
        return messages
        
    def keepAlive(self):
        if self._isInitialized:
            try:
                self._POP.noop()
            except:
                #print "exception",9
                self._isInitialized = False
        
class SMTPserver:           
    def __init__(self, serverDict = None):
        self._isInitialized = False
        self.setServerInfo( serverDict )

    def _pingServer(self):
        raise NotImplementedError()
        
    def getServerInfo(self):
        return self._serverDict
        
    def setServerInfo(self, newDict = None):
        self._serverDict = newDict
        try:
            self._initializeServer()
        except ServerError():
            pass
        #except:
            #return False
        return True         
        
    def _isServerInfoValid(self):
        return ( self._serverDict.has_key('From') and self._serverDict.has_key('server') )
        
    def _initializeServer(self):
        if self._serverDict == None:
            raise Exception("No server to initialize!")
        if not self._isServerInfoValid:
            raise Exception("Server info is not valid!")

        if self._isInitialized:
            self._releaseServer()

        #print self._serverDict
        server = self._serverDict['server']
        if self._serverDict.has_key( 'port' ):
            port = self._serverDict['port']
            try:
                newSMTP = smtplib.SMTP( server , port )
            except:
                #print "exception",10
                raise ServerError()
        else:
            try:
                newSMTP = smtplib.SMTP( server )
            except:
                #print "exception",11
                raise
                raise ServerError()
        
        
        self._SMTP = newSMTP
        if self._serverDict.has_key('TLS') and self._serverDict['TLS'] == True:
            try:
                self._SMTP.ehlo()
                self._SMTP.starttls()
                self._SMTP.ehlo()
            except:
                #print "exception",12
                raise ServerError()

        if self._serverDict.has_key('authentication') and self._serverDict['authentication']:
            try:
                self._SMTP.login( self._serverDict['user'], self._serverDict['password'] )
            except:
                #print "exception",13
                raise #UserPasswordError()

        self._isInitialized = True
            
        
    def _releaseServer(self):
        if self._isInitialized:
            self._SMTP.quit()
            del self._SMTP
        self._isInitialized = False
        
    def sendMessage(self, msg):
        msg['From'] = self._serverDict['From']
        if not self._verifyMessage(msg):
            raise Exception("Not a valid message.")
        messageText = msg.as_string()
        try:
            self._initializeServer()
        except:
            #print "exception",14
            #TO DO: use the standard exception
            raise
            #raise Exception("Could not access SMTP server.")
        try:
            print self._SMTP.sendmail( msg['From'], msg['To'], messageText )
        except:
            #TO DO: not sure what to do here
            raise
        
        try:
            self._releaseServer()
        except:
            #TO DO: this should eventually be a pass
            raise
        
        
    def _constructText(self, msg):
        messageText = ""
        for i in msg:
            if msg[i] <> 'body':
                messageText += (i+": " + msg[i] + "\r\n")
        messageText += msg['body']
        return messageText

    def _verifyMessage(self, msg):
        #TO DO: make sure that the address makes sense.
        return (msg.has_key('From') and msg.has_key('To'))




import threading

global incoming_email_lock,incoming_email,outgoing_email_lock,outgoing_email
incoming_email_lock = threading.Lock()
incoming_email = []
outgoing_email_lock = threading.Lock()
outgoing_email = []

global server_settings_changed,check_mail_now   
server_settings_changed = threading.Event()
check_mail_now = threading.Event()

global incoming_servers_lock,incoming_servers,outgoing_servers_lock,outgoing_servers
incoming_servers_lock = threading.Lock()
incoming_servers = []
outgoing_servers_lock = threading.Lock()
outgoing_servers = []

is_incoming_mail = threading.Event()
is_outgoing_mail = threading.Event()

global system_quit
system_quit = threading.Event()
system_quit.clear()


class IncomingEmailThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global incoming_servers, incoming_servers_lock
        incoming_servers_lock.acquire()
        self._servers = incoming_servers
        incoming_servers_lock.release()
        self._settingsChanged = True
        self._serverLogonFailed = []
        self._serverObjects = []
        
    def run(self):
        while 1:
            global server_settings_changed, system_quit
            if system_quit.isSet():
                break
            #TO DO: this is a very inefficient way of doing this, but very stable; maybe a more elegant method?
            if server_settings_changed.isSet():
                global incoming_servers, incoming_servers_lock
                incoming_servers_lock.acquire()
                self._servers = incoming_servers
                server_settings_changed.clear()
                incoming_servers_lock.release()
            for i in range( len(self._serverObjects) ):
                try:
                    self._serverObjects[i].releaseServer()
                except:
                    #print "exception", 20
                    pass
                del self._serverObjects[i]
            for j in self._servers:
                try:
                    if j['protocol'] == 'IMAP':
                        self._serverObjects.append( IMAPEmail(j) )
                    if j['protocol'] == 'POP':
                        self._serverObjects.append( POPemail(j) )
                    self._serverLogonFailed.append( False )
                except:
                    self._serverLogonFailed.append( True )
            newMessages = []
            for j in self._serverObjects:
                newMessages += j.getMail()

            print "received ", len(newMessages)," messages"

            global is_incoming_mail
            if len(newMessages) > 0:
                global incoming_email, incoming_email_lock
                incoming_email_lock.acquire()
                incoming_email += newMessages
                incoming_email_lock.release()
                is_incoming_mail.set()
                
            global check_mail_now
            check_mail_now.wait(30)
            print "receivemail thread woken up"
            if check_mail_now.isSet():
                check_mail_now.clear()
            #for i in self._serverObjects:
                #i.keepAlive()


class OutgoingEmailThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._settingsChanged = True
        self._serverObjects = []

    def run(self):
        newMessages = []
        while 1:
            global server_settings_changed, is_outgoing_mail, system_quit
            if system_quit.isSet():
                break
            
            
            global outgoing_servers, outgoing_servers_lock
            global outgoing_email, outgoing_email_lock
            
            is_outgoing_mail.wait(180)
            print 'sendmail thread woken up'

            outgoing_email_lock.acquire()
            if len(outgoing_email) > 0:
                newMessages = outgoing_email
                outgoing_email = []
            else:
                newMessages = []
            outgoing_email_lock.release()
                
            if len(newMessages) > 0:
                outgoing_servers_lock.acquire()
                self._servers = outgoing_servers
                outgoing_servers_lock.release()
                
                newServer = None
                for j in self._servers:
                    try:
                        newServer = SMTPserver( j )
                        break
                    except:
                        pass
                if newServer:
                    for i in newMessages:
                        try:
                            newServer.sendMessage(i)
                        except Exception, e:
                            outgoing_email.append( i )
                else:
                    outgoing_email_lock.acquire()
                    outgoing_email.extend( newMessages )
                    outgoing_email_lock.release()
            is_outgoing_mail.clear()
            print outgoing_email
                    

incomingThread = IncomingEmailThread()
outgoingThread = OutgoingEmailThread()
