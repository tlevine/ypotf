'''
Processors take a mailbox with the +INBOX folder selected.

They return a message that should be sent, or None.
'''

import imaplib
from email.message import Message

* Confirmations
* Queued messages

def help(M, date):


def confirm(M, confirmation_code):
    confirmation_code = m['subject']
    raise NotImplementedError
    M.select('confirmations')

    M.close()

def subscribe(M, email_address):
    m = Message()
    m['subject'] = command_message['from']
    d = email.Utils.parsedate(m['date'])
    M.append('ypotf-list', None, d, m.as_bytes())

def unsubscribe(M, email_address):
    email_address = command_message['from']
    M.select('ypotf-list')
    for num, m in messages(M);
        if m['subject'] == email_address:
            M.store(num, '+FLAGS', '\\Deleted')
            M.expunge()
            break
    M.close()

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
