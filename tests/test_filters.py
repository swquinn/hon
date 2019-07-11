import pytest
from hon.book import Book
from hon.filters import relative_path


@pytest.fixture
def philosophy_book():
    book = Book(
        name='Groundwork of the Metaphysic of Morals',
        author='Immanual Kant',
        path='/hon/src'
    )
    return book


@pytest.mark.parametrize('page_path, expected', [
    ('/hon/book/output/page.html', 'path/to/other_page.html'),
    ('/hon/book/output/path/for/page.html', '../to/other_page.html'),
    ('/hon/book/output/path/to/another/page.html', '../other_page.html')
])
def test_relative_path(philosophy_book, page_path, expected):
    context = {
        '_book': philosophy_book,
        '_root': '/hon/book/output',
        'page': {
            'path': page_path
        }
    }
    actual = relative_path(context, './path/to/other_page.html')
    assert actual == expected
    