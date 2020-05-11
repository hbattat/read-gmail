import imaplib
import email
import re


class GmailIMAP4_SSL(imaplib.IMAP4_SSL):
    def __init__(self, host='imap.gmail.com', port=imaplib.IMAP4_SSL_PORT,
                 keyfile=None, certfile=None):
        imaplib.IMAP4_SSL.__init__(self, host, port, keyfile, certfile)

        imaplib.Commands['XLIST'] = ('AUTH', 'SELECTED')
        imaplib.Commands['ID'] = ('AUTH')

    def id(self, *args):
        ''' Provide app information to the server,
            and get information in return'''
        arg = '("' + '" "'.join(args) + '")'
        name = 'ID'
        typ, dat = self._simple_command(name, arg)
        return self._untagged_response(typ, dat, name)

    def xlist(self, directory='""', pattern='*'):
        '''List mailbox names in directory matching pattern.
           (typ, [data]) = <instance>.xlist(directory='""', pattern='*')
           'data' is list of XLIST responses.
        '''
        name = 'XLIST'
        typ, dat = self._simple_command(name, directory, pattern)
        return self._untagged_response(typ, dat, name)

    def special_folders(self):
        ''' return a dictionary of localized Gmail special folders '''
        path = {}
        for entry in self.xlist()[1]:
            for name in ('Inbox', 'Starred', 'Sent', 'Drafts',
                         'Spam', 'AllMail'):
                if re.search(' .%s\\)' % name, entry):
                    path[name] = re.search(r'\"([^\"]+)\"$', entry).group(1)
        return path

    def uid2msgid(self, uid):
        ''' Convert an IMAP UID to a Gmail MSGID '''
        typ, data = self.uid('fetch', uid, '(X-GM-MSGID)')
        msgid_dec = re.search('X-GM-MSGID ([0-9]+)', data[0]).group(1)
        msgid_hex = hex(int(msgid_dec))
        return msgid_hex[2:]

    def uid2thrid(self, uid):
        ''' Convert an IMAP UID to a Gmail MSGID '''
        typ, data = self.uid('fetch', uid, '(X-GM-THRID)')
        thrid_dec = re.search('X-GM-THRID ([0-9]+)', data[0]).group(1)
        thrid_hex = hex(int(thrid_dec))
        return thrid_dec

    def mark_as_read(self, uid):
        ''' Reads the message '''
        typ, data = self.fetch(uid, '(RFC822)')
        return typ, data
