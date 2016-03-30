import datetime

from .fixtures import bare_imap, populated_imap
from .. import storage

class Inbox(storage.Folder):
    name = 'INBOX'
    
def test_getitem(populated_imap):
    populated_imap.select('INBOX')
    db = Inbox(populated_imap)
    assert db['key2'] == 'value2'

def test_setitem(bare_imap):
    bare_imap.select('INBOX')
    db = Inbox(bare_imap)
    db['key'] = 'value'
    typ, data = bare_imap.search(None, 'ALL')
    assert typ == 'OK'
    assert data == [b'1']
    typ, data = bare_imap.fetch(b'1', '(RFC822)')
    assert typ == 'OK'
    print(data)
    assert data == [
        (
            b'1 (FLAGS (\\Seen \\Recent) RFC822 {21}',
            b'Subject: key\r\n\r\nvalue'
        ),
        b')',
    ]
