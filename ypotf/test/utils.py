def r(x):
    typ, data = x
    assert typ == 'OK', typ
    return data
