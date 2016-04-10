import re
import email
import datetime

from email.message import Message
from functools import partial

from .utils import email_address, uuid

def _now():
    return email.utils.format_datetime(datetime.datetime.now())

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

def _set_reply_headers(list_address, m_in, m_out):
    e = email_address(m_in['From'])
    m_out['To'] = e
    m_out['From'] = list_address
    m_out['Subject'] =  'Re: ' + re.sub(r'^ *Re: *', '', m_in['Subject'])
    rs = (m_in.get('References', ''), m_in.get('Message-Id', ''))
    m_out['References'] = ' '.join(rs).strip()
    m_out['Date'] = _now()
    return m_out

def subscribe_ok(list_address, m_in, code):
    m = _set_list_headers(list_address, Message())
    m['To'] = email_address(m_in['From'])
    m['From'] = list_address
    m['Subject'] = 'Verify your email address {%s}' % code
    m.set_payload('Reply to verify your email address and finish subscribing.')
    return m

def subscribe_fail_already_member(list_address, m_in):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    x = '''Your email address, %s, is already subscribed;
this subscription command did nothing.'''
    m.set_payload(x % email_address(m_in['From']))
    return m

def archive(list_address, m_in, subjects):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    m['Subject'] = 'List Archive'
    subjects_str = '\n  '.join(subjects)
    m.set_payload('''
Here are the subject lines of the past few messages.

  %s

I might improve this list archives feature eventually.''' % subjects_str)
    return m

def help(list_address, m_in):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    m['Subject'] = 'List help'
    m.set_payload('Documentation will eventually go here.')
    return m

def set_publication_headers(m):
    m['X-Ypotf-Id'] = uuid()
    m['X-Ypotf-Date'] = _now()
    return m

def set_publication_batch_headers(m, to_addresses):
    m['Bcc'] = ', '.join(to_addresses)
    return m

def publication_ok(list_address, msg):
    m = _set_list_headers(list_address, msg)
    del(msg['To'])
    msg['To'] = list_address
    return msg

def subscription(m_in):
    m = Message()
    m['Subject'] = email_address(m_in['From'])
    m['X-Ypotf-Id'] = uuid()
    m['X-Ypotf-Subscription'] = ''
    return m

def confirm_ok(list_address, m_in):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    x = '''Your email address, %s, has been added
to the %s list.'''
    m.set_payload(x % (email_address(m_in['From']), list_address))
    return m

def confirm_fail_already_confirmed(list_address, m_in, from_addr):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    del(m['To'])
    m['To'] = from_addr
    x = '''Your email address, %s, had already been confirmed;
this confirmation command did nothing.'''
    m.set_payload(x % email_address(m_in['From']))
    return m

def unsubscribe_ok(list_address, m_in):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    x = '''Your email address, %s, has been
removed from this mailing list.'''
    m.set_payload(x % e)
    return m

def unsubscribe_fail_not_member(list_address, m_in):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    e = email_address(m_in['From'])
    m.set_payload('''Your email address, %s, is already not on this
mailing list; your unsubscribe command did nothing.''' % e)
    return m

def error(list_address, m_in, text):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    m.set_payload(text)
    return m
