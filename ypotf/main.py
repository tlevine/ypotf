import imaplib
import logging

from .utils import r

logger = logging.getLogger(__name__)

def ypotf(password, *quotas):
    M = imaplib.IMAP4_SSL('mail.gandi.net')
    r(M.login('_@dada.pink', password))
    N = quota_for_this_session(M, quotas)

    send(address, [], next_msg,
         host=host, user=address, password=password)

def quota_for_this_session(M, quotas):
    N = None
    for quota in quotas:
        minutes, count = map(int, quota.split(':'))
        n = count - n_sent(M, minutes)
        if N == None or n < N:
            N = n
    return N

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
