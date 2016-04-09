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

def _parse_flags(x):
    m = re.match('[0-9 (]+FLAGS \(([^)]+)', x[0].decode('utf-8'))
    if m:
        return set(n.upper() for n in m.group(1).split())

def _search(criterion, M):
    x = 'UNDELETED ' + criterion
    y = '\n%s\n' % textwrap.indent(textwrap.fill(x.strip(), 50), '  ')
    logger.debug('Searching:\n%s' % y)

    nums = r(M.search(None, x))
    n = (nums[0].count(b' ')+1) if nums[0] else 0

    logger.debug('%d results' % n)
    return nums

def search_one(M, criterion):
    nums = _search(criterion, M)
    xs = nums[0].split()
    if len(xs) == 1:
        return xs[0]
    elif len(xs) == 0:
        raise ValueError('No messages match "%s"' % criterion)
    else:
        raise ValueError('Multiple messages match "%s"' % criterion)

def _fetch(fetch, M, nums):
    for num in nums[0].split():
        yield num, r(M.fetch(num, fetch))

def fetch_one(M, num):
    data = r(M.fetch(num, '(RFC822)')
    return message_from_bytes(data[0][1])

class inbox(object):

    @staticmethod
    def subscribers(M):
        '''
        :returns: Iterable of subscriber email addresses
        '''
        nums = _search('ANSWERED HEADER X-Ypotf-Kind Subscription', M)
        x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
        headers = (_parse_headers(m) for _, m in _fetch(x, M, nums))
        return set(m['SUBJECT'] for m in headers)

    @staticmethod
    def subscriber_ypotf_id(M, address):
        '''
        :returns: Iterable of subscriber email addresses
        '''
        e = email_address(address)

        s = 'ANSWERED HEADER X-Ypotf-Kind Subscription Subject "%s"'
        nums = _search(q % s, M)

        f = 'BODY.PEEK[HEADER.FIELDS (X-Ypotf-Id Subject)]'
        for _, m in _fetch(f, M, nums):
            _parse_headers(m)
            if email_address(m['Subject']) == e:
                return m['X-Ypotf-Id']

    @staticmethod
    def current(M, address):
        return inbox._subscriber(M, address, 'UNDRAFT SEEN')

    @staticmethod
    def pending(M, address):
        return inbox._subscriber(M, address, 'DRAFT SEEN')

    @staticmethod
    def new_orders(M):
        '''
        Search for just-received emails.
        '''
        nums = _search('UNSEEN UNANSWERED', M)
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

    @staticmethod
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
