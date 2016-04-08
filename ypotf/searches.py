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
        data = r(M.fetch(num, fetch))
        yield _parse_headers(data[1][0][1])


# Search the Sent folder with the SENTSINCE search key to assess quotas
# (one search per quota)
def sent_since(M, datetime):
    criterion = 'SENTSINCE "01-JAN-2014"' % datetime.strftime('%d-%b-%Y')
    return len(_search('Sent', criterion, M).split())

# Search the Inbox folder for the subject fields of messages with the
# Flagged flag and without the Draft flag; these are the current
# subscribers.
def subscribers(M):
    nums = _search('Inbox', 'FLAGGED UNDRAFT', M)
    x = 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
    return set(m['subject'] for m in _fetch(x, M, nums))
}

# Search for Draft (confirmation) and non-Seen (just-received) emails.
orders = {
    'folder': 'Inbox',
    'criterion': 'OR DRAFT UNSEEN',
    'fetch': 'BODY.PEEK[HEADER.FIELDS (TO SUBJECT)]',
}
