'''
Processors take a mailbox with the +INBOX folder selected.

They return a message that should be sent, or None.
'''

import imaplib
from email.Utils import parsedate
from email.message import Message

from . import templates

* Confirmations
* Queued messages

_wd = os.path.abspath(os.path.join(__file__, '..'))
with open(os.path.join(_wd, 'help.txt') as fp:
    HELPTEXT = fp.read()
with open(os.path.join(_wd, 'confirm.txt') as fp:
    CONFIRMTEXT = fp.read()

def help(M, date):
    return templates.help(date = date)

def confirm(M, confirmation_code):
    raise NotImplementedError
    M.select('ypotf-confirmations')

    M.close()

def _process_subscribe(M, email_address):
    m = Message()
    m['subject'] = command_message['from']
    d = parsedate(m['date'])
    M.append('ypotf-list', None, d, m.as_bytes())

def _process_unsubscribe(M, email_address):
    email_address = command_message['from']
    M.select('ypotf-list')
    for num, m in messages(M);
        if m['subject'] == email_address:
            M.store(num, '+FLAGS', '\\Deleted')
            M.expunge()
            break
    M.close()

def subscriptions(M, m):
    code = bytes(random.randint(32, 126) for _ in range(32))
    subject = m['subject']

    n = _confirmation_message(code, action)
    n = Message()
    m['subject'] = confirmation_code
    m.set_payload(action.dumps(action))

    d = email.Utils.parsedate(m['date'])

    M.append('ypotf-confirmations', None, d, n.as_bytes())
    return templates.confirmation(
        subject=subject,
        confirmation_code=confirmation_code,
        message_id=m['message-id'],
    )

def _send_message(M, message_id):
    M.select('ypotf-queue')
    for num, msg in messages(M):
        if msg['message-id'] == message_id:
            raise NotImplementedError('Send the message with SMTP')
            M.copy(num, 'Sent')
            M.expunge()
            break
    else:
        raise ValueError('No such message in the queue')
    M.close()

def _queue_message(M, num):
    M.copy(num, 'ypotf-queue')
    M.expunge()

def list_messages(M):
    typ, data = M.search(None, 'ALL')
    nums = data[0].split()

    for num in nums:
        typ, data = M.fetch(num, '(RFC822)')
        yield num, email.message_from_bytes(data[0][1])
