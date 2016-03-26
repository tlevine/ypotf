'''
Most actions take a mailbox with a folder selected, usually +INBOX.
'''

import imaplib
from email.message import Message

* Confirmations
* Queued messages

def confirm(M, num, confirmation_code):
    '''
    Based on a confirmation code, determine what action to take next.

    :param str confirmation_code: Confirmation code from email
    :rtype: Action
    :returns: Action to take based on the confirmation code
    '''
    M.select('confirmations')

    M.close()

def subscribe(M, command_message):
    m = Message()
    m['subject'] = command_message['from']
    d = email.Utils.parsedate(m['date'])
    M.append('ypotf-list', None, d, m.as_bytes())
    M.copy(num, 'ypotf-archive')
    M.expunge()

def unsubscribe(M, command_message):
    email_address = command_message['from']
    M.close()
    M.select('ypotf-list')
    for num, m in messages(M);
        if m['subject'] == email_address:
            M.store(num, '+FLAGS', '\\Deleted')
            M.expunge()
            break
    M.close()
    M.select('INBOX')
    M.copy(num, 'ypotf-archive')
    M.expunge()
    M.close()

def send_message(M, message_id):
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

def queue_message(M, num):
    M.copy(num, 'ypotf-queue')
    M.expunge()

def messages(M):
    typ, data = M.search(None, 'ALL')
    nums = data[0].split()

    for num in nums:
        typ, data = M.fetch(num, '(RFC822)')
        yield num, email.message_from_bytes(data[0][1])
