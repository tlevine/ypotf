from email.message import Message

def confirmation_message(action, code):
    m = Message()
    m['Subject'] = 'list-confirm-%s' % code
    m.set_payload('Reply to confirm your %s' % action)
    return m

def help():
    m = Message()
    m['Subject'] = 'List help'
    m.set_payload('Documentation will eventually go here.')
    return m
