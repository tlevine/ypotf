def r(x, expected='OK'):
    typ, data = x
    assert typ == expected, typ
    return data
