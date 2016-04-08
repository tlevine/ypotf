from random import sample
import re
import logging
import datetime
import string
from functools import partial

from email.message import Message
from email import message_from_bytes

from . import templates
from . import search
from . import send
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

def _append(box, M, flags, m):
    d = tuple(datetime.datetime.now().timetuple())
    if 'seen' not in flags.lower():
        raise ValueError('"\\Seen" must be a flag.')
    logger.debug('''Appending this message to %s
----------------------------------------
%s
----------------------------------------''' % (box, m))
    return r(M.append(box, flags, d, m.as_bytes()))


log_tpl = '''Sending this message
----------------------------------------
%s
----------------------------------------'''
list_address = '_@dada.pink'

class Transaction(object):
    def __init__(self, S, M):
        self.S = S
        self.M = M

    def __enter__(self):
        self._finalize = []
        self._revert = []
        return self._finalize

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            for f, args in self._finalize:
                f(*args)
        else:
            logger.info('Exception occurred in transaction, aborting.')
            for f, args in self._revert:
                f(*args)

    def plus_flags(self, num, flags):
        self._revert.append((self._store, (num, '-FLAGS', flags)))
        return self._store(num, '+FLAGS', flags)

    def minus_flags(self, num, *flags):
        self._revert.append((self._store, (num, '+FLAGS', flags)))
        return self._store(num, '-FLAGS', flags)

    def _store(self, num, action, flags):
        return r(M.store(num, action, flags))

    def send(self, msg, to_addresses):
        for to_address in to_addresses:
            # This is not reverted.
            _append('Sent', self.M, '\\SEEN', msg)
            S.send_message(msg, list_address, [to_address])

    def append(self, box, msg, flags):
        # This is not reverted.
        _append(box, self.M, '\\SEEN \\DRAFT', msg)

def process(S, M, num, from_address, subject, message_id):
    _send = partial(send.send, S, M)

    for k, v in MATCHERS.items():
        if re.match(v, subject):
            action = k
            break
    else:
        action = 'message'
    
    with Transaction() as t:
        if action == 'help':
            t.plus_flags(num, '\\SEEN \\ANSWERED')
            t.send(templates.help(), from_address)

        elif action == 'list-archive':
            raise NotImplementedError

        elif action == 'message':
            code = _confirmation_code()
            data = r(M.fetch(num, '(RFC822)'))
            m = message_from_bytes(data[0][1])
            m['TO'] = code

            t.extend([
                (send, (templates.confirmation(action, code),
                        from_address)),
                (_append, ('Inbox', M, '\\SEEN \\DRAFT', m)),
            ])
            t.plus_flags(num, '\\SEEN \\ANSWERED')

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
                m = templates.subscriber(to=code, subject=from_address)
                _append('Inbox', M, flags, m)

            _send(templates.confirmation(action, code), from_address)
            r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

        elif action == 'unsubscribe':
            draft_num, code = search.inbox.subscriber(M, from_address)
            with Transaction() as t:
                if draft_num and code:
                    # Add confirmation code to unsubscribe message.
                    t.extend([
                        (_append, ('Inbox', M, '\\FLAGGED \\SEEN',
                                   _message(to=code, subject=from_address))),
                        (send, (templates.confirmation(action, code),
                                from_address)),
                    ])
                    t.plus_flags(draft_num, '\\DELETED')
                else:
                    t.append(send, (templates.not_a_member(), from_address))
                t.plus_flags(num, '\\SEEN \\ANSWERED'))

        elif action == 'list-confirm':
            code = re.match(MATCHERS['list-confirm'], subject).group(1)
            draft_num, draft_action = search.inbox.confirmation(M, code)
            if draft_num and draft_action:
                if draft_action == 'message':
                    data = r(M.fetch(draft_num, '(RFC822)'))
                    _send(message_from_bytes(data[0][1]), None)

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
