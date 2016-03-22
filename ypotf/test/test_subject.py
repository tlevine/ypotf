from .. import subject

testcases_categorize = [
    ('subscribe', 'subscribe'),
    ('unsubscribe', 'unsubscribe'),
    ('help', 'help'),
    ('sUBscribe', 'subscribe'),
    ('uNSubscribe', 'unsubscribe'),
    ('hELp', 'help'),
    ('help waaaa', 'message'),
    ('unsubscribe me', 'message'),
    ('subscribe la la la', 'message'),
    ('Re: Fwd: list-confirm-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx','confirm'),
    ('Re: Fwd: list-confirm-notexactly32chars','message'),
    ('list-archive 20150703..20151001', 'archive'),
    ('list-archive', 'archive'),
    ('Re: list-archive 20150703..20151001', 'message'),
    ('Re: list-archive', 'message'),
]
@pytest.mark.parametrize('line, category', testcases_categorize)
def test_categorize(line, category):
    assert subject.categorize(line) == category
