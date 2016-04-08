from random import randint
import re

from email.message import Message
from email import message_from_bytes

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('list-confirm', r'list-confirm-[a-z0-9]{32}'),
#   ('list-archive', r'^list-archive'),
    ('help', r'^help$'),
]}

def _confirmation_code():
    return bytes(randint(32, 126) for _ in range(32)).decode('ascii')

def _append(M, flags, m):
    d = tuple(datetime.datetime.now().timetuple())
    if 'seen' not in flags.lower():
        raise ValueError('"\\Seen" must be a flag.')
    return r(M.append('Inbox', flags, d, m.as_bytes()))

def _message(**headers):
    m = Message()
    for key, value in headers.items():
        m[key] = value
    return m  

def process(M, num, from_address, subject, message_id):
    for k, v in MATCHERS.items():
        if re.match(v, h['SUBJECT']):
            action = k
    else:
        action = 'message'
    
    send = partial(full_send, message_id)

    if action == 'help':
        send(_help(), from_address)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'list-archive'
        raise NotImplementedError

    elif action == 'message':
        code = _confirmation_code()
        data = r(M.fetch(num, '(RFC822)'))

        m = message_from_bytes(data[0][1])
        m['TO'] = code


        send(_confirmation_message(action, code), from_address)
        _append(M, '\\SEEN \\DRAFT', m)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'subscribe':
        FLAGS = '\\FLAGGED \\DRAFT \\SEEN'
        draft_num, code = subscriber(M, from_address)

        if draft_num and code:
            # Reuse the existing message.
            M.store(draft_num, '+Flags', flags)
        else:
            code = _confirmation_code()
            _append(M, flags, _message(to=code, subject=from_address))

        send(_confirmation_message(action, code), from_address)
        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'unsubscribe':
        FLAGS = '\\FLAGGED \\SEEN'
        draft_num, code = subscriber(M, from_address)

        if draft_num and code:
            M.store(draft_num, '+FLAGS', '\\DELETED')
            _append(M, flags, _message(to=code, subject=from_address))
            send(_confirmation_message(action, code), from_address)
        else:
            send(_not_a_member(), from_address)

        r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

    elif action == 'list-confirm':
        code = re.match(MATCHERS['list-confirm'], subject).group(1)
        c_num, c_action = searches.Inbox.confirmations(M, code)
        if c_num and c_action:
            if c_action == 'message':
                data = r(M.fetch(num, '(RFC822)'))

                send(message_from_bytes(data[0][1]), None)
                r(M.copy(c_num, 'Sent'))
                r(M.store(c_num, '+FLAGS', '\\DELETED'))

                r(M.store(num, '+FLAGS', '\\SEEN \\ANSWERED'))

            elif c_action == 'subscribe':
                r(M.store(c_num, '-FLAGS', '\\DRAFT'))
                r(M.store(num, '+FLAGS', '\\SEEN'))

            elif c_action == 'unsubscribe':
                r(M.store(c_num, '-FLAGS', '\\FLAGGED'))
                r(M.store(num, '+FLAGS', '\\SEEN'))

            else:
                raise ValueError

    else:
        raise ValueError('Bad action')
