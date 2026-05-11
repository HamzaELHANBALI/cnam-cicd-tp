import pytest

from tp_app.calculator import add, divide, multiply, subtract


def test_add():
    assert False
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(10, 4) == 6


def test_multiply():
    assert multiply(6, 7) == 42


def test_divide():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)


def test_add_wrong():
    assert add(2, 3) == 5


def test_multiply_wrong():
    assert multiply(3, 4) == 12
