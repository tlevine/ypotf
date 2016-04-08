'''
Processors take a mailbox with the +INBOX folder selected.

They return a message that should be sent, or None.
'''
import datetime
import re
import logging

from random import randint
from .utils import r

logger = logging.getLogger(__name__)

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('confirmations', r'list-confirm-[a-z0-9]{32}'),
#   ('archive', r'^list-archive'),
    ('help', r'^help$'),
]}

def _just_email_address(x):
    return x

def process(confirmations, M, num):
    m = message_from_bytes(r(M.fetch(num, '(RFC822)'))[0][1])
    from_address = _just_email_address(m['from'])

    def _log(cat):
        tpl = 'Processing message %s as a %s comand'
        logger.info(tpl % (m['message-id'], cat))

    if re.match(MATCHERS['subscribe'], m['subject']):
        _log('subscription')
        code = _confirmation_code()
        _append(M, '\\Flagged \\Draft',
                _message(to=code, subject=from_address))

        r(M.store(num, '+FLAGS', '\\Seen')
        return template.configure(
            'sender',
            to_address=m['From'],
            references=m['message-id'],
            subject=subject,
            confirmation_code=code,
        )

    elif re.match(MATCHERS['confirmations'], m['subject']):
        _log('confirmation')
        code = re.match(MATCHERS['confirmations'], m['subject']).group(1)
        confirmation = confirmations[code]

        if confirmation['action'] == 'message':
        elif confirmation['action'] == 'subscribe':
        elif confirmation['action'] == 'unsubscribe':
        else:
            raise ValueError

    elif re.match(MATCHERS['help'], m['subject']):
        _log('help')
        raise NotImplementedError
        return template.configure(
            'sender',
            to_address=m['From'],
            subject='Re: ' + m['subject'].strip(),
            references=m['message-id'],
            date = m['date'],
        )
    else:
        _log('message')
        storage.queue_message(M, num)
        r(M.close())
        code = _confirmation_code()
        confirmations[code] = '%s %s' % ('message', m['message-id'])
        return template.configure(
            'sender',
            to_address=m['From'],
            references=m['message-id'],
            subject='Re: ' + m['subject'].strip(),
            confirmation_code=code,
        )

def _confirmation_code():
    return bytes(randint(32, 126) for _ in range(32)).decode('ascii')

def _append(M, flags, m):
    d = tuple(datetime.datetime.now().timetuple())
    return r(M.append('Inbox', flags, d, m.as_bytes()))

def _message(**headers):
    m = Message()
    for key, value in headers.items():
        m[key] = value
    return m  
