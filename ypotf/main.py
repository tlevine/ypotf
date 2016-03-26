import imaplib

from . import processors
from . import parsers

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    for num, m in processors.list_messages(M):
        M.select('INBOX')
        process(M, num, m)
    M.expunge()
    M.logout()
