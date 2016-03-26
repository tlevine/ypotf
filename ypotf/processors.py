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
    c = Confirmations(M)
    raise NotImplementedError
    M.select('ypotf-confirmations')

    M.close()

def subscriptions(M, m):

    def new(self, direction):
        if direction not in {'subscribe', 'unsubscribe'}:
            raise ValueError('direction must be "subscribe" or "unsubscribe"')
        code = bytes(random.randint(32, 126) for _ in range(32))
        self[code] = direction
        return code

    confirmation_code = storage.Confirmations(M).new(m['subject'])
    return templates.confirmation(
        subject=m['subject'],
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

