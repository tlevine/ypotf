'''
Processors take a mailbox with the +INBOX folder selected.

They return a message that should be sent, or None.
'''
import random
import re
import logging

from . import template
from . import storage

logger = logging.getLogger(__name__)

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscriptions', r'^(?:un)?subscribe$'),
    ('confirmations', r'list-confirm-[a-z0-9]{32}'),
#   ('archive', r'^list-archive'),
    ('help', r'^help$'),
]}

def process(M, num, m):
    confirmations = storage.Confirmations(M)
    subscribers = storage.Subscribers(M)

    def _log(cat):
        tpl = 'Processing message %s as a %s comand'
        logger.info(tpl % (m['message-id'], cat))
    if re.match(MATCHERS['subscriptions'], m['subject']):
        _log('subscription')
        storage.archive_message(M, num)
        M.close()
        code = _confirmation_code()
        confirmations[code] = '%s %s' % (m['subject'], m['from'])
        subject = 'Re: Your %s request' % m['subject'].strip().lower()
        return template.render(
            references=m['message-id'],
            subject=subject,
            confirmation_code=code,
        )
    elif re.match(MATCHERS['confirmations'], m['subject']):
        _log('confirmation')
        storage.archive_message(M, num)
        M.close()
        code = re.match(MATCHERS['confirmations'], m['subject']).group(1)
        action, argument = confirmations[code].partition(' ')
        if action == 'message':
            storage.send_message(argument)
        elif action == 'subscribe':
            subscribers[argument] = ''
        elif action == 'unsubscribe':
            del(subscribers[argument])
        else:
            raise ValueError
    elif re.match(MATCHERS['help'], m['subject']):
        _log('help')
        storage.archive_message(M, num)
        M.close()
        return template.render(
            subject='Re: ' + m['subject'].strip(),
            references=m['message-id'],
            date = m['date'],
        )
    else:
        _log('message')
        storage.queue_message(M, num)
        M.close()
        code = _confirmation_code()
        confirmations[code] = '%s %s' % ('message', m['message-id'])
        return template.render(
            references=m['message-id'],
            subject='Re: ' + m['subject'].strip(),
            confirmation_code=code,
        )

def _confirmation_code():
    return bytes(random.randint(32, 126) for _ in range(32)).decode('ascii')
           
