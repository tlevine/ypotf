import sys
import imaplib
import logging

from . import search
from . import quota
from .process import process
from .utils import r

logger = logging.getLogger(__name__)

def ypotf(password, *quotas, list_subscribers=False):
    imap_host = smtp_host = 'mail.gandi.net'
    imap_username = smtp_username = '_@dada.pink'
    imap_password = smtp_password = password

    M = imaplib.IMAP4_SSL(imap_host)
    r(M.login(imap_username, imap_password))

    if list_subscribers:
        subscribers(M)

    r(M.select('Sent'))
    N = quota.quota(M, quotas)
    r(M.close())

    S = quota.LimitedSMTP(N, host=smtp_host)
    S.login(smtp_username, smtp_password)

    r(M.select('Inbox'))
    orders = search.inbox.new_orders(M)
    for num, from_address, subject, message_id in orders:
        logger.info('Processing message from %s' % from_address)
        process(S, M, num, from_address, subject, message_id)
    r(M.close())
    r(M.logout(), 'BYE')

def subscribers(M):
    r(M.select('Inbox'))
    xs = search.inbox.subscribers(M)

    if len(xs):
        sys.stdout.write('\n'.join(sorted(xs)) + '\n')
    else:
        sys.stderr.write('No subscribers\n')

    r(M.close())
    r(M.logout(), 'BYE')

    sys.exit(1 if len(xs) else 0)

def cli():
    logging.basicConfig(level=logging.DEBUG)
    import horetu
    horetu.horetu(ypotf)
