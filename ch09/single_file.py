def foo():
    return "foo"


def bar():
    return "bar"


def baz():
    return "baz"


def main():
    print(foo(), baz())


if __name__ == "__main__":  # pragma: no cover
    main()

# test code, requires pytest


def test_foo():
    assert foo() == "foo"


def test_baz():
    assert baz() == "baz"


def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "foo baz\n"
