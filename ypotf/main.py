import imaplib

from . import processors

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    M.select('INBOX')
    for num, m in processors.messages(M):
        u
    M.logout()
