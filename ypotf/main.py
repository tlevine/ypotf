import sys
import imaplib
import logging

from . import search
from . import quota
from .process import process
from .utils import r

logger = logging.getLogger(__name__)

def ypotf(password, *quotas, n:int=0, list_subscribers=False):
    '''
    Process mailing list commands.

    :param str password: Password for the account
    :param str quotas: Sending rate limits in the form "$minutes:$count"
    :param int n: Number of incoming emails to process this session
        If it is zero (the default), it is ignored.

    The max emails to send this session is the minimum that I determine
    from all quotas.
    '''
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
    for i, (num, from_address, subject, message_id) in enumerate(orders):
        if n and i < n:
            logger.info('Processing message from %s' % from_address)
            process(S, M, num, from_address, subject, message_id)
        else:
            logger.info('Processed %d messages' % n)
            break
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
