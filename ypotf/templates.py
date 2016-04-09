from email.message import Message
from functools import partial

FORWARDED_HEADERS = {
    'from',
    'subject', 'date', 'user-agent',
    'mime-version', 'content-type', 'content-transfer-encoding',
    'message-id', 'in-reply-to', 'references',
}
def _list_headers(list_address):
    return {
        'List-Id': list_address.replace('@', '.'),
        'List-Unsubscribe': 'mailto:%s?subject=unsubscribe' % list_address,
        'List-Archive': 'mailto:%s?subject=list-archive' % list_address,
        'List-Post': 'mailto:%s' % list_address,
        'List-Help': 'mailto:%s?subject=help' % list_address,
        'List-Subscribe': 'mailto:%s?subject=subscribe' % list_address,
    }

def _set_list_headers(list_address, msg):
    list_headers = _list_headers(list_address)
    for header in msg:
        if header.lower() not in FORWARDED_HEADERS:
            del(msg[header])

    for k, v in list_headers.items():
        if k in msg:
            del(msg[k])
        msg[k] = v
    return msg

def confirm_ok(action, list_address, to_address, code):
    m = _set_list_headers(list_address, Message())
    m['To'] = to_address
    m['From'] = list_address
    m['Subject'] = 'Verify your email address {%s}' % code
    tpl = 'Reply to verify your email address and %s.'
    _desc = {
        'subscribe': 'finish subscribing',
        'unsubscribe': 'unsubscribe',
        'message': 'publish the message you just sent',
    }
    m.set_payload(tpl % _desc[action])
    return m

def help(list_address, to_address):
    m = _set_list_headers(list_address, Message())
    m['To'] = to_address
    m['From'] = list_address
    m['Subject'] = 'List help'
    m['Date'] = email.utils.format_datetime(_now())
    m.set_payload('Documentation will eventually go here.')
    return m

def publication(list_address, msg):
    m = _set_list_headers(list_address, msg)
    del(msg['To'])
    msg['To'] = list_address
    m['X-Ypotf-Id'] = _uuid()
    m['X-Ypotf-Date'] = email.utils.format_datetime(_now())
    return msg

def subscriber(address):
    m = _set_ypotf_headers(Message())
    m['Subject'] = address
    m['X-Ypotf-Id'] = _uuid()
    return m

def publication_batch(list_address, m, to_addresses):
    m = publication(list_address, m)
    m['Bcc'] = ', '.join(to_addresses)
    return m
