import pytest

from hon.book import Book


@pytest.fixture
def philosophy_book():
    book = Book(
        name='Groundwork of the Metaphysic of Morals',
        author=[
            'Immanual Kant'
        ]
    )
    return book
