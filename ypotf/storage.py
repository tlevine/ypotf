from email.messages import Message

def list_messages(M):
    typ, data = M.search(None, 'ALL')
    nums = data[0].split()

    for num in nums:
        typ, data = M.fetch(num, '(RFC822)')
        yield num, email.message_from_bytes(data[0][1])

class Folder(object):
    '''
    >>> Folder(imaplib.IMAP4('foo.bar'), 'baz')
    '''
    def __init__(self, M, name):
        self.M = M
        self.name = name

    def items(self):
        M.select(self.name)
        for num, m in list_messages(self.M):
            yield m['subject'], m.get_payload()
        M.close()

    def __setitem__(self, key, value):
        d = datetime.datetime.now().timetuple()
        M.append(self.name, None, d, m.as_bytes())

    def __delitem__(self, key):
        M.select(self.name)
        for num, m in list_messages(M):
            if m['subject'] == key:
                M.store(num, '+FLAGS', '\\Deleted')
                M.expunge()
                break
        else:
            msg = 'Key "%s" is not in folder "%s"'
            raise KeyError(msg % (key, self.name))
        M.close()
