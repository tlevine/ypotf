import re

MATCHERS = {k: re.compile(v, flags=re.IGNORECASE) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('confirmations', r'list-confirm-[a-z0-9]{32}'),
#   ('archive', r'^list-archive'),
    ('help', r'^help$'),
]}
