import foo_module
import bar_module


def test_foo():
    assert foo_module.foo() == "foo"


def test_bar():
    assert bar_module.bar() == "bar"
