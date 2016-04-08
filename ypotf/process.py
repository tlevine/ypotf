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

def _append(M, flags, m):
    box = 'Inbox'
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

def process(S, M, num, from_address, subject, message_id):
    for k, v in MATCHERS.items():
        if re.match(v, subject):
            action = k
            break
    else:
        action = 'message'
    
    def send(msg, to_address):
        if to_address == None:
            raise NotImplementedError
        else:
            msg['To'] = to_address
        msg['From'] = '_@dada.pink'

        logger.debug('''Sending this message
----------------------------------------
%s
----------------------------------------''' % msg)

        S.send_message(msg)

    if action == 'help':
        send(_help(), from_address)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'list-archive':
        raise NotImplementedError

    elif action == 'message':
        code = _confirmation_code()
        data = r(M.fetch(num, '(RFC822)'))

        m = message_from_bytes(data[0][1])
        m['TO'] = code

        send(templates.confirmation_message(action, code), from_address)
        _append(M, '\\SEEN \\DRAFT', m)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'subscribe':
        flags = '\\FLAGGED \\DRAFT \\SEEN'
        draft_num, code = search.inbox.subscriber(M, from_address)

        if draft_num and code:
            logger.debug('Reusing existing pending confirmation')
            M.store(draft_num, '+Flags', flags)
        else:
            logger.debug('Creating a new pending confirmation')
            code = _confirmation_code()
            _append(M, flags, _message(to=code, subject=from_address))

        send(templates.confirmation_message(action, code), from_address)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'unsubscribe':
        draft_num, code = search.inbox.subscriber(M, from_address)
        if draft_num and code:
            # Add confirmation code to unsubscribe message.
            M.store(draft_num, '+FLAGS', '\\DELETED')
            _append(M, '\\FLAGGED \\SEEN',
                    _message(to=code, subject=from_address))
            send(templates.confirmation_message(action, code),
                 from_address)
        else:
            send(templates.not_a_member(), from_address)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'list-confirm':
        code = re.match(MATCHERS['list-confirm'], subject).group(1)
        draft_num, draft_action = search.inbox.confirmation(M, code)
        if draft_num and draft_action:
            if draft_action == 'message':
                data = r(M.fetch(num, '(RFC822)'))

                send(message_from_bytes(data[0][1]), None)
                r(M.copy(draft_num, 'Sent'))
                r(M.store(draft_num, '+FLAGS', '\\DELETED'))

                r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

            elif draft_action == 'subscribe':
                data = r(M.fetch(draft_num, '(RFC822)'))
                m = message_from_bytes(data[0][1])
                del(m['TO'])

                r(M.store(num, '+FLAGS', '\\SEEN'))
                M.store(draft_num, '+FLAGS', '\\DELETED')
                _append(M, '\\FLAGGED \\SEEN \\DRAFT', m)

            elif c_action == 'unsubscribe':
                r(M.store(c_num, '-FLAGS', '\\FLAGGED'))
                r(M.store(num, '+FLAGS', '\\SEEN'))

            else:
                raise ValueError
        else:
            logger.warning('Invalid confirmation code')

    else:
        raise ValueError('Bad action')
