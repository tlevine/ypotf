import imaplib
import logging

from . import searches
from . import quota
from .utils import r

logger = logging.getLogger(__name__)

def ypotf(password, *quotas):
    M = imaplib.IMAP4_SSL('mail.gandi.net')
    r(M.login('_@dada.pink', password))

    N = quota.quota(M, quotas)
    subs = searches.subscribers(M)
    orders = searches.orders(M)
    for num in orders['new']:

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
