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
    confirmations = storage.Confirmations(M)
    if re.match(MATCHERS['subscriptions'], m['subject']):
        return add_confirmation(confirmations, m['message-id'],
                                m['subject'], m['from'])
    elif re.match(MATCHERS['help'], subject):
        return templates.help(date = m['date'])
    elif re.match(MATCHERS['confirmations'], subject)
        code = re.match(MATCHERS['confirmations'], subject).group(1)
        action, argument = confirmations[code].partition(' ')
        if action == 'message':
            storage.send_message(argument)
        elif action == 'subscribe':
        elif action == 'unsubscribe':
        else:
            raise ValueError
    else:
        code = bytes(random.randint(32, 126) \
                                  for _ in range(32))
        confirmations[code] = '%s %s' % ('message', m['message-id'])
        return templates.confirmation(
            references=m['message-id'],
            subject='Re: ' + m['subject'].strip()
            confirmation_code=code,
        )
