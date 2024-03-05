import lib
import pytest


def test_fast_func():
    assert lib.fast_func() == 2


@pytest.mark.slow
def test_slow_func():
    assert lib.slow_func() == 1
