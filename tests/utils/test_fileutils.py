import pytest
from hon.utils.fileutils import (
    filename_matches_pattern,
    is_current_directory,
    copy_from
)

@pytest.mark.parametrize('subject, pattern, expected', [
    ('foo', 'foo', True),
    ('foo', ['foo'], True),
    ('foo', 'bar', False),
    ('foo', ['bar'], False),
    ('foo', ['foo', 'bar'], True),
    ('prefixed/foo', 'foo', False),
    ('prefixed/foo', '**/foo', True),
])
def test__match(subject, pattern, expected):
    actual = filename_matches_pattern(subject, pattern)
    assert actual == expected


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