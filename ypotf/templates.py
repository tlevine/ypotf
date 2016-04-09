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
    m_out['Subject'] = 'Re: %(Subject)ss' % m_in
    m_out['References'] = ('%(References)s %(Message-Id)s' % m_in).strip()
    m_out['Date'] = _now()
    return m_out

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

def subscription(m):
    m = Message()
    m['Subject'] = email_address(m['From'])
    m['X-Ypotf-Id'] = uuid()
    return m

def unsubscribe_ok(list_address, m_in):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    m['From'] = list_address
    x = 'Your email address, %s, has been removed from this mailing list.'
    m.set_payload(x % e)
    return m

def unsubscribe_fail_not_member(list_address, m_in):
    m = _set_list_headers(list_address, Message())
    m = _set_reply_headers(list_address, m_in, m)
    e = email_address(m_in['From'])
    m['Subject'] = 'Re: %(Subject)s' % m_in
    m.set_payload('''Your email address, %s, is already not on this
mailing list; your unsubscribe command did nothing.''' % e)
    return m
