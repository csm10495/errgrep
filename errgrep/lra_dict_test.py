from .lra_dict import LeastRecentlyAddedDict

def test_lra_dict():
    d = LeastRecentlyAddedDict(2)
    d['a'] = 1
    d['b'] = 2

    assert d['a'] == 1
    assert d['b'] == 2

    d['c'] = 3

    assert d['b'] == 2
    assert d['c'] == 3

    assert 'a' not in d