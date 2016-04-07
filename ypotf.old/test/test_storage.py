from email.message import Message

from .fixtures import (
    bare_imap, populated_imap, ypotf_imap,
    _now,
)
from .. import storage

def test_listings(bare_imap):
    bare_imap.select('INBOX')

    m1 = Message()
    m1['Subject'] = 'unsubscribe'
    bare_imap.append('INBOX', None, _now(), m1.as_bytes())

    m2 = Message()
    m2['Subject'] = 'subscribe'
    bare_imap.append('INBOX', None, _now(), m2.as_bytes())

    bare_imap.close()

    bare_imap.select('INBOX')
    assert storage.message_nums(bare_imap) == [b'1', b'2']

    num, m = storage.first_message(bare_imap)
    assert num == b'1'
    assert m.as_string() == m1.as_string()

def test_move(populated_imap):
    populated_imap.create('chainsaw')

    populated_imap.select('INBOX')
    storage._move('chainsaw', populated_imap, b'2')

    populated_imap.select('chainsaw')
    typ, data = populated_imap.fetch(b'1', '(RFC822)')
    assert typ == 'OK'
    assert data == [
        (
            b'1 (FLAGS (\\Seen \\Recent) RFC822 {23}',
            b'Subject: key2\r\n\r\nvalue2',
        ),
        b')',
    ]


def test_send_message(ypotf_imap):
    m = Message()
    m['message-id'] = 'the-message-id'
    ypotf_imap.append(storage.MAILBOXES['queue'], None, _now(), m.as_bytes())
    storage.send_message(ypotf_imap, 'the-message-id')
    ypotf_imap.select(storage.MAILBOXES['sent'])
    typ, data = ypotf_imap.fetch(b'1', '(RFC822)')
    assert typ == 'OK'
    assert data == [
        (
            b'1 (RFC822 {30}',
            b'message-id: the-message-id\r\n\r\n',
        ),
        b')',
    ]
