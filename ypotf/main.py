import imaplib

from . import processors
from . import parsers

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    for num, m in processors.messages(M):
        M.select('INBOX')
        M.copy(num, 'ypotf-archive')
        f, p = process(num, m)
        f(M, p(num))
    M.expunge()
    M.logout()

def process(num, m):
    return {
        'subscribe': (processors.subscribe, parsers.email_address),
        'unsubscribe': (processors.unsubscribe, parsers.email_address),
        'confirm': (processors.confirm, parsers.confirmation_code),
#       'archive': (processors.,),
        'help': (processors.help, parsers.date),
        'message': (processors.send_message, parsers.message_id),
    }[parsers.subject(m)]
