import imaplib
import logging
import urllib

from .utils import r

logger = logging.getLogger(__name__)

def ypotf(host:str,
          imap_address:str=None, imap_password:str=None,
          smtp_address:str=None, smtp_password:str=None,
          ):
    '''
    >>> ypotf('mail.gandi.net')
    ...

    >>> ypotf('mail.gandi.net', imap_address='imaps://blah:980')
    ...
    '''
    M = _imap_from_url(imap_address, imap_password)
    r(M.login(address, password))
    send(address, [], next_msg,
         host=host, user=address, password=password)

def _imap_from_url(url):
    x = urllib.parse.urlparse(url)

    if x.scheme.lower() == 'imap':
        f = imaplib.IMAP4
    else:
        f = imaplib.IMAP4_SSL

    if x.port:
        args = x.hostname, x.port
    else:
        args = x.hostname,

    return f(*args)

def cli():
    logging.basicConfig(level=logging.INFO)
    import horetu
    horetu.horetu(ypotf)
