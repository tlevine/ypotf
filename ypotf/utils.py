import uuid
import email

def r(x, expected='OK'):
    typ, data = x
    assert typ == expected, typ
    return data

def uuid():
    return uuid.uuid1().hex

def email_address(x):
    return email.utils.parse_addr(x)[1].lower()
