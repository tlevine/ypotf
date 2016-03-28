import datetime

from email import message_from_bytes
from email.message import Message

def message_nums(M):
    typ, data = M.search(None, 'ALL')
    return data[0].split()

def _list_messages(M):
    for num in _message_nums(M):
        typ, data = M.fetch(num, '(RFC822)')
        yield num, message_from_bytes(data[0][1])

def first_message(M):
    nums = message_nums(M)
    if len(nums) > 0:
        num = nums[0]
        typ, data = M.fetch(num, '(RFC822)')
        return num, message_from_bytes(data[0][1])
    else:
        return None, None

class Folder(object):
    '''
    >>> Folder(imaplib.IMAP4('foo.bar'), 'baz')
    '''
    def __init__(self, M):
        self.M = M

    def items(self):
        self.M.select(self.name)
        for num, m in _list_messages(self.M):
            yield m['subject'], m.get_payload()
        self.M.close()

    def __getitem__(self, key):
        self.M.select(self.name)
        for num, m in _list_messages(self.M):
            if m['Subject'] == key:
                out = m.get_payload()
        else:
            out = None
        self.M.close()
        return out

    def __setitem__(self, key, value):
        d = tuple(datetime.datetime.now().timetuple())
        m = Message()
        m['Subject'] = key
        m.set_payload(value)
        self.M.append(self.name, None, d, m.as_bytes())

    def __delitem__(self, key):
        self.M.select(self.name)
        for num, m in _list_messages(self.M):
            if m['Subject'] == key:
                self.M.store(num, '+FLAGS', '\\Deleted')
                self.M.expunge()
                break
        else:
            msg = 'Key "%s" is not in folder "%s"'
            raise KeyError(msg % (key, self.name))
        self.M.close()

MAILBOXES = {
    'list': 'ypotf-list',
    'confirmations': 'ypotf-confirmations',
    'archive': 'ypotf-archive',
    'queue': 'ypotf-queue',
    'sent': 'ypotf-sent',
}

class Subscribers(Folder):
    name = MAILBOXES['list']

class Confirmations(Folder):
    name = MAILBOXES['confirmations']

def archive_message(M, num):
    M.copy(num, MAILBOXES['archive'])
    M.store(num, '+FLAGS', '\\Deleted')
    M.expunge()

def queue_message(M, num):
    M.copy(num, MAILBOXES['queue'])
    M.store(num, '+FLAGS', '\\Deleted')
    M.expunge()

def send_message(M, message_id):
    M.select(MAILBOXES['queue'])
    for num, msg in messages(M):
        if msg['message-id'] == message_id:
            del(msg['To'])
            out = msg
            M.copy(num, MAILBOXES['sent'])
            M.store(num, '+FLAGS', '\\Deleted')
            M.expunge()
            break
    else:
        raise ValueError('No such message in the queue')
    M.close()
    return out
