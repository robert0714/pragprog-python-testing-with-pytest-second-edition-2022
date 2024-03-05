import hello
import pytest


def test_hello_world():
    assert hello.world() == "Hello, World!"


@pytest.mark.parametrize(
    "actor", ["Graham", "John", "Terry", "Eric", "Michael"]
)
def test_hello_name(actor):
    assert hello.name(actor) == f"Hello, {actor}!"
