from email.message import Message
from .fixtures import bare_imap, _password, _now
from ..utils import r
from ..main import ypotf

def test_ypotf(bare_imap):
    m = Message()
    m['from'] = 'test-ypotf2@dada.pink'
    m['Subject'] = 'subscribe'


    r(bare_imap.create('INBOX'))
    r(bare_imap.append('INBOX', None, _now(), m.as_bytes()))

    ypotf('mail.gandi.net', 'test-ypotf@dada.pink', _password())

    r(bare_imap.select('INBOX'))
    assert r(bare_imap.search(None, 'ALL')) == [b'']
    r(bare_imap.create('ypotf-confirm'))
    r(bare_imap.select('ypotf-confirm'))
    assert r(bare_imap.search(None, 'ALL')) == [b'1']
    assert r(bare_imap.fetch(b'1', '(RFC322)')) == False

    r(bare_imap.select('ypotf-confirm'))
