import re

def date(m):
    return m['Date']

def subject(m):
    subject = m['subject']
    for cat, expr in MATCHERS:
        if re.search(expr, subject):
            return cat
    return 'message'

def email_address(m):
    return m['from']

def confirmation_code(m):
    m = re.match(MATCHERS['confirm'], m['subject'])
    return m.group(1)
