
def _imap_from_url(url):
    x = urllib.parse.urlparse(url)

    if x.scheme.lower() == 'imap':
        f = imaplib.IMAP4
    else:
        f = imaplib.IMAP4_SSL

    if x.port:
        args = x.hostname, x.port
    else:
        args = x.hostname,

    return f(*args)

