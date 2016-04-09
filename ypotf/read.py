import re
import logging
import textwrap

from email import message_from_bytes
from .utils import r, email_address

logger = logging.getLogger(__name__)

def _parse_headers(x):
    lines = filter(None, re.split(r'[\r\n]+', x[0][1].decode('utf-8')))
    pairs = (re.split(r': ?', line, maxsplit=1) for line in lines)
    return {k.upper():v for k,v in pairs}

def subscribers(M):
    '''
    :returns: Iterable of subscriber email addresses
    '''
    nums = _search(M, 'ANSWERED HEADER X-Ypotf-Kind Subscription')
    x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
    headers = (_parse_headers(m) for _, m in _fetch(x, M, nums))
    return set(m['SUBJECT'] for m in headers)

def subscription_ypotf_id(M, address):
    '''
    :returns: Ypotf ID for a particular subscription
    '''
    e = email_address(address)

    s = 'ANSWERED HEADER X-Ypotf-Kind Subscription Subject "%s"'
    nums = _search(M, q % s)

    f = 'BODY.PEEK[HEADER.FIELDS (X-Ypotf-Id Subject)]'
    for _, m in _fetch(f, M, nums):
        _parse_headers(m)
        if email_address(m['Subject']) == e:
            return m['X-Ypotf-Id']

def is_subscribed(M, address):
    '''
    :returns: Whether the address is subscribed
    :rtype: bool
    '''
    return subscription_ypotf_id(address) != None

def ypotf_id_num(M, x):
    q = 'ANSWERED HEADER X-Ypotf-Kind Subscription X-Ypotf-Id "%s"'
    return search_one(M, q % x)
    






    def current(M, address):
        return inbox._subscriber(M, address, 'UNDRAFT SEEN')

    def pending(M, address):
        return inbox._subscriber(M, address, 'DRAFT SEEN')

    def new_orders(M):
        '''
        Search for just-received emails.
        '''
        nums = _search(M, 'UNSEEN UNANSWERED')
        message_parts = 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT MESSAGE-ID)]'
        for num, m in _fetch(message_parts, M, nums):
            h = _parse_headers(m)
            if {'FROM', 'SUBJECT'}.issubset(h):
                logger.debug('''Found a new order

  From: %(FROM)s
  Subject: %(SUBJECT)s
  Message-id: %(MESSAGE-ID)s
''' % h)
                e = email_address(h['FROM'])
                yield num, e, h['SUBJECT'], h['MESSAGE-ID']
            else:
                logger.warning('Message %s is missing headers' %
                               num.decode('ascii'))

    def confirmation(M, code):
        criterion = re.sub(r'[\n ]+', ' ', '''
          SUBJECT "%s"
          ( OR
            ( FLAGGED DRAFT SEEN )
            ( OR
              ( FLAGGED UNDRAFT UNSEEN )
              ( UNFLAGGED DRAFT )))''' % code)

        nums = _search(criterion, M)
        for num, m in _fetch('FLAGS', M, nums):
            flags = _parse_flags(m)
            if {'\\FLAGGED', '\\DRAFT'}.issubset(flags):
                return num, 'subscribe'
            elif '\\FLAGGED' in flags:
                return num, 'unsubscribe'
            elif '\\DRAFT' in flags:
                return num, 'message'
        return None, None
