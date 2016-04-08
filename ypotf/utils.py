def r(x, expected='OK'):
    typ, data = x
    assert typ == expected, typ
    return data

def email_address(x):
    if '\\' in x or '"' in x:
        raise ValueError('Invalid email address: %s' % x)
    return x
