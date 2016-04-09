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

log_tpl = '''%s this message to %s
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
        self._select(box)
        return self

    def _select(self, box):
        if self._box != box:
            self._box = box
            r(self._M.select(self._box))
            logger.debug('Selected box %s' % self._box)

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

    def _store(self, *args):
        '''
        :param args: Tuple of num, action, flags
        '''
        logger.debug('STORE %d %s (%s)' % *args)
        return r(self._M.store(*args))

    def send(self, msg, *to_addresses):
        logger.info('Sending to %d addresses' % len(to_addresses))
        msg2 = _prepare_send(msg) # sent message kind 2

        if msg2['To'].lower() == list_address:
            msg2['Bcc'] = ', '.join(to_addresses)
            self.append('Sent', '\\SEEN', msg2)

        for to_address in to_addresses:
            msg1 = _prepare_send(msg) # sent message kind 1
            logger.debug(log_tpl % ('Sending', to_address, msg1))
            self.append('Sent', '\\SEEN', msg1)
            self.S.send_message(msg1, list_address, [to_address])

    def append(self, box, flags, m):
        '''
        It is possible to append to boxes other than the current one.
        This gets interesting.
        '''
        if 'seen' not in flags.lower():
            raise ValueError('"\\Seen" must be a flag.')
        logger.debug(log_tpl % ('Appending', to_address, msg1))

        append_id = _confirmation_code()
        m['X-Ypotf-Append'] = append_id

        # Reverting an append may require a switch of box.
        # Put it at the beginning of the revert list so it runs last.
        self._revert.insert(0, self._revert_append, (box, append_id))

        d = tuple(_now().timetuple())
        return r(self._M.append(box, flags, d, m.as_bytes()))

    def _revert_append(box, append_id):
        query = 'HEADER X-Ypotf-Append %s' % append_id))
        self._select(box)
        
        num = search.get_num(M, query)
        self._store(num, '+FLAGS', '\\DELETED')

def process(S, M, num, from_address, subject, message_id):
    for k, v in MATCHERS.items():
        if re.match(v, subject):
            action = k
            break
    else:
        action = 'message'

    logging.debug('"%s" request from "%s"' % (action, from_address))
    
    with Transaction(S, M) as t:
        t.plus_flags(num, '\\SEEN')
        if action == 'help':
            t.send(templates.help(from_address), from_address)

        elif action == 'list-archive':
            raise NotImplementedError

        elif action == 'message':
            code = _confirmation_code()
            m = templates.i_message_confirmation(fetch_num(num), code)
            t.append('Inbox', '\\SEEN \\DRAFT', m)
            t.send(templates.message_confirm(from_address, code),
                   from_address)

        elif action == 'subscribe':
            if is_subscriber(from_address):
                logger.debug('Already subscribed')
                raise NotImplementedError
            else:
                code = search.inbox.pending_subscribe(M, from_address)
                if code:
                    logger.debug('Reusing existing pending subscription')
                else:
                    logger.debug('Creating a new pending subscription')
                    code = _confirmation_code()
                    m = templates.i_subscriber(from_address, code)
                    t.append('Inbox', '\\FLAGGED \\SEEN \\DRAFT', m)
                t.send(templates.subscribe_confirm(from_address, code),
                       from_address)

        elif action == 'unsubscribe':
            draft_num, code = current_subscriber(from_address):
            if draft_num and code:
                t.minus_flags(draft_num, '\\SEEN')
                t.send(templates.unsubscribe_confirm(from_address, code),
                       from_address)
            else:
                t.send(templates.not_a_member(from_address), from_address)

        elif action == 'list-confirm':
            code = re.match(MATCHERS['list-confirm'], subject).group(1)
            draft_num, draft_action = search.inbox.confirmation(M, code)
            if draft_num and draft_action:
                if draft_action == 'message':
                    m = search.fetch_num(draft_num)
                    to_addresses = search.inbox.subscribers(M)
                    t.plus_flags(draft_num, '\\ANSWERED')
                    t.send(m, *to_addresses)

                elif draft_action == 'subscribe':
                    t.minus_flags(draft_num, '\\DRAFT')

                elif draft_action == 'unsubscribe':
                    t.minus_flags(draft_num, '\\ANSWERED')

                else:
                    raise ValueError
            else:
                logger.warning('Invalid confirmation code')

        else:
            raise ValueError('Bad action')
