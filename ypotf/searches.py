'''
TODO: Ignore from self because that's a good infinite loop.
'''
import re

from .utils import r

def _parse_headers(x):
    lines = re.split(r'[\r\n]+', x[0][1].decode('utf-8'))
    return dict(re.split(r': ?', line, maxsplit=1) for line.lower() in lines)

def _search(folder, criterion, M):
    r(M.select(folder))
    return r(M.search(None, criterion))

def _fetch(fetch, M, nums):
    for num in nums.split():
        yield num, r(M.fetch(num, fetch))

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
    headers = (_parse_headers(m) for _, m in _fetch(x, M, nums))
    return {m['SUBJECT']:num for m,num in zip(headers, nums.split())}

# Search for Draft (confirmation) and non-Seen (just-received) emails.
def orders(M):
    '''
    UNSEEN
        New order, not a confirmation for a previous order
    FLAGGED DRAFT
        Subscription confirmation
    FLAGGED UNDRAFT TO ""
        Unsubscription confirmation
    UNFLAGGED DRAFT
        Message confirmation
    '''
    criterion = re.sub(r'[\n ]+', ' ', '''
        ( OR
          UNSEEN
          ( OR
            ( FLAGGED DRAFT
              ( OR
                ( FLAGGED UNDRAFT TO "")
                ( UNFLAGGED DRAFT)))))''')
    nums = _search('Inbox', criterion , M)
    out = {'confirmations': {}, 'new': []}

    message_parts = 'BODY.PEEK[HEADER.FIELDS (TO SUBJECT)]'
    for num, data in _fetch(message_parts, M, nums):
        h = _parse_headers(data)

        m = re.match(r'.*FLAGS \(([^)]+).*', m[0][0].decode('utf-8'))
        if not m:
            raise ValueError('Bad response: %s' % data)
        flags = set(m.group(1).split())

        if '\\UNSEEN' in flags:
            # New message
            out['new'].append(num)
        elif {'\\FLAGGED', '\\DRAFT'}.issubset(flags):
            # Subscribe confirmation
            out['confirmations'][h['TO']] = {
                'action': 'subscribe',
                'address': h['SUBJECT'],
                'code': h['TO'],
                'num': num,
            }
        elif ('DRAFT' not in flags) and 'FLAGGED' in flags and 'TO' in h:
            # Unsubscribe confirmation
            out['confirmations'][h['TO']] = {
                'action': 'unsubscribe',
                'address': h['SUBJECT'],
                'code': h['TO'],
                'num': num,
            }
        elif 'DRAFT' in flags and not 'FLAGGED' in flags:
            # Message confirmation
            out['confirmations'][h['TO']] = {
                'action': 'message',
                'address': h['SUBJECT'],
                'code': h['TO'],
                'num': num,
            }
        else:
            raise ValueError('Bad response: %s' % data)
    return out
