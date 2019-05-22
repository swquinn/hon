import pytest
from hon.utils import numberutils


def test_to_int_ns():
    assert numberutils.to_int_ns(None) is None
    assert numberutils.to_int_ns(1) == 1
    assert numberutils.to_int_ns('2') == 2
    assert numberutils.to_int_ns('3.5') == 3
    assert numberutils.to_int_ns(10.8) == 10


def test_to_int_ns_fails_for_invalid_literals():
    with pytest.raises(ValueError):
        numberutils.to_int_ns('')
