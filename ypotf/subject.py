import re

MATCHERS = [(k, re.compile(v, flags=re.IGNORECASE)) for (k,v) in [
    ('subscribe', r'^subscribe$'),
    ('unsubscribe', r'^unsubscribe$'),
    ('confirm', r'list-confirm-[a-z0-9]{32}'),
    ('archive', r'^list-archive'),
    ('help', r'help$'),
]]

def categorize(subject):
    for cat, expr in MATCHERS:
        if re.match(expr, subject):
            return cat
    return 'message'
