import imaplib
import os
import logging

from .storage import first_message, MAILBOXES
from .processors import process

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
