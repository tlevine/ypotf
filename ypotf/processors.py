import imaplib

* Confirmations
* Queued messages

def confirm(confirmation_code):
    '''
    Based on a confirmation code, determine what action to take next.

    :param str confirmation_code: Confirmation code from email
    :rtype: Action
    :returns: Action to take based on the confirmation code
    '''
    M.select('confirmations')

def subscribe(M, num):
    _message(num)['from']
    M.append('ypotf-list', flags, date_time, message)

def unsubscribe(M, num):
    _message(num)['from']
    M.select('ypotf-list')

def send_message(M, message_id):
    M.select('ypotf-queue')
    for num, msg in _messages(M):
        if msg['message-id'] == message_id:
            raise NotImplementedError('Send the message with SMTP')
            M.copy(num, 'Sent')
            M.expunge()

def queue_message(M, num):
    M.copy(num, 'ypotf-queue')
    M.expunge()

def _messages(M):
    typ, data = M.search(None, 'ALL')
    nums = data[0].split()

    for num in nums:
        typ, data = M.fetch(num, '(RFC822)')
        yield num, email.message_from_bytes(data[0][1])

def _message(M, num):
    typ, data = M.fetch(num, '(RFC822)')
    return email.message_from_bytes(data[0][1])
