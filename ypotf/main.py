import imaplib

from . import processors
from . import parsers

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    for num, m in processors.list_messages(M):
        M.select('INBOX')
        M.copy(num, 'ypotf-archive')
        f, p = process(num, m)
        f(M, p(m))
    M.expunge()
    M.logout()

def process(num, m):
    return {
        'subscriptions': (processors.subscriptions, lambda m: m),
        'confirm': (processors.confirm, parsers.confirmation_code),
#       'archive': (processors.,),
        'help': (processors.help, parsers.date),
        'message': (processors.message, parsers.message_id),
    }[parsers.subject(m)]
