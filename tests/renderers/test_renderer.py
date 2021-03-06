import pytest

from hon.book import Book
from hon.renderers import Renderer
from hon.structure import Chapter, Separator


@pytest.fixture
def chapter_content():
    return """static str = "
# Dummy Chapter

this is some dummy text.

And here is some \
                                     more text.
"""


@pytest.fixture
def philosophy_book():
    book = Book(
        name='Groundwork of the Metaphysic of Morals',
        author='Immanual Kant'
    )
    return book


@pytest.fixture
def sample_chapter(chapter_content):
    chapter = Chapter(name='Chapter 1', raw_text=chapter_content)
    return chapter


@pytest.fixture
def sample_chapter_with_nested_items(chapter_content):
    nested_items = [
        Chapter(name='Hello, World!'),
        Chapter(name='Goodbye, Cruel World!')
    ]
    chapter = Chapter(
        name='Chapter 1',
        raw_text=chapter_content,
        path='Chapter_1/index.md',
        children=nested_items,
        parent=None
    )
    return chapter


def test_add_chapter(app, sample_chapter):
    renderer = Renderer(app)
    renderer.add_chapter(sample_chapter)
    renderer.build_chapter_graph()

    assert len(renderer.chapters) == 1
    assert renderer.chapters[0] == sample_chapter
    assert renderer.chapters[0].previous is None
    assert renderer.chapters[0].next is None

    new_chapter = Chapter(name='Chapter 2')
    renderer.add_chapter(new_chapter)
    renderer.build_chapter_graph()

    assert len(renderer.chapters) == 2
    assert renderer.chapters[1] == new_chapter
    assert renderer.chapters[0].previous is None
    assert renderer.chapters[0].next == new_chapter
    assert renderer.chapters[1].previous == sample_chapter
    assert renderer.chapters[1].next is None

    last_chapter = Chapter(name='Chapter 3')
    renderer.add_chapter(last_chapter)
    renderer.build_chapter_graph()

    assert len(renderer.chapters) == 3
    assert renderer.chapters[2] == last_chapter
    assert renderer.chapters[0].previous is None
    assert renderer.chapters[0].next == new_chapter
    assert renderer.chapters[1].previous == sample_chapter
    assert renderer.chapters[1].next == last_chapter
    assert renderer.chapters[2].previous == new_chapter
    assert renderer.chapters[2].next is None


def test_add_chapters(app, sample_chapter):
    renderer = Renderer(app)

    chapters = [sample_chapter, Chapter(name='Chapter 2'), Chapter(name='Chapter 3')]
    renderer.add_chapters(chapters)
    renderer.build_chapter_graph()

    assert len(renderer.chapters) == 3
    assert renderer.chapters[0].previous is None
    assert renderer.chapters[0].next == chapters[1]
    assert renderer.chapters[1].previous == chapters[0]
    assert renderer.chapters[1].next == chapters[2]
    assert renderer.chapters[2].previous == chapters[1]
    assert renderer.chapters[2].next is None


def test_items_property(app, sample_chapter):
    renderer = Renderer(app)
    renderer.add_chapters([sample_chapter, Chapter()])
    renderer.build_chapter_graph()

    expected = tuple(renderer.chapters)
    actual = renderer.items
    assert actual == expected


def test_items_property_against_chapters_with_children(app, sample_chapter_with_nested_items):
    """When chapters have nested items, assert that the items property returns
    """
    renderer = Renderer(app)
    renderer.add_chapters([
        sample_chapter_with_nested_items,
        Chapter(name='Chapter 2')
    ])
    renderer.build_chapter_graph()

    actual = renderer.items
    assert len(actual) == 4

    chapter_names = [item.name for item in actual if type(item) == Chapter]
    assert chapter_names == ['Chapter 1', 'Hello, World!', 'Goodbye, Cruel World!', 'Chapter 2']
