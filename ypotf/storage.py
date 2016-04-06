import datetime

from functools import partial

from email import message_from_bytes
from email.message import Message

def message_nums(M):
    return r(M.search(None, 'ALL'))[0].split()

def _list_messages(M):
    for num in message_nums(M):
        data = r(M.fetch(num, '(RFC822)'))
        yield num, message_from_bytes(data[0][1])

def first_message(M):
    nums = message_nums(M)
    if len(nums) > 0:
        num = nums[0]
        data = r(M.fetch(num, '(RFC822)'))
        return num, message_from_bytes(data[0][1])
    else:
        return None, None

class Folder(object):
    '''
    >>> Folder(imaplib.IMAP4('foo.bar'))
    '''
    def __init__(self, M):
        self.M = M

    def items(self):
        r(self.M.select(self.name))
        for num, m in _list_messages(self.M):
            yield m['subject'], m.get_payload()
        r(self.M.close())

    def __getitem__(self, key):
        r(self.M.select(self.name))
        for num, m in _list_messages(self.M):
            if m['Subject'] == key:
                out = m.get_payload()
                break
        else:
            out = None
        r(self.M.close())
        return out

    def __setitem__(self, key, value):
        d = tuple(datetime.datetime.now().timetuple())
        m = Message()
        m['Subject'] = key
        m.set_payload(value)
        r(self.M.append(self.name, None, d, m.as_bytes()))

    def __delitem__(self, key):
        r(self.M.select(self.name))
        for num, m in _list_messages(self.M):
            if m['Subject'] == key:
                r(self.M.store(num, '+FLAGS', '\\Deleted'))
                r(self.M.expunge())
                break
        else:
            msg = 'Key "%s" is not in folder "%s"'
            raise KeyError(msg % (key, self.name))
        r(self.M.close())

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

def _move(mailbox, M, num):
    r(M.copy(num, mailbox))
    r(M.store(num, '+FLAGS', '\\Deleted'))
    r(M.expunge())

archive_message = partial(_move, MAILBOXES['archive'])
queue_message = partial(_move, MAILBOXES['queue'])

def send_message(M, message_id):
    r(M.select(MAILBOXES['queue']))
    for num, msg in _list_messages(M):
        if msg['message-id'] == message_id:
            del(msg['To'])
            _move(MAILBOXES['sent'], M, num)
            break
    else:
        raise ValueError('No such message in the queue')
    r(M.close())
    return msg
