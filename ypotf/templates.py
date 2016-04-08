from email.message import Message

def confirmation_message(action, code):
    m = Message()
    m['Subject'] = 'list-confirm-%s' % code
    m.set_payload('Reply to confirm your %s' % action)
    return m
