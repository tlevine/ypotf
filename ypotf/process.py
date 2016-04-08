from random import randint
import re

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('confirmations', r'list-confirm-[a-z0-9]{32}'),
#   ('archive', r'^list-archive'),
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

def process(M, num, from_address, subject):
    for k, v in MATCHERS.items():
        if re.match(v, h['SUBJECT']):
            action = k
    else:
        action = 'message'
    
    # Defaults
    code = None

    if action == 'help':
        raise NotImplementedError
    elif action == 'archive'
        raise NotImplementedError
    elif action == 'subscribe':
        FLAGS = '\\FLAGGED \\DRAFT \\SEEN'
        draft_num, code = subscriber(M, from_address)
        if draft_num and code:
            # Reuse the existing message.
            M.store(draft_num, '+Flags', flags)
        else:
            code = _confirmation_code()
            _append(M, flags, _message(to=code, subject=from_address))

    elif action == 'unsubscribe':
        FLAGS = '\\FLAGGED \\SEEN'
        draft_num, code = subscriber(M, from_address)
        if draft_num and code:
            M.store(draft_num, '+FLAGS', '\\DELETED')
            _append(M, flags, _message(to=code, subject=from_address))

    elif action == 'message':
        code = re.match(MATCHERS['confirmations'], subject).group(1)
        c_num, c_action = searches.Inbox.confirmations(M, code)
        if c_num and c_action:
            if c_action == 'message':
                M.copy(c_num, 'Sent')
                M.store(c_num, '+FLAGS', '\\DELETED')
            elif c_action == 'subscribe':
                M.store(c_num, '-FLAGS', '\\DRAFT')
            elif c_action == 'unsubscribe':
                M.store(c_num, '-FLAGS', '\\FLAGGED')
            else:
                raise ValueError




    r(M.store(num, '+FLAGS', '\\Seen')
    return template.configure(
        'sender',
        to_address=m['From'],
        references=m['message-id'],
        subject=subject,
        confirmation_code=code,
    )
