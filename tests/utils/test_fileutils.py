import pytest
from hon.utils.fileutils import (
    _match,
    is_current_directory,
    copy_from
)

def test__match():
    pytest.fail()


@pytest.mark.parametrize('path, expected', [
    ('.', True),
    ('foo/', False),
    (None, False)
])
def test_is_current_directory(path, expected):
    actual = is_current_directory(path)
    assert actual == expected


def test_copy_from():
    pytest.fail()