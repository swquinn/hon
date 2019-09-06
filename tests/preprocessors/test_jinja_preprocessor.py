import pytest

import hon.preprocessors.jinja
from hon.preprocessors.jinja import ChapterLoader


@pytest.fixture
def mock_isfile(mocker):
    _context = hon.preprocessors.jinja.__name__
    _mock = mocker.patch(f'{_context}.os.path.isfile')
    return _mock


@pytest.mark.parametrize('path, is_file, expected', [
    ('/path/to/chapters/my_chapter.md', True, ['/path/to/chapters']),
    ('/path/to/chapters', False, ['/path/to/chapters']),
])
def test_instantiate_chapter_loader_with_single_path(path, is_file, expected, mock_isfile):
    mock_isfile.return_value = is_file

    loader = ChapterLoader(path)
    actual = loader.paths
    assert actual == expected


@pytest.mark.parametrize('paths', [
    ['/path/to/chapters', '/other/path'],
])
def test_instantiate_chapter_loader_with_multiple_paths(paths):
    loader = ChapterLoader(paths)
    actual = loader.paths
    assert actual == paths


