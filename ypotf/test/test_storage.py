import datetime
from email.message import Message

from .fixtures import imap
from .. import storage

def _now():
    return tuple(datetime.datetime.now().timetuple())

def test_blah(imap):
    m = Message()
    imap.select('INBOX')

    m['Subject'] = 'unsubscribe'
    imap.append('INBOX', None, _now(), m.as_bytes())

    m['Subject'] = 'subscribe'
    imap.append('INBOX', None, _now(), m.as_bytes())

    imap.close()

    imap.select('INBOX')
    assert storage.message_nums(imap) == [b'1', b'2']
