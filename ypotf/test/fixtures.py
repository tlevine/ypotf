import imaplib
import subprocess, os

import pytest

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

@pytest.fixture
def imap(request):
    host = 'mail.gandi.net'
    address = 'test-ypotf@dada.pink'
    password = _password()

    M = imaplib.IMAP4_SSL(host)
    M.login(address, password)

    def fin():
        M.select('INBOX')
        typ, data = M.search(None, 'ALL')
        for num in data[0].split():
           M.store(num, '+FLAGS', '\\Deleted')
        M.expunge()
        M.logout()
    request.addfinalizer(fin)
    return M
