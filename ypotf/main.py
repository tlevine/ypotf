import imaplib
import logging

from .utils import r

logger = logging.getLogger(__name__)

def ypotf(password):
    M = imaplib.IMAP4_SSL('mail.gandi.net')
    r(M.login('_@dada.pink', password))
    send(address, [], next_msg,
         host=host, user=address, password=password)

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
