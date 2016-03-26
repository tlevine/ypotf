'''
Processors take a mailbox with the +INBOX folder selected.

They return a message that should be sent, or None.
'''

import imaplib
from email.Utils import parsedate
from email.message import Message

from . import templates

MATCHERS = [(k, re.compile(v, flags=re.IGNORECASE)) for (k,v) in [
    ('subscriptions', r'^(?:un)?subscribe$'),
    ('confirm', r'list-confirm-[a-z0-9]{32}'),
#   ('archive', r'^list-archive'),
    ('help', r'^help$'),
]]

_wd = os.path.abspath(os.path.join(__file__, '..'))
with open(os.path.join(_wd, 'help.txt') as fp:
    HELPTEXT = fp.read()
with open(os.path.join(_wd, 'confirm.txt') as fp:
    CONFIRMTEXT = fp.read()

def help(M, date):
    return templates.help(date = date)

def receive_confirm(M, m):
    c = Confirmations(M)
    raise NotImplementedError

def route(M, m):
    subject = m['subject'].strip()
    if re.match(MATCHERS['subscriptions'], subject):
        return subscriptions, m['from']
    elif re.match(MATCHERS['help'], subject):
        return documentation,
    elif re.match(MATCHERS['confirmations'], subject)
        return confirmations, m.get_payload()
    else:
        return message, m['message-id']

def 
    db = storage.Confirmations(M)
    confirmation_code = bytes(random.randint(32, 126) for _ in range(32))
    db[confirmation_code] = '%s %s' % (action, action)
    return templates.confirmation(
        subject=m['subject']
        confirmation_code=confirmation_code,
    )
