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
from .utils import r, _uuid

logger = logging.getLogger(__name__)

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('list-confirm', r'.*{([a-z0-9]{32})}.*'),
#   ('list-archive', r'^list-archive'),
    ('help', r'^help$'),
]}

_now = datetime.datetime.now

def _prepare_send(msg):
    m = deepcopy(msg)
    m['X-Ypotf-Id'] = _uuid()
    m['X-Ypotf-Date'] = email.utils.format_datetime(_now())
    return m

from .templates import list_address

def process(S, M, num, from_address, subject, message_id):
    for k, v in MATCHERS.items():
        if re.match(v, subject):
            action = k
            break
    else:
        action = 'message'

    logging.debug('"%s" request from "%s"' % (action, from_address))
    
    with Transaction(S, M) as t:
        t.store_current(num)
        if action == 'help':
            t.send(templates.help(from_address), from_address)

        elif action == 'list-archive':
            raise NotImplementedError

        elif action == 'message':
            # XXX skip confirmation if this is from a subscriber with
            # good SFP.
            code = _uuid()
            XXX m = templates.i_message_confirmation(fetch_num(num), code)
            t.append_pending(m)
            t.send(templates.message_confirm(from_address, code),
                   from_address)

        elif action == 'subscribe':
            if search.inbox.current(from_address):
                logger.debug('Already subscribed')
                raise NotImplementedError
            else:
                code = search.inbox.pending(M, from_address)
                if code:
                    logger.debug('Reusing existing pending subscription')
                else:
                    logger.debug('Creating a new pending subscription')
                    code = _uuid()
                    m = templates.i_subscriber(from_address, code)
                    t.append_pending(m)
                t.send(templates.subscribe_confirm(from_address, code),
                       from_address)

        elif action == 'unsubscribe':
            code = search.inbox.current(from_address)
            if code:
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
                    t.store_deleted(draft_num)
                    t.send(m, *to_addresses)

                elif draft_action == 'subscribe':
                    t.store_current(draft_num)

                elif draft_action == 'unsubscribe':
                    t.store_deleted(draft_num)

                else:
                    raise ValueError
            else:
                logger.warning('Invalid confirmation code')

        else:
            raise ValueError('Bad action')
