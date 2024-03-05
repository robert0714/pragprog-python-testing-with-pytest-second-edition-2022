import lib


def test_fast_func():
    assert lib.fast_func() == 1


def test_slow_func():
    assert lib.slow_func() == 2
