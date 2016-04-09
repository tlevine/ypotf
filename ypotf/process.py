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
            x = 'List archives are not implemented yet.'
            t.send(templates.error(x), from_address)

        elif action == 'message':
            if search.is_subscribed(M, from_address):
                # Skip confirmation if this is "From" a subscriber
                # Rely on the email provider to have SPF, DKIM,
                # and spam filtering.
                m = templates.envelope.message(fetch_num(num))
                to_addresses = search.inbox.subscribers(M)
                t.send(m, *to_addresses)
            else:
                t.send(templates.not_a_member(from_address), from_address)

        elif action == 'subscribe':
            if search.inbox.current(from_address):
                t.send(templates.error('You are already subscribed.'),
                       from_address)
            else:
                code = search.inbox.pending(M, from_address)
                if code:
                    logger.debug('Reusing existing pending subscription')
                else:
                    logger.debug('Creating a new pending subscription')
                    m = templates.new.subscription(from_address, code)
                    t.append_pending(m)
                t.send(templates.subscribe_confirm(from_address, code),
                       from_address)

        elif action == 'unsubscribe':
            code = search.inbox.current(from_address) # XXX
            if code:
                t.send(templates.unsubscribe_confirm(from_address, code),
                       from_address)
            else:
                t.send(templates.not_a_member(from_address), from_address)

        elif action == 'list-confirm':
            code = re.match(MATCHERS['list-confirm'], subject).group(1)
            draft_num, draft_action = search.inbox.confirmation(M, code)
            if draft_num and draft_action:
                if draft_action == 'subscribe':
                    t.store_current(draft_num)
                elif draft_action == 'unsubscribe':
                    t.store_deleted(draft_num)
                else:
                    x = 'I can confirm only subscribe and unsubscribe.'
                    logger.error(x)
            else:
                t.send(templates.error('Invalid confirmation code'),
                       from_address)

        else:
            logger.error('Bad action')
