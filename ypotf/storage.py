from email import message_from_bytes
from email.message import Message

def message_nums(M):
    typ, data = M.search(None, 'ALL')
    return data[0].split()

def _list_messages(M):
    for num in _message_nums(M):
        typ, data = M.fetch(num, '(RFC822)')
        yield num, message_from_bytes(data[0][1])

class Folder(object):
    '''
    >>> Folder(imaplib.IMAP4('foo.bar'), 'baz')
    '''
    def __init__(self, M):
        self.M = M

    def items(self):
        M.select(self.name)
        for num, m in _list_messages(self.M):
            yield m['subject'], m.get_payload()
        M.close()

    def __getitem__(self, key):
        for num, m in _list_messages(M):
            if m['Subject'] == key:
                return m.get_payload()

    def __setitem__(self, key, value):
        d = datetime.datetime.now().timetuple()
        m = Message()
        m['Subject'] = key
        m.set_payload(value)
        M.append(self.name, None, d, m.as_bytes())

    def __delitem__(self, key):
        M.select(self.name)
        for num, m in _list_messages(M):
            if m['Subject'] == key:
                M.store(num, '+FLAGS', '\\Deleted')
                M.expunge()
                break
        else:
            msg = 'Key "%s" is not in folder "%s"'
            raise KeyError(msg % (key, self.name))
        M.close()

class Subscribers(Folder):
    name = 'ypotf-list'

class Confirmations(Folder):
    name = 'ypotf-confirmations'

def archive_message(M, num):
    M.copy(num, 'ypotf-archive')
    M.expunge()

def queue_message(M, num):
    M.copy(num, 'ypotf-queue')
    M.expunge()

def send_message(M, message_id):
    M.select('ypotf-queue')
    for num, msg in messages(M):
        if msg['message-id'] == message_id:
            raise NotImplementedError('Send the message with SMTP')
            M.copy(num, 'ypotf-sent')
            M.expunge()
            break
    else:
        raise ValueError('No such message in the queue')
    M.close()

def _confirmation_code():
    return bytes(random.randint(32, 126) for _ in range(32))
