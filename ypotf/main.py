import imaplib
import logging

from . import searches
from .utils import r

logger = logging.getLogger(__name__)

def ypotf(password, *quotas):
    M = imaplib.IMAP4_SSL('mail.gandi.net')
    r(M.login('_@dada.pink', password))

    N = sending_quota_for_this_session(M, quotas)
    subs = searches.subscribers(M)
    orders = searches.orders(M)
    for num in orders['new']:
        m = message_from_bytes(r(M.fetch(num, '(RFC822)'))[0][1])
        m['subject']

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
