import pytest
from hon.structure import Chapter, ChapterNode, ChapterGraph


@pytest.fixture
def chapters():
    chapters = [
        Chapter(name='Chapter 1'),
        Chapter(name='Chapter 2', children=[
            Chapter(name='Chapter 2-A'),
            Chapter(name='Chapter 2-B'),
            Chapter(name='Chapter 2-C'),
        ]),
        Chapter(name='Chapter 3', children=[
            Chapter(name='Chapter 3-A', children=[
                Chapter(name='Chapter 3-A-I')
            ]),
            Chapter(name='Chapter 3-B'),
        ]),
    ]
    return chapters


def test_instantiate():
    graph = ChapterGraph()

    assert graph.first == None
    assert graph.last == None


def test_append_chapter():
    graph = ChapterGraph()
    
    chapter = Chapter(name='foo')
    graph.append(chapter)

    assert graph.first.chapter == chapter 
    assert graph.last.chapter == chapter


def test_append_chapter_with_children():
    graph = ChapterGraph()
    
    chapter = Chapter(name='foo', children=[
        Chapter(name='bar'),
        Chapter(name='baz')
    ])
    graph.append(chapter)

    assert graph.first.chapter == chapter
    assert graph.last.chapter == chapter.children[1]


def test_extend(chapters):
    graph = ChapterGraph()
    graph.extend(chapters)

    assert graph.first.chapter == chapters[0]
    assert graph.last.chapter == chapters[2].children[1]


def test_get(chapters):
    graph = ChapterGraph(chapters)

    actual = graph.get(chapters[1].children[1])
    assert actual is not None
    assert actual.chapter.name == 'Chapter 2-B'


def test_get_returns_none_for_unknown_chapter(chapters):
    graph = ChapterGraph(chapters)

    actual = graph.get(Chapter(name='Foobarbaz'))
    assert actual is None
