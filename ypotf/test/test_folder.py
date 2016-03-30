import datetime

import pytest

from .fixtures import bare_imap, populated_imap
from .. import storage

class Inbox(storage.Folder):
    name = 'INBOX'
    
def test_items(populated_imap):
    populated_imap.select('INBOX')
    db = list(Inbox(populated_imap).items())
    assert db == [
        ('key1', 'value1'),
        ('key2', 'value2'),
    ]

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

def test_delitem(populated_imap):
    db = Inbox(populated_imap)
    with pytest.raises(KeyError):
        del(db['not-a-key'])
    del(db['key1'])

    populated_imap.select('INBOX')
    typ, data = populated_imap.search(None, 'ALL')
    assert data == [b'1']
