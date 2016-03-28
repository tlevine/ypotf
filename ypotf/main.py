import imaplib
import os

from .storage import first_message, MAILBOXES
from .processors import process

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    for name in MAILBOXES.values():
        M.create(name)
    while True:
        M.select('INBOX')
        num, m = first_message(M)
        if m:
            process(M, num, m)
            M.close()
        else:
            M.close()
            break
    M.logout()

def cli():
    ypotf('mail.gandi.net', '_@dada.pink', os.environ['PASSWORD'])
#   import horetu
#   horetu.horetu(ypotf)
