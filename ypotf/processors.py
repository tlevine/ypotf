'''
Processors take a mailbox with the +INBOX folder selected.

They return a message that should be sent, or None.
'''

import imaplib
from email.Utils import parsedate
from email.message import Message

from . import templates
from . import storage

MATCHERS = [(k, re.compile(v, flags=re.IGNORECASE)) for (k,v) in [
    ('subscriptions', r'^(?:un)?subscribe$'),
    ('confirmations', r'list-confirm-[a-z0-9]{32}'),
#   ('archive', r'^list-archive'),
    ('help', r'^help$'),
]]

def process(M, m):
    db = storage.Confirmations(M)
    if re.match(MATCHERS['subscriptions'], m['subject']):
        return add_confirmation(db, m['message-id'],
                                m['subject'], m['from'])
    elif re.match(MATCHERS['help'], subject):
        return templates.help(date = m['date'])
    elif re.match(MATCHERS['confirmations'], subject)
        code = re.match(MATCHERS['confirmations'], subject).group(1)
        return process_confirmation(db, code)
    else:
        return add_confirmation(db, m['message-id'],
                                'message', m['message-id'])

def add_confirmation(db, message_id, action, argument):
    confirmation_code = bytes(random.randint(32, 126) for _ in range(32))
    db[confirmation_code] = '%s %s' % (action, argument)
    return templates.confirmation(
        references=message_id,
        subject='Re: ' + subject.strip()
        confirmation_code=confirmation_code,
    )

def process_confirmation(db, confirmation_code):
    action, argument = db[confirmation_code].partition(' ')
    if action == 'message':
        storage.send_message(argument)
    else:
        raise ValueError
