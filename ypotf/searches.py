import re
from .utils import r

def _parse_headers(x):
    lines = re.split(r'[\r\n]+', x.decode('utf-8'))
    return dict(re.split(r': ?', line, maxsplit=1) for line in lines)

def _search(folder, criterion, M):
    r(M.select(folder))
    return r(M.search(None, criterion))

def _fetch(fetch, M, nums):
    for num in nums.split():
        yield r(M.fetch(num, fetch))

# Search the Sent folder with the SENTSINCE search key to assess quotas
# (one search per quota)
def n_sent(M, timedelta):
    '''
    :param imaplib.IMAP4_SSL M: A mailbox
    :type timedelta: datetime.timedelta or int
    :param timedelta: A time duration, integers interpreted as minutes
    :returns: The number of messages
    :rtype: int
    '''
    criterion = 'SENTSINCE "01-JAN-2014"' % dt.strftime('%d-%b-%Y')
    return len(_search('Sent', criterion, M).split())

# Search the Inbox folder for the subject fields of messages with the
# Flagged flag and without the Draft flag; these are the current
# subscribers.
def subscribers(M):
    '''
    :param imaplib.IMAP4_SSL M: A mailbox
    :returns: Set of str email addresses of subscribers
    :rtype: set
    '''
    nums = _search('Inbox', 'FLAGGED UNDRAFT', M)
    x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
    headers = (_parse_headers(m[1][0][1]) for m in _fetch(x, M, nums))
    return set(m['subject'] for m in headers)

# Search for Draft (confirmation) and non-Seen (just-received) emails.
def orders(M):
    nums = _search('Inbox', 'OR (FLAGGED DRAFT) UNSEEN', M)
    out = {'confirmations': {}, 'new': {}}
    for m in _fetch('BODY.PEEK[HEADER.FIELDS (TO SUBJECT)]', M, nums):
        m['subject']
        yield _parse_headers(data[1][0][1])
FLAGS (\\Answered \\Seen)
