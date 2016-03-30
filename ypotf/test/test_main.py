from email.message import Message
from .fixtures import bare_imap, _password, _now
from ..main import ypotf

def test_ypotf(bare_imap):
    m = Message()
    m['from'] = 'test-ypotf2@dada.pink'
    m['Subject'] = 'subscribe'
    bare_imap.append('INBOX', None, _now(), m.as_bytes())

    ypotf('mail.gandi.net', 'test-ypotf@dada.pink', _password())

    typ, _ = bare_imap.select('INBOX')
    assert typ == 'OK'
    typ, data = bare_imap.search(None, 'ALL')
    assert typ == 'OK'
    assert data == [b'']
