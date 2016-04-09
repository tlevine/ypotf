import re
import logging
import textwrap

from email import message_from_bytes
from .utils import r, email_address, search

logger = logging.getLogger(__name__)

def _fetch(fetch, M, nums):
    for num in nums[0].split():
        yield num, message_from_bytes(r(M.fetch(num, fetch))[0][1])

def subscribers(M):
    '''
    :returns: Iterable of subscriber email addresses
    '''
    nums = search(M, 'ANSWERED HEADER X-Ypotf-Subscription ""')
    x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
    return set(m['SUBJECT'] for _, m in _fetch(x, M, nums))

def is_subscribed(M, address):
    '''
    :returns: Whether the address is subscribed
    :rtype: bool
    '''
    e = email_address(address)
    s = 'ANSWERED HEADER X-Ypotf-Subscription "" SUBJECT %s' % e
    return search(M, s) != [b'']

def subscription_ypotf_id(M, address):
    '''
    :returns: Ypotf ID for a particular subscription
    '''
    e = email_address(address)

    s = 'HEADER X-Ypotf-Subscription "" HEADER SUBJECT "%s"'
    nums = search(M, s % e)

    f = 'BODY.PEEK[HEADER.FIELDS (X-Ypotf-Id Subject)]'
    for _, m in _fetch(f, M, nums):
        if email_address(m['Subject']) == e:
            return m['X-Ypotf-Id']

def ypotf_id_num(M, x):
    q = 'HEADER "X-Ypotf-Subscription" "" HEADER "X-Ypotf-Id" "%s"'
    criterion = q % x
    nums = search(M, criterion)
    xs = nums[0].split()
    if len(xs) == 1:
        return xs[0]
    elif len(xs) == 0:
        logger.debug('No messages match "%s"' % criterion)
    else:
        logger.warning('Multiple messages match "%s"' % criterion)
        return xs[0]
    
def new_orders(M):
    '''
    Search for just-received emails.
    '''
    nums = search(M, 'UNANSWERED NOT HEADER X-Ypotf-Subscription ""')
    for num, m in _fetch('(RFC822)', M, nums):
        if 'From' in m and 'Subject' in m:
            logger.debug('''Found a new order

From: %(FROM)s
Subject: %(SUBJECT)s
''' % m)
            yield num, m
        else:
            logger.warning('Message %s is missing headers, skipping' %
                           num.decode('ascii'))

def archive(M, matchers):
    '''
    :returns: Iterable of subscriber email addresses
    '''
    nums = search(M, 'ANSWERED NOT HEADER X-Ypotf-Subscription ""')
    x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
    for _, m in _fetch(x, M, nums):
        for exp in matchers.values():
            if re.match(exp, m['Subject']):
                break
        else:
            yield m['Subject']
