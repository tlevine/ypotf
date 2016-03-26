from email.messages import Message

def list_messages(M):
    typ, data = M.search(None, 'ALL')
    nums = data[0].split()

    for num in nums:
        typ, data = M.fetch(num, '(RFC822)')
        yield num, email.message_from_bytes(data[0][1])

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


class Folder(object):
    '''
    >>> Folder(imaplib.IMAP4('foo.bar'), 'baz')
    '''
    def __init__(self, M):
        self.M = M

    def items(self):
        M.select(self.name)
        for num, m in list_messages(self.M):
            yield m['subject'], m.get_payload()
        M.close()

    def __getitem__(self, key):
        for num, m in list_messages(M):
            if m['Subject'] == key:
                return m.get_payload()

    def __setitem__(self, key, value):
        d = datetime.datetime.now().timetuple()
        m['Subject'] = key
        m.set_payload(value)
        M.append(self.name, None, d, m.as_bytes())

    def __delitem__(self, key):
        M.select(self.name)
        for num, m in list_messages(M):
            if m['Subject'] == key:
                M.store(num, '+FLAGS', '\\Deleted')
                M.expunge()
                break
        else:
            msg = 'Key "%s" is not in folder "%s"'
            raise KeyError(msg % (key, self.name))
        M.close()

class List(Folder):
    name = 'ypotf-list'

class Confirmations(Folder):
    name = 'ypotf-confirmations'
