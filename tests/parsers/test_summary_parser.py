import pytest
from hon.parsing import MarkdownParser
from hon.parsers.summary_parser import (
    SectionNumber, SummaryParser, stringify_events
)
from hon.structure import Part, Section
from hon.utils.mdutils import flatten_tree
from xml.etree.ElementTree import ElementTree


@pytest.mark.parametrize("source, expected", [
    ('[First](./first.md)', Part(name='First', source='./first.md')),
])
def test_create_part(app, source, expected):
    parser = SummaryParser(app, source)
    element = parser.stream.parse_tree.find('.//a')

    actual = parser.create_part(element)
    assert actual == expected


def test_create_part_raises_value_error_when_link_is_empty(app):
    src = "[Empty]()\n";
    parser = SummaryParser(app, src)

    element = parser.stream.parse_tree.find('.//a')
    with pytest.raises(ValueError):
        parser.create_part(element)


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
    actual = parser.parse_title()

    assert actual == expected


@pytest.mark.parametrize("source, expected", [
    ('Hello *World*, `this` is some text [and a link](./path/to/link)',
     'Hello World, this is some text and a link')
])
def test_stringify_events(source, expected):
    parser = MarkdownParser()
    parser.parse(source)

    actual = stringify_events(parser.parse_tree)
    assert actual == expected


def test_parse_sections_with_no_sections(app):
    parser = SummaryParser(app, '')
    actual = parser.parse_sections()
    assert actual == []


def test_parse_sections_with_one_section_and_no_heading(app):
    source = """
- [1A](./1A.md)
- [1B](./1B.md)
- [1C](./1C.md)
"""
    parser = SummaryParser(app, source)
    actual = parser.parse_sections()

    expected = [
        Section(parts=[
            Part('1A', source='./1A.md', level=0),
            Part('1B', source='./1B.md', level=0),
            Part('1C', source='./1C.md', level=0),
        ])
    ]
    assert actual == expected


def test_parse_sections_with_one_section_and_heading(app):
    source = """
## Section 1

- [1A](./1A.md)
- [1B](./1B.md)
- [1C](./1C.md)
"""
    parser = SummaryParser(app, source)
    actual = parser.parse_sections()

    expected = [
        Section(title='Section 1', parts=[
            Part('1A', source='./1A.md', level=0),
            Part('1B', source='./1B.md', level=0),
            Part('1C', source='./1C.md', level=0),
        ])
    ]
    assert actual == expected


def test_parse_section_with_one_section_excluding_non_links(app):
    src = """
- [First](./first.md)
- [Second](./second.md)
- Item 1
- Item 2
- [Third](./third.md)"""
    parser = SummaryParser(app, src)
    actual = parser.parse_sections()

    expected = [
        Section(parts=[
            Part('First', source='./first.md', level=0),
            Part('Second', source='./second.md', level=0),
            Part('Third', source='./third.md', level=0),
        ])
    ]
    assert actual == expected


def test_parse_sections_with_one_section_and_heading_without_title(app):
    source = """
---

- [1A](./1A.md)
- [1B](./1B.md)
- [1C](./1C.md)
"""
    parser = SummaryParser(app, source)
    actual = parser.parse_sections()

    expected = [
        Section(parts=[
            Part('1A', source='./1A.md', level=0),
            Part('1B', source='./1B.md', level=0),
            Part('1C', source='./1C.md', level=0),
        ])
    ]
    assert actual == expected


def test_parse_sections_with_multiple_sections(app):
    source = """
## Section 1

- [1A](./1A.md)
- [1B](./1B.md)
- [1C](./1C.md)

---

- [2A](./2A.md)
- [2B](./2B.md)
- [2C](./2C.md)
- [2D](./2D.md)

#### Section 3

- [3A](./3A.md)

"""
    parser = SummaryParser(app, source)
    actual = parser.parse_sections()

    expected = [
        Section(title='Section 1', parts=[
            Part('1A', source='./1A.md', level=0),
            Part('1B', source='./1B.md', level=0),
            Part('1C', source='./1C.md', level=0),
        ]),
        Section(parts=[
            Part('2A', source='./2A.md', level=0),
            Part('2B', source='./2B.md', level=0),
            Part('2C', source='./2C.md', level=0),
            Part('2D', source='./2D.md', level=0),
        ]),
        Section(title='Section 3', parts=[
            Part('3A', source='./3A.md', level=0),
        ]),
    ]
    assert actual == expected


def test_parse_sections_with_multiple_sections_where_first_section_has_no_heading(app):
    source = """
- [1A](./1A.md)
- [1B](./1B.md)
- [1C](./1C.md)

## Section 2

- [2A](./2A.md)

"""
    parser = SummaryParser(app, source)
    actual = parser.parse_sections()

    expected = [
        Section(parts=[
            Part('1A', source='./1A.md', level=0),
            Part('1B', source='./1B.md', level=0),
            Part('1C', source='./1C.md', level=0),
        ]),
        Section(title='Section 2', parts=[
            Part('2A', source='./2A.md', level=0),
        ]),
    ]
    assert actual == expected


def test_parse_prefix_section(app):
    source = """
[1A](./1A.md)
[1B](./1B.md)
[1C](./1C.md)

## Section 2

- [2A](./2A.md)
- [2B](./2B.md)

"""
    parser = SummaryParser(app, source)
    actual = parser.parse_sections()

    expected = [
        Section(parts=[
            Part('1A', source='./1A.md'),
            Part('1B', source='./1B.md'),
            Part('1C', source='./1C.md'),
        ]),
        Section(title='Section 2', parts=[
            Part('2A', source='./2A.md', level=0),
            Part('2B', source='./2B.md', level=0),
        ]),
    ]
    assert actual == expected


def test_parse_suffix_section(app):
    source = """
## Section 1

- [1A](./1A.md)
- [1B](./1B.md)

---

[2A](./2A.md)
[2B](./2B.md)
[2C](./2C.md)
"""
    parser = SummaryParser(app, source)
    actual = parser.parse_sections()

    expected = [
        Section(title='Section 1', parts=[
            Part('1A', source='./1A.md', level=0),
            Part('1B', source='./1B.md', level=0),
        ]),
        Section(parts=[
            Part('2A', source='./2A.md'),
            Part('2B', source='./2B.md'),
            Part('2C', source='./2C.md'),
        ]),
    ]
    assert actual == expected
