from random import sample
import re
import logging
import datetime
from functools import partial
from copy import deepcopy

from email.message import Message
from email import message_from_bytes

from . import templates
from . import search
from .utils import r

logger = logging.getLogger(__name__)

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('list-confirm', r'.*{([a-z0-9]{32})}.*'),
#   ('list-archive', r'^list-archive'),
    ('help', r'^help$'),
]}

_now = datetime.datetime.now

def _confirmation_code():
    return uuid.uuid1().hex

def _prepare_send(msg):
    m = deepcopy(msg)
    m['X-Ypotf-Id'] = _confirmation_code()
    m['X-Ypotf-Date'] = email.utils.format_datetime(_now())
    return m

append_tpl = '''Appending this message to %s
----------------------------------------
%s
----------------------------------------''' 

send_tpl = '''Sending this message to %s
----------------------------------------
%s
----------------------------------------'''
from .templates import list_address

class Transaction(object):
    def __init__(self, S, M):
        self._S = S
        self._M = M

    def __enter__(self, box='Inbox'):
        self._finalize = []
        self._revert = []
        self._box = box

        r(self._M.select(self._box))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            for f, args in self._finalize:
                f(*args)
        else:
            logger.info('Exception occurred in transaction, aborting.')
            for f, args in self._revert:
                f(*args)
        r(self._M.close())

    def plus_flags(self, num, flags):
        self._revert.append((self._store, (num, '-FLAGS', flags)))
        return self._store(num, '+FLAGS', flags)

    def minus_flags(self, num, *flags):
        self._revert.append((self._store, (num, '+FLAGS', flags)))
        return self._store(num, '-FLAGS', flags)

    def _store(self, num, action, flags):
        return r(self._M.store(num, action, flags))

    def send(self, msg, *to_addresses):
        logger.info('Sending to %d addresses' % len(to_addresses))
        msg2 = _prepare_send(msg) # sent message kind 2

        if msg2['To'].lower() == list_address:
            msg2['Bcc'] = ', '.join(to_addresses)
            self.append('Sent', '\\SEEN', msg1)

        for to_address in to_addresses:
            msg1 = _prepare_send(msg) # sent message kind 1
            logger.debug(send_tpl % (to_address, msg1))
            self.append('Sent', '\\SEEN', msg1)
            self.S.send_message(msg1, list_address, [to_address])

    def append(self, box, flags, m, force_revert=False):
        '''
        It is possible to append to boxes other than the current one.
        This gets interesting.
        '''
        if 'seen' not in flags.lower():
            raise ValueError('"\\Seen" must be a flag.')
        logger.debug(append_tpl % (box, m))

        append_id = _confirmation_code()
        m['X-Ypotf-Append'] = append_id
        if box == self._box:
            self._revert.append(self._revert_append, (box, append_id))
        else:
            # Put it at the beginning of the revert list so it runs last.
            self._revert.insert(0, self._revert_append, (box, append_id))

        d = tuple(_now().timetuple())
        return r(self._M.append(box, flags, d, m.as_bytes()))

    def _revert_append(box, append_id):
        query = 'HEADER X-Ypotf-Append %s' % append_id))

        if self._box != box:
            self._M.select(box)
        self._box = box
        
        num = search.get_num(M, query)
        self._store(num, '+FLAGS', '\\DELETED')

def process(S, M, num, from_address, subject, message_id):
    for k, v in MATCHERS.items():
        if re.match(v, subject):
            action = k
            break
    else:
        action = 'message'
    
    with Transaction(S, M) as t:
        if action == 'help':
            t.plus_flags(num, '\\SEEN \\ANSWERED')
            t.send(templates.help(from_address), from_address)

        elif action == 'list-archive':
            raise NotImplementedError

        elif action == 'message':
            code = _confirmation_code()
            data = r(M.fetch(num, '(RFC822)'))
            m = message_from_bytes(data[0][1])
            m['TO'] = code

            t.send(templates.confirmation(action, from_address, code),
                   from_address)
            t.append('Inbox', '\\SEEN \\DRAFT', m)
            t.plus_flags(num, '\\SEEN \\ANSWERED')

        elif action == 'subscribe':
            flags = '\\FLAGGED \\DRAFT \\SEEN'
            draft_num, code = search.inbox.subscriber(M, from_address)

            if draft_num and code:
                logger.debug('Reusing existing pending confirmation')
                t.plus_flags(draft_num, flags)
            elif draft_num:
                logger.debug('Already subscribed')
                raise NotImplementedError
            else:
                logger.debug('Creating a new pending confirmation')
                code = _confirmation_code()
                m = templates.subscriber(to=code, subject=from_address)
                t.append('Inbox', flags, m)

            t.send(templates.confirmation(action, from_address, code),
                   from_address)
            t.add_flags(num, '+FLAGS', '\\SEEN \\ANSWERED')

        elif action == 'unsubscribe':
            draft_num, code = search.inbox.subscriber(M, from_address)
            if draft_num and code:
                # Add confirmation code to unsubscribe message.
                m = _message(to=code, subject=from_address)
                t.append('Inbox', '\\FLAGGED \\SEEN', m)
                t.send(templates.confirmation(action, from_address, code),
                       from_address)
                t.plus_flags(draft_num, '\\DELETED')
            else:
                t.send(templates.not_a_member(from_address), from_address)
            t.plus_flags(num, '\\SEEN \\ANSWERED')

        elif action == 'list-confirm':
            code = re.match(MATCHERS['list-confirm'], subject).group(1)
            draft_num, draft_action = search.inbox.confirmation(M, code)
            if draft_num and draft_action:
                if draft_action == 'message':
                    data = r(M.fetch(draft_num, '(RFC822)'))
                    to_addresses = search.inbox.subscribers(M)

                    t.plus_flags(draft_num, '\\DELETED')
                    t.plus_flags(num, '\\ANSWERED')
                    m = templates.message(message_from_bytes(data[0][1]))
                    t.send(m, *to_addresses)

                elif draft_action == 'subscribe':
                    data = r(M.fetch(draft_num, '(RFC822)'))
                    m = message_from_bytes(data[0][1])
                    del(m['TO'])
                    t.plus_flags(draft_num, '\\DELETED')
                    t.append('Inbox', '\\FLAGGED \\SEEN', m)

                elif c_action == 'unsubscribe':
                    t.minus_flags(c_num, '\\FLAGGED')

                else:
                    raise ValueError
            else:
                logger.warning('Invalid confirmation code')
            t.plus_flags(num, '\\SEEN')

        else:
            raise ValueError('Bad action')
