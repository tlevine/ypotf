from random import sample
import re
import logging
import datetime
import string

from email.message import Message
from email import message_from_bytes

from . import templates
from . import search
from .utils import r

logger = logging.getLogger(__name__)

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('list-confirm', r'.*list-confirm-([a-z0-9]{32}).*'),
#   ('list-archive', r'^list-archive'),
    ('help', r'^help$'),
]}

CHARACTERS = string.ascii_lowercase + string.digits

def _confirmation_code():
    return ''.join(sample(CHARACTERS, 32))

def _store(M, num, action, flags):
    return r(M.store(num, action, flags))

def _append(box, M, flags, m):
    d = tuple(datetime.datetime.now().timetuple())
    if 'seen' not in flags.lower():
        raise ValueError('"\\Seen" must be a flag.')
    logger.debug('''Appending this message to %s
----------------------------------------
%s
----------------------------------------''' % (box, m))
    return r(M.append(box, flags, d, m.as_bytes()))

def _message(**headers):
    m = Message()
    for key, value in headers.items():
        m[key] = value
    return m  

class Transaction(object):
    def __enter__(self):
        self._queue = []
        return self._queue

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.info('Exception occurred in transaction, aborting.')
        else:
            for f, args in self._queue:
                f(*args)

FORWARDED_HEADERS = {
    'from', 'to',
    'cc', 'subject', 'date',
    'user-agent',
    'mime-version', 'content-type', 'content-transfer-encoding',
    'message-id', 'in-reply-to', 'references',
}
LIST_HEADERS = {
    'From': '_@dada.pink',
    'List-Id': '_.dada.pink',
    'List-Unsubscribe': 'mailto:_@dada.pink?subject=unsubscribe',
    'List-Archive': 'mailto:_@dada.pink?subject=list-archive',
    'List-Post': 'mailto:_@dada.pink',
    'List-Help': 'mailto:_@dada.pink?subject=help',
    'List-Subscribe': 'mailto:_@dada.pink?subject=subscribe',
}

def process(S, M, num, from_address, subject, message_id):
    for k, v in MATCHERS.items():
        if re.match(v, subject):
            action = k
            break
    else:
        action = 'message'
    
    def send(msg, to_address):
        if to_address == None:
            to_addresses = search.inbox.subscribers(M)
            logger.info('Sending to %d addresses' % len(to_addresses))
        else:
            to_addresses = {to_address}
        for to_address in to_addresses:
            for header in msg:
                if header.lower() not in FORWARDED_HEADERS:
                    del(msg[header])
            if 'From' not in msg:
                for k, v in LIST_HEADERS.items():
                    if k in msg:
                        del(msg[k])
                    msg[k] = v
            if '@' not in msg.get('To', ''):
                del(msg['To'])
                msg['To'] = '_@dada.pink'

            logger.debug('''Sending this message
----------------------------------------
%s
----------------------------------------''' % msg)

            with Transaction() as t:
                t.extend([
                    (S.send_message,
                        (msg, '_@dada.pink', [to_address])),
                    (_append, ('Sent', M, '\\SEEN', msg)),
                ])

    if action == 'help':
        send(templates.help(), from_address)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'list-archive':
        raise NotImplementedError

    elif action == 'message':
        code = _confirmation_code()
        data = r(M.fetch(num, '(RFC822)'))

        m = message_from_bytes(data[0][1])
        m['TO'] = code

        with Transaction() as t:
            t.extend([
                (send, (templates.confirmation_message(action, code),
                        from_address)),
                (_append, ('Inbox', M, '\\SEEN \\DRAFT', m)),
                (_store, (M, num, '+FLAGS', '\\SEEN \\ANSWERED'))
            ])

    elif action == 'subscribe':
        flags = '\\FLAGGED \\DRAFT \\SEEN'
        draft_num, code = search.inbox.subscriber(M, from_address)

        if draft_num and code:
            logger.debug('Reusing existing pending confirmation')
            r(M.store(draft_num, '+Flags', flags))
        elif draft_num:
            logger.debug('Already subscribed')
            raise NotImplementedError
        else:
            logger.debug('Creating a new pending confirmation')
            code = _confirmation_code()
            _append('Inbox', M, flags,
                    _message(to=code, subject=from_address))

        send(templates.confirmation_message(action, code), from_address)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'unsubscribe':
        draft_num, code = search.inbox.subscriber(M, from_address)
        with Transaction() as t:
            if draft_num and code:
                # Add confirmation code to unsubscribe message.
                t.extend([
                    (_store, (M, draft_num, '+FLAGS', '\\DELETED')),
                    (_append, ('Inbox', M, '\\FLAGGED \\SEEN',
                               _message(to=code, subject=from_address))),
                    (send, (templates.confirmation_message(action, code),
                            from_address)),
                ])
            else:
                t.append(send, (templates.not_a_member(), from_address))
            t.append(_store, (M, num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'list-confirm':
        code = re.match(MATCHERS['list-confirm'], subject).group(1)
        draft_num, draft_action = search.inbox.confirmation(M, code)
        if draft_num and draft_action:
            if draft_action == 'message':
                data = r(M.fetch(draft_num, '(RFC822)'))
                send(message_from_bytes(data[0][1]), None)

                r(M.copy(draft_num, 'Sent'))
                r(M.store(draft_num, '+FLAGS', '\\DELETED'))

                r(M.store(num, '+FLAGS', '\\ANSWERED'))

            elif draft_action == 'subscribe':
                data = r(M.fetch(draft_num, '(RFC822)'))
                m = message_from_bytes(data[0][1])
                del(m['TO'])
                r(M.store(draft_num, '+FLAGS', '\\DELETED'))
                _append('Inbox', M, '\\FLAGGED \\SEEN', m)

            elif c_action == 'unsubscribe':
                r(M.store(c_num, '-FLAGS', '\\FLAGGED'))

            else:
                raise ValueError
        else:
            logger.warning('Invalid confirmation code')
        r(M.store(num, '+FLAGS', '\\SEEN'))

    else:
        raise ValueError('Bad action')
