from random import sample
import re
import logging
import datetime
from functools import partial

from . import read, templates
from .write import Writer

logger = logging.getLogger(__name__)

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('confirm', r'.*{([a-z0-9]{32})}.*'),
    ('archive', r'^list-archive'),
    ('help', r'^help$'),
]}

_now = datetime.datetime.now

def process(list_address, S, M, num, m):
    for k, v in MATCHERS.items():
        if re.match(v, m['Subject']):
            action = k
            break
    else:
        action = 'publication'

    logging.debug('"%s" request from "%s"' % (action, m['From']))

    with Writer(list_address, S, M) as t:
        t.store_current(num)
        if action == 'help':
            t.send(templates.help(m['From'], message_id))

        elif action == 'list-archive':
            x = 'List archives are not implemented yet.'
            t.send(templates.error(x, m['From'], message_id))

        elif action == 'publication':
            if read.is_subscribed(M, m['From']):
                # Skip confirmation if this is "From" a subscriber
                # Rely on the email provider to have SPF, DKIM,
                # and spam filtering.
                m = templates.publication_ok(m)
                to_addresses = read.subscribers(M)
                t.send(m, to_addresses)
            else:
                t.send(templates.publication_not_a_member(m))

        elif action == 'subscribe':
            if read.is_subscribed(M, m['From']):
                t.send(templates.subscribe_fail_already_member(m))
            else:
                code = read.subscription_ypotf_id(M, m['From'])
                if code:
                    logger.debug('Reusing existing pending subscription')
                else:
                    logger.debug('Creating a new pending subscription')
                    t.append_pending(templates.subscription(m))
                t.send(templates.subscribe_ok(m['From'], code))

        elif action == 'unsubscribe':
            code = read.subscription_ypotf_id(M, m['From'])
            if code:
                sub_num = read.ypotf_id_num(M, code)
                t.store_deleted(sub_num)
                t.send(templates.unsubscribe_ok(m['From']))
            else:
                t.send(templates.unsubscribe_fail_not_member(m['From']))

        elif action == 'confirm':
            code = re.match(MATCHERS['confirm'], subject).group(1)
            sub_num = read.ypotf_id_num(M, code)
            if sub_num:
                t.store_current(draft_num)
                t.send(templates.subscribe(m['From']), from_address)
            else:
                t.send(templates.error('Invalid confirmation code'),
                       m['From'])

        else:
            logger.error('Bad action')
