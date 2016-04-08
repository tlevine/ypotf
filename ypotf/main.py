import imaplib
import logging

from . import searches
from . import quota
from .utils import r

logger = logging.getLogger(__name__)

def ypotf(password, *quotas):
    M = imaplib.IMAP4_SSL('mail.gandi.net')
    r(M.login('_@dada.pink', password))

    # "Sent" folder
    N = quota.quota(M, quotas)

    # "Inbox" folder
    for num, action, subject in searches.Inbox.new_orders(M):
        getattr(process, action)(M, num, subject)

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
