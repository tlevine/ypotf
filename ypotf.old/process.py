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


def process(confirmations, M, num):
    m = message_from_bytes(r(M.fetch(num, '(RFC822)'))[0][1])
    from_address = _just_email_address(m['from'])

    def _log(cat):
        tpl = 'Processing message %s as a %s comand'
        logger.info(tpl % (m['message-id'], cat))

    if re.match(MATCHERS['subscribe'], m['subject']):
        _log('subscription')
        code = _confirmation_code()
        _append(M, '\\Flagged \\Draft \\Seen',
                _message(to=code, subject=from_address))

        r(M.store(num, '+FLAGS', '\\Seen')
        return template.configure(
            'sender',
            to_address=m['From'],
            references=m['message-id'],
            subject=subject,
            confirmation_code=code,
        )

    elif re.match(MATCHERS['unsubscribe'], m['subject']):
        _log('subscription')
        code = _confirmation_code()
        e = _just_email_address(m['from'])
        nums = M.search(None, 'MESSAGE-ID "%s"' % subs[e])
        if not nums:
            raise NotImplementedError
        M.fetch(nums.split()[0]

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

        if code not in confirmations:
            raise NotImplementedError
        confirmation = confirmations[code]

        raise NotImplementedError
        if confirmation['action'] == 'message':
            M.copy(confirmation['num'], 'Sent')
            M.store(confirmation['num'], '+FLAGS', '\\DELETED')
        elif confirmation['action'] == 'subscribe':
            M.store(confirmation['num'], '-FLAGS', '\\DRAFT')
        elif confirmation['action'] == 'unsubscribe':
            M.store(confirmation['num'], '-FLAGS', '\\FLAGGED')
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
