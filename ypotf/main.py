import imaplib
import smtplib
import logging

from . import searches
from .utils import r

logger = logging.getLogger(__name__)

class LimitedSMTP(smtplib.SMTP):
    def __init__(self, N, *args, **kwargs):
        '''
        :param int n: Max messages to send this session
        '''
        self.N = N
        self.n = 0
        super(LimitedSMTP, self).__init__(*args, **kwargs)
    def sendmail(*args, **kwargs):
        self.n += 1
        if self.n < self.N:
            return super(LimitedSMTP, self).sendmail(*args, **kwargs)
        else:
            raise RuntimeError('Rate limit exceeded')

def ypotf(password, *quotas):
    M = imaplib.IMAP4_SSL('mail.gandi.net')
    r(M.login('_@dada.pink', password))

    N = sending_quota_for_this_session(M, quotas)
    subs = searches.subscribers(M)
    orders = searches.orders(M)
    for num in orders['new']:
        m = message_from_bytes(r(M.fetch(num, '(RFC822)'))[0][1])
        

def sending_quota_for_this_session(M, quotas):
    N = None
    for quota in quotas:
        minutes, count = map(int, quota.split(':'))
        n = count - searches.n_sent(M, minutes)
        if N == None or n < N:
            N = n
    return N

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
