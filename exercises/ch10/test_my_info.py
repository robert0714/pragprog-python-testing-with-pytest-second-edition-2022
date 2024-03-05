from unittest import mock
import my_info


def test_my_home_returns_correct_value():
    value = my_info.home_dir()
    assert value == "/users/fake_user"


def test_my_home_is_called():
    my_info.home_dir()
    # check to see if Path.home() was called
