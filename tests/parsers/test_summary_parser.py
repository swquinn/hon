import pytest
from hon.markdown import Markdown
from hon.parsers.summary_parser import (
    SectionNumber, SummaryParser, SummaryItemSeparator, stringify_events
)
from hon.structure import Link
from hon.utils.mdutils import flatten_tree
from xml.etree.ElementTree import ElementTree


@pytest.mark.parametrize("inputs, expected", [
    ([0], "0."),
    ([1, 3], "1.3."),
    ([1, 2, 3], "1.2.3.")
])
def test_section_number_has_correct_dotted_representation(inputs, expected):
    actual = str(SectionNumber(inputs))
    assert actual == expected


@pytest.mark.parametrize("source, expected", [
    ("# Summary", "Summary"),
    ("# My **Awesome** Summary", "My Awesome Summary")
])
def test_parse_initial_title(app, source, expected):
    parser = SummaryParser(app, source)
    actual = parser.parse_title() #.unwrap()

    assert actual == expected


@pytest.mark.parametrize("source, expected", [
    ('Hello *World*, `this` is some text [and a link](./path/to/link)',
     'Hello World, this is some text and a link')
])
def test_stringify_events(source, expected):
    md = Markdown()
    md.convert(source)

    actual = stringify_events(md.parse_tree)
    assert actual == expected


def test_parse_prefix_items_with_a_separator(app):
    src = """
[First](./first.md)

---

[Second](./second.md)

- Item 1
- Item 2

[Third](./third.md)

[Fourth](./fourth.md)

---

[Fifth](./fifth.md)"""
    parser = SummaryParser(app, src)

    #let _ = parser.stream.next(); // step past first event
    actual = parser.parse_affix(is_prefix=True)
    expected = [
        Link(name="First", location="./first.md"),
        SummaryItemSeparator(),
        Link(name="Second", location="./second.md"),
    ]

    assert len(actual) == len(expected)
    assert actual == expected


def test_parse_suffix_items_with_a_separator(app):
    src = """
[First](./first.md)

---

[Second](./second.md)

- Item 1
- Item 2

[Third](./third.md)

[Fourth](./fourth.md)

---

[Fifth](./fifth.md)"""
    parser = SummaryParser(app, src)

    #let _ = parser.stream.next(); // step past first event
    actual = parser.parse_affix(is_prefix=False)
    expected = [
        Link(name="Third", location="./third.md"),
        Link(name="Fourth", location="./fourth.md"),
        SummaryItemSeparator(),
        Link(name="Fifth", location="./fifth.md"),
    ]

    assert len(actual) == len(expected)
    assert actual == expected


def test_suffix_items_cannot_be_followed_by_a_list(app):
    src = """
[First](./first.md)

- [Second](./second.md)"""
    parser = SummaryParser(app, src)

    with pytest.raises(ValueError):
        parser.parse_affix(is_prefix=False)



@pytest.mark.parametrize("source, expected", [
    ('[First](./first.md)', Link(name='First', location='./first.md'))
])
def test_parse_a_link(app, source, expected):
    parser = SummaryParser(app, source)
    link = parser.stream.elements.find('.//a')

    actual = parser.parse_link(link)
    assert actual == expected


def test_parse_a_numbered_chapter(app):
    src = "- [First](./first.md)\n"
    link = Link(
        name="First",
        location="./first.md",
        level=0
    )
    expected = [link]

    parser = SummaryParser(app, src)
    actual = parser.parse_numbered()
    assert actual == expected


def test_parse_some_prefix_items(app):
    src = "[First](./first.md)\n[Second](./second.md)\n"
    parser = SummaryParser(app, src)

    expected = [
        Link(
            name="First",
            location="./first.md"
        ),
        Link(
            name="Second",
            location="./second.md"
        ),
    ]

    actual = parser.parse_affix(is_prefix=True)
    assert actual == expected



def test_parse_nested_numbered_chapters(app):
    src = "- [First](./first.md)\n    - [Nested](./nested.md)\n- [Second](./second.md)"

    expected = [
        Link(
            name="First",
            location="./first.md",
            level=0,
            children=[
                Link(
                    name="Nested",
                    location="./nested.md",
                    level=1,
                    children=[],
                ),
            ]
        ),
        Link(
            name="Second",
            location="./second.md",
            level=0,
            children=[]
        ),
    ]

    parser = SummaryParser(app, src)
    actual = parser.parse_numbered()
    assert actual == expected


def test_can_have_a_subheader_between_nested_items(app):
    """
    This test ensures the book will continue to pass because it breaks the
    `SUMMARY.md` up using level 2 headers ([example]).

    [example]: https://github.com/rust-lang/book/blob/2c942dc094f4ddcdc7aba7564f80782801197c99/second-edition/src/SUMMARY.md#basic-rust-literacy
    """
    src = "- [First](./first.md)\n\n## Subheading\n\n- [Second](./second.md)\n";
    expected = [
        Link(
            name="First",
            location="./first.md",
            level=0,
            children=[]
        ),
        Link(
            name="Second",
            location="./second.md",
            level=0,
            children=[]
        ),
    ]

    parser = SummaryParser(app, src)
    actual = parser.parse_numbered()
    assert actual == expected


#[test]
def test_an_empty_link_location_is_an_error(app):
    src = "- [Empty]()\n";
    parser = SummaryParser(app, src)

    link = parser.stream.elements.find('.//a')
    with pytest.raises(ValueError):
        parser.parse_link(link)


def test_keep_numbering_after_separator(app):
    """
    /// Regression test for https://github.com/rust-lang-nursery/mdBook/issues/779
    /// Ensure section numbers are correctly incremented after a horizontal separator.
    """
    src = "- [First](./first.md)\n\n---\n\n- [Second](./second.md)\n\n---\n\n- [Third](./third.md)\n"
    expected = [
        Link(
            name="First",
            location="./first.md",
            level=0,
            children=[]
        ),
        SummaryItemSeparator(),
        Link(
            name="Second",
            location="./second.md",
            level=0,
            children=[]
        ),
        SummaryItemSeparator(),
        Link(
            name="Third",
            location="./third.md",
            level=0,
            children=[]
        ),
    ]

    parser = SummaryParser(app, src)
    actual = parser.parse_numbered()
    assert actual == expected

#: TODO: Add tests for empty summaries? Is this supported? Doesn't the book just end put as empty? Should we err with this instead?