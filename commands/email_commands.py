# email_commands.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

import commands
from archy_state import archyState

import email_thread

import messages
import copy
from forms import AddFormCommand

# --- --- ---

class EmailServerForm(AddFormCommand):
    def __init__(self):
        AddFormCommand.__init__(self)

        self.create('Email Address', 'archy@mydomain.com')
        self.create('Incoming Server', 'imap.mydomain.com')
        self.create('Protocol', 'IMAP', ['IMAP', 'POP'])
        self.create('SSL', 'No', ['Yes', 'No'], [True, False])
        self.create('Incoming User', 'Archy')
        self.create('Incoming Password', password = 1)
        self.create('Outgoing Server', 'smtp.mydomain.com')
        self.create('Outgoing Authentication', 'No', ['Yes', 'No'], [True, False])
        self.create('TLS', 'No', ['Yes', 'No'], [True, False])
        self.create('Outgoing User', 'Archy')
        self.create('Outgoing Password', password = 1)

    def name(self):
        return "NEW EMAIL SERVER"

class EmailForm(AddFormCommand):
    def __init__(self):
        AddFormCommand.__init__(self)
        self.create('To')
        self.create('CC')
        self.create('Subject')
        self.create('Body', multiline = 1)
        self.border('~')

    def name(self):
        return "NEW EMAIL"

class RecievedEmailForm(AddFormCommand):
    def __init__(self):
        AddFormCommand.__init__(self)
        self.create('From')
        self.create('To')
        self.create('CC')
        self.create('Subject')
        self.create('Body', multiline = 1)
        self.border('~')

    def name(self):
        return "RecievedEmailForm"

def getEmailServerInformation():
    import email_thread

    start = archyState.mainText.textArray.find('`E M A I L   S E T T I N G S', 0)
    end   = archyState.mainText.textArray.find('E N D   O F   E M A I L   S E T T I N G S', 0)
    text, style = archyState.mainText.getStyledText(start, end)

    form = EmailServerForm()
    form.parse(text, start)

    return form

class SendEmailCommand(commands.CommandObject):
    def name(self):
        return "SEND"
        
    def recordable(self):
        return False

    def execute(self):
        import email.Message
        selRange = archyState.mainText.getSelection('selection')
        text, style = archyState.mainText.getStyledText(*selRange)
        text = filter(lambda x: x <> '~', text)
        
        serverForm = getEmailServerInformation()
        emailForm = EmailForm()
        emailForm.parse(text)

        bodyTag = 'Body:'
        bodyStart = text.find(bodyTag)
        text[bodyStart+len(bodyTag):]
        msg = email.Message.Message()
        msg.set_payload( text[bodyStart+len(bodyTag):] )
        msg['To'] = emailForm['To']
        msg['CC'] = emailForm['CC']
        msg['Subject'] = emailForm['Subject']

        newServerInfo = { 'server': serverForm['Outgoing Server'], 'authentication':serverForm['Outgoing Authentication'] , 'From':serverForm['Email Address'], 'password':serverForm['Outgoing Password'], 'user':serverForm['Outgoing User'], 'TLS':serverForm['TLS']}
        email_thread.outgoing_servers_lock.acquire()
        email_thread.outgoing_servers = [ newServerInfo ]
        email_thread.outgoing_servers_lock.release()

        email_thread.outgoing_email_lock.acquire()
        email_thread.outgoing_email.append( msg )
        email_thread.is_outgoing_mail.set()
        email_thread.outgoing_email_lock.release()
        
        messages.queue('Email sent successfully', 'normal')
        
        

class GetEmailCommand(commands.CommandObject):
    def name(self):
        return "GET EMAIL"

    def updateServerInformation(self):
        serverForm = getEmailServerInformation()
        newServerInfo = { 'protocol':serverForm['Protocol'], 'server': serverForm['Incoming Server'], 'user':serverForm['Incoming User'],\
                  'password':serverForm['Incoming Password'], 'SSL':serverForm['SSL']}

        email_thread.incoming_servers_lock.acquire()
        email_thread.incoming_servers = [ newServerInfo ]
        email_thread.incoming_servers_lock.release()
        email_thread.server_settings_changed.set()

    def writeEmail(self, msg):
        newEmail = archyState.commandMap.findSystemCommand('RecievedEmailForm')
        newEmail['From'] = msg['From']
        newEmail['To'] = msg['To']
        newEmail['Subject'] = msg['Subject']
        if not msg.is_multipart():
            newEmail['Body'] = filter(lambda x:x <> '\r', msg.get_payload())


        self.history = []
        
        cmd = archyState.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( '`E M A I L \n') 
        self.history.append(cmd)

        cmd = archyState.commandMap.findSystemCommand('LEAP forward to:')
        cmd.setinfo( '\n')
        self.history.append(cmd)
        
        self.history.append( cmd = archyState.commandMap.findSystemCommand('CreepRight') )

        cmd = archyState.commandMap.findSystemCommand('AddText')
        cmd.setinfo('\n' + newEmail.text() ) 
        self.history.append(cmd)
        
        self.history.append( archyState.commandMap.findSystemCommand('LOCK') )
        self.history.append( archyState.commandMap.findSystemCommand('CreepRight') )

        for i in self.history:
            archyState.commandHistory.executeCommand( i )


    def execute(self):
        self.updateServerInformation()

        email_thread.check_mail_now.set()

        email_thread.incoming_email_lock.acquire()
        newMessages = email_thread.incoming_email
        email_thread.incoming_email = []
        email_thread.incoming_email_lock.release()

        for msg in newMessages:
            self.writeEmail(msg)

    def undo(self):
        pass

SYSTEM_COMMANDS = [EmailServerForm, RecievedEmailForm]
COMMANDS = [EmailForm, SendEmailCommand, GetEmailCommand]
BEHAVIORS = []
