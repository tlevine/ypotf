from email.message import Message

list_address = '_@dada.pink'
FORWARDED_HEADERS = {
    'from',
    'subject', 'date', 'user-agent',
    'mime-version', 'content-type', 'content-transfer-encoding',
    'message-id', 'in-reply-to', 'references',
}
LIST_HEADERS = {
    'List-Id': list_address.replace('@', '.'),
    'List-Unsubscribe': 'mailto:%s?subject=unsubscribe' % list_address,
    'List-Archive': 'mailto:%s?subject=list-archive' % list_address,
    'List-Post': 'mailto:%s' % list_address,
    'List-Help': 'mailto:%s?subject=help' % list_address,
    'List-Subscribe': 'mailto:%s?subject=subscribe' % list_address,
}
def _set_list_headers(msg):
    for header in msg:
        if header.lower() not in FORWARDED_HEADERS:
            del(msg[header])

    for k, v in LIST_HEADERS.items():
        if k in msg:
            del(msg[k])
        msg[k] = v
    return msg

def confirmation(action, to_address, code):
    m = _set_list_headers(Message())
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

def help(to_address):
    m = _set_list_headers(Message())
    m['To'] = to_address
    m['From'] = list_address
    m['Subject'] = 'List help'
    m.set_payload('Documentation will eventually go here.')
    return m

def subscriber(**headers):
    m = Message()
    for key, value in headers.items():
        m[key] = value
    return m

def message(msg):
    m = _set_list_headers(msg)
    del(msg['To'])
    msg['To'] = list_address
    return msg
