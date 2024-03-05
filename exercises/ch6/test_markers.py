import pytest


def test_one():
    pass


def test_two():
    pass


def test_three():
    pass


class TestClass:
    def test_four(self):
        pass

    def test_five(self):
        pass


@pytest.mark.parametrize("x", [6, 7])
def test_param(x):
    pass
