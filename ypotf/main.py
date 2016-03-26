import imaplib

from . import processors
from .subject import categorize

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    M.select('INBOX')
    for num, m in processors.messages(M):
        f = {
            'subscribe': processors.subscribe,
            'unsubscribe': processors.unsubscribe,
            'confirm': processors.confirm,
#           'archive': processors.,
#           'help': processors.,
            'message': processors.,
        }[categorize(m['subject'])]
        f(M, num)
    M.logout()
