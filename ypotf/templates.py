from email.message import Message

def confirmation(action, code):
    m = Message()
    m['Subject'] = 'Verify your email address {%s}' % code
    tpl = 'Reply to verify your email address and %s.'
    _desc = {
        'subscribe': 'finish subscribing',
        'unsubscribe': 'unsubscribe',
        'message': 'publish the message you just sent',
    }
    m.set_payload(tpl % _desc[action])
    return m

def help():
    m = Message()
    m['Subject'] = 'List help'
    m.set_payload('Documentation will eventually go here.')
    return m

def subscriber(**headers):
    m = Message()
    for key, value in headers.items():
        m[key] = value
    return m

FORWARDED_HEADERS = {
    'from', 'to',
    'cc', 'subject', 'date',
    'user-agent',
    'mime-version', 'content-type', 'content-transfer-encoding',
    'message-id', 'in-reply-to', 'references',
}
LIST_HEADERS = {
    'From': '_@dada.pink',
    'List-Id': '_.dada.pink',
    'List-Unsubscribe': 'mailto:_@dada.pink?subject=unsubscribe',
    'List-Archive': 'mailto:_@dada.pink?subject=list-archive',
    'List-Post': 'mailto:_@dada.pink',
    'List-Help': 'mailto:_@dada.pink?subject=help',
    'List-Subscribe': 'mailto:_@dada.pink?subject=subscribe',
}

def _finish(msg, list_address):
    for header in msg:
        if header.lower() not in FORWARDED_HEADERS:
            del(msg[header])

    if 'From' not in msg:
        for k, v in LIST_HEADERS.items():
            if k in msg:
                del(msg[k])
            msg[k] = v

    if '@' not in msg.get('To', ''):
        del(msg['To'])
        msg['To'] = list_address

    return msg
