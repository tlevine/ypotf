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
    lines = re.split(r'[\r\n]+', x[0][1].decode('utf-8'))
    return dict(re.split(r': ?', line, maxsplit=1) for line.lower() in lines)

def _search(criterion, M):
    return r(M.search(None, criterion))

def _fetch(fetch, M, nums):
    for num in nums.split():
        yield num, r(M.fetch(num, fetch))

class Sent(object):
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
        r(M.select('Sent'))
        return len(_search(criterion, M).split())

class Inbox(object):
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
        for num, m in _fetch(nums, 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'):
            if _just_email_addres(_parse_headers(m)['SUBJECT']) == e:
                return num

    @staticmethod
    def new_orders(M):
        '''
        Search for non-Seen (just-received) emails.
        '''
        nums = _search('UNSEEN', M)
        message_parts = 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]'
        return _fetch(message_parts, M, nums)

    @staticmethod
    def confirmations(M):
        '''
        Search for Draft (confirmation)

        FLAGGED DRAFT
            Subscription confirmation
        FLAGGED UNDRAFT TO ""
            Unsubscription confirmation
        UNFLAGGED DRAFT
            Message confirmation
        '''
        criterion = re.sub(r'[\n ]+', ' ', '''
            OR
            ( FLAGGED DRAFT
              ( OR
                ( FLAGGED UNDRAFT TO "")
                ( UNFLAGGED DRAFT)))''')
        message_parts = '(FLAGS BODY.PEEK[HEADER.FIELDS (TO SUBJECT)])'

        nums = _search(criterion, M)
        return _fetch(message_parts, M, nums)
