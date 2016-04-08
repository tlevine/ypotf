import re
import logging
import textwrap

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

def _block(x):
    return '\n%s\n' % textwrap.indent(textwrap.fill(x.strip(), 50), '  ')

def _search(criterion, M):
    x = 'UNDELETED ' + criterion
    logger.debug('Searching:\n%s' % _block(x))

    nums = r(M.search(None, x))
    n = (nums[0].count(b' ')+1) if nums[0] else 0

    logger.debug('%d results' % n)
    return nums

def _fetch(fetch, M, nums):
    for num in nums[0].split():
        yield num, r(M.fetch(num, fetch))

class sent(object):
    @staticmethod
    def n_sent(M, timedelta):
        '''
        Search the Sent folder with the SENTSINCE search key to assess
        quotas (one search per quota).

        :param imaplib.IMAP4_SSL M: A mailbox
        :type timedelta: datetime.timedelta or int
        :param timedelta: A time duration, integers interpreted as minutes
        :returns: The number of messages
        :rtype: int
        '''
        criterion = 'SENTSINCE "%s"' % dt.strftime('%d-%b-%Y')
        return len(_search(criterion, M).split())

class inbox(object):
    @staticmethod
    def subscribers(M):
        '''
        Search the Inbox folder for the subject fields of messages with the
        Flagged flag and without the Draft flag; these are the current
        subscribers.

        :param imaplib.IMAP4_SSL M: A mailbox
        :returns: Set of str email addresses of subscribers
        :rtype: set
        '''
        r(M.select('Inbox'))
        nums = _search('FLAGGED UNDRAFT', M)
        x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT MESSAGE-ID)]'
        headers = (_parse_headers(m) for _, m in _fetch(x, M, nums))
        return set(m['SUBJECT'] for m in headers)

    @staticmethod
    def subscriber(M, from_field):
        '''
        " and \ are not allowed in email addresses, so this is safe.
        '''
        e = email_address(from_field)
        nums = _search('FLAGGED UNDRAFT SUBJECT "%s"' % e, M)
        x = 'BODY.PEEK[HEADER.FIELDS (TO SUBJECT)]'
        for num, m in _fetch(x, M, nums):
            h = _parse_headers(m)
            if email_address(h['SUBJECT']).lower() == e.lower():
                return num, h.get('TO') # None if already subscribed
        return None, None

    @staticmethod
    def new_orders(M):
        '''
        Search for non-Seen (just-received) emails.
        '''
        nums = _search('UNSEEN', M)
        message_parts = 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT MESSAGE-ID)]'
        for num, m in _fetch(message_parts, M, nums):
            h = _parse_headers(m)
            if {'FROM', 'SUBJECT', 'MESSAGE-ID'}.issubset(h):
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
        '''
        Search for Draft (confirmation)

        FLAGGED DRAFT
            Subscription confirmation
        FLAGGED UNDRAFT
            Unsubscription confirmation
        UNFLAGGED DRAFT
            Message confirmation
        '''
        criterion = re.sub(r'[\n ]+', ' ', '''
          TO "%s"
          ( OR
            ( FLAGGED DRAFT )
            ( OR
              ( FLAGGED UNDRAFT )
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
