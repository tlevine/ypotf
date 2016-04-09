import re
import logging
import textwrap

from email import message_from_bytes
from .utils import r, email_address, search

logger = logging.getLogger(__name__)

def _fetch(fetch, M, nums):
    for num in nums[0].split():
        yield num, message_from_bytes(r(M.fetch(num, fetch)))

def subscribers(M):
    '''
    :returns: Iterable of subscriber email addresses
    '''
    nums = search(M, 'ANSWERED HEADER X-Ypotf-Kind Subscription')
    x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
    return set(m['SUBJECT'] for _, m in _fetch(x, M, nums))

def subscription_ypotf_id(M, address):
    '''
    :returns: Ypotf ID for a particular subscription
    '''
    e = email_address(address)

    s = 'ANSWERED HEADER X-Ypotf-Kind Subscription Subject "%s"'
    nums = search(M, q % s)

    f = 'BODY.PEEK[HEADER.FIELDS (X-Ypotf-Id Subject)]'
    for _, m in _fetch(f, M, nums):
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
    nums = search(M, q % x)
    xs = nums[0].split()
    if len(xs) == 1:
        return xs[0]
    elif len(xs) == 0:
        raise ValueError('No messages match "%s"' % criterion)
    else:
        raise ValueError('Multiple messages match "%s"' % criterion)
    
def new_orders(M):
    '''
    Search for just-received emails.
    '''
    nums = search(M, 'UNSEEN UNANSWERED')
    message_parts = 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT MESSAGE-ID)]'
    for num, m in _fetch(message_parts, M, nums):
        message_from_bytes(m)
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






