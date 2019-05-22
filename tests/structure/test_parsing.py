import os
import pytest

from hon.book import Book
from hon.structure.parsing import (
    find_parsable_file, lookup_structure_file, parse_structure_file
)


@pytest.fixture
def book_en(app, assets_path):
    book = Book(app=app, path=os.path.join(assets_path, 'multi-book/src/en'))
    return book


@pytest.fixture
def mock_find_parsable_file(mocker):
    return mocker.patch('{}.{}'.format(
        find_parsable_file.__module__,
        find_parsable_file.__name__))


@pytest.mark.parametrize('structure_filename, should_exist', [
    ('GLOSSARY.md', True),
    ('README.md', True),
    ('SUMMARY.md', True),
    ('FOO.md', False)
])
def test_find_parsable_file(book_en, structure_filename, should_exist):
    actual = find_parsable_file(book_en, structure_filename)

    if should_exist:
        assert actual is not None
        assert os.path.basename(actual) == structure_filename
    else:
        assert actual is None


@pytest.mark.parametrize('structure_type, expected_filename', [
    ('glossary', 'GLOSSARY.md'),
    ('readme', 'README.md'),
    ('summary', 'SUMMARY.md'),
    ('foo', None)
])
def test_lookup_structure_file(book_en, structure_type, expected_filename, mock_find_parsable_file):
    lookup_structure_file(book_en, structure_type)
    mock_find_parsable_file.assert_called_once_with(book_en, expected_filename)
