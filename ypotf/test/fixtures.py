import imaplib
import datetime
import subprocess, os
import functools
from email.message import Message

import pytest

TEST_MAILBOXES = ['INBOX', 'chainsaw']

def _now():
    return tuple(datetime.datetime.now().timetuple())

def _password():
    fn = os.path.expanduser('~/.test-ypotf-password')
    cmd = ['pass', 'show', 'test-ypotf@dada.pink']
    if os.path.isfile(fn):
        with open(fn) as fp:
            x = fp.read().strip()
    else:
        sp = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        sp.wait()
        x = sp.stdout.read().decode('utf-8')
        with open(fn, 'w') as fp:
            fp.write(x)
    return x

def _finalize(M):
    for mailbox in TEST_MAILBOXES:
        typ, data = M.select(mailbox)
        if typ == 'NO':
            continue
        typ, data = M.search(None, 'ALL')
        for num in data[0].split():
           M.store(num, '+FLAGS', '\\Deleted')
        M.expunge()
        M.close()
    M.logout()

@pytest.fixture
def bare_imap(request):
    host = 'mail.gandi.net'
    address = 'test-ypotf@dada.pink'
    password = _password()

    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)

    request.addfinalizer(functools.partial(_finalize, M))
    return M

@pytest.fixture
def populated_imap(request):
    host = 'mail.gandi.net'
    address = 'test-ypotf@dada.pink'
    password = _password()

    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)

    m1 = Message()
    m1['Subject'] = 'key1'
    m1.set_payload('value1')
    M.append('INBOX', None, _now(), m1.as_bytes())

    m2 = Message()
    m2['Subject'] = 'key2'
    m2.set_payload('value2')
    M.append('INBOX', None, _now(), m2.as_bytes())

    request.addfinalizer(functools.partial(_finalize, M))
    return M
