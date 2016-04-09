import uuid
import email
import textwrap
import logging

logger = logging.getLogger(__name__)

def r(x, expected='OK'):
    typ, data = x
    assert typ == expected, typ
    return data

def uuid():
    return uuid.uuid1().hex

def email_address(x):
    return email.utils.parse_addr(x)[1].lower()

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
    data = r(M.fetch(num, fetch)
    return email.utils.message_from_bytes(data[0][1])
