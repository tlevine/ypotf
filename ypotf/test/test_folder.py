import datetime

import pytest

from .fixtures import bare_imap, populated_imap
from .utils import r
from .. import storage

class Inbox(storage.Folder):
    name = 'INBOX'
    
def test_items(populated_imap):
    r(populated_imap.select('INBOX'))
    db = list(Inbox(populated_imap).items())
    assert db == [
        ('key1', 'value1'),
        ('key2', 'value2'),
    ]

def test_getitem(populated_imap):
    r(populated_imap.select('INBOX'))
    db = Inbox(populated_imap)
    assert db['key2'] == 'value2'

def test_setitem(bare_imap):
    r(bare_imap.select('INBOX'))
    db = Inbox(bare_imap)
    db['key'] = 'value'
    assert r(bare_imap.search(None, 'ALL')) == [b'1']
    assert r(bare_imap.fetch(b'1', '(RFC822)')) == [
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

    r(populated_imap.select('INBOX'))
    assert r(populated_imap.search(None, 'ALL')) == [b'1']
