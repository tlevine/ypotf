import datetime
from email.message import Message

from .fixtures import imap
from .. import storage

def _now():
    return tuple(datetime.datetime.now().timetuple())

def test_blah(imap):
    imap.select('INBOX')

    m1 = Message()
    m1['Subject'] = 'unsubscribe'
    imap.append('INBOX', None, _now(), m1.as_bytes())

    m2 = Message()
    m2['Subject'] = 'subscribe'
    imap.append('INBOX', None, _now(), m2.as_bytes())

    imap.close()

    imap.select('INBOX')
    assert storage.message_nums(imap) == [b'1', b'2']

    num, m = storage.first_message(imap)
    assert num == b'1'
    assert m.as_string() == m1.as_string()
