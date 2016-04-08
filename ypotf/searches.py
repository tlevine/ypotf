'''
TODO: Ignore from self because that's a good infinite loop.
'''
import re

from .utils import r

def _just_email_address(x):
    if '\\' in x or '"' in x:
        raise ValueError('Invalid email address: %s' % x)
    return x

def _parse_headers(x):
    lines = filter(None, re.split(r'[\r\n]+', x[0][1].decode('utf-8')))
    return dict(re.split(r': ?', line.lower(), maxsplit=1) \
                for line in lines)

def _parse_flags(x):
    m = re.match('[0-9 (]+FLAGS \(([^)]+)', x[0].decode('utf-8'))
    if m:
        return set(n.upper() for n in m.group(1).split())

def _search(criterion, M):
    return r(M.search(None, 'UNDELETED ' + criterion))

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
        e = _just_email_address(from_field)
        nums = _search('FLAGGED UNDRAFT SUBJECT "%s"' % e, M)
        x = 'BODY.PEEK[HEADER.FIELDS (TO SUBJECT)]'
        for num, m in _fetch(x, M, nums):
            h = _parse_headers(m)
            if _just_email_addres(h['SUBJECT']) == e:
                return num, h['TO']

    @staticmethod
    def new_orders(M):
        '''
        Search for non-Seen (just-received) emails.
        '''
        nums = _search('UNSEEN', M)
        message_parts = 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]'
        for num, m in _fetch(message_parts, M, nums):
            h = _parse_headers(m)
            e = _just_email_address(h['FROM'])
            yield num, e, h['SUBJECT'], h['MESSAGE-ID']

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
            ( FLAGGED DRAFT
              ( OR
                ( FLAGGED UNDRAFT TO "")
                ( UNFLAGGED DRAFT))))''' % code)

        nums = _search(criterion, M)
        for num, m in _fetch('FLAGS', M, nums):
            flags = _parse_flags(m)
            if {'FLAGGED', 'DRAFT'}.issubset(flags):
                return num, 'subscribe'
            elif 'FLAGGED' in flags:
                return num, 'unsubscribe'
            elif 'DRAFT' in flags:
                return num, 'message'
        return None, None
