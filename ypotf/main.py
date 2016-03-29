import imaplib
import os
import logging

from .storage import first_message, MAILBOXES, Subscribers
from .processors import process
from .template import send

logger = logging.getLogger(__name__)

IGNORE_MISSING_HEADERS = \
    'Ignoring a message because it lacks the right headers'
IGNORE_FROM_SELF = '''Ignoring message %(message-id)s
because it was sent from %(from)s'''

def ypotf(host:str, address:str, password:str):
    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)
    for name in MAILBOXES.values():
        M.create(name)
    while True:
        M.select('INBOX')
        num, m = first_message(M)
        if m:
            if not 'from' in m and 'message-id' in m:
                logger.warning(IGNORE_MISSING_HEADERS)
            elif m['from'].rstrip('> \n\r').endswith(address):
                logger.warning(IGNORE_FROM_SELF % m)
            else:
                next_msg = process(M, num, m)
                assert M.state == 'AUTH', M.state
                if next_msg:
                   #send(host, address, list(Subscribers(M)), m)
                    send(address, [], next_msg,
                         host=host, user=address, password=password)
        else:
            break
    M.logout()

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
