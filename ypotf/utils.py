from uuid import uuid1
import email
import textwrap
import logging

logger = logging.getLogger(__name__)

def r(x, expected='OK'):
    typ, data = x
    assert typ == expected, typ
    return data

def uuid():
    return uuid1().hex

def email_address(x):
    return email.utils.parseaddr(x)[1].lower()

def search(M, criterion):
    x = 'UNDELETED ' + criterion
    y = '\n%s\n' % textwrap.indent(textwrap.fill(x.strip(), 50), '  ')
    logger.debug('Searching:\n%s' % y)

    nums = r(M.search(None, x))
    n = (nums[0].count(b' ')+1) if nums[0] else 0

    logger.debug('%d results' % n)
    return nums

def get_num(M, criterion):
    ns = nums[0].split()
    if len(ns) == 0:
        raise ValueError('No results')
    elif len(ns) == 1:
        return ns[0]
    else:
        raise ValueError('%d results' % len(ns))
