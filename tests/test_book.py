import pytest

from hon.book import Book
from hon.structure import Chapter, Separator


@pytest.fixture
def philosophy_book():
    book = Book(
        name='Groundwork of the Metaphysic of Morals',
        author=[
            'Immanual Kant'
        ]
    )
    return book
