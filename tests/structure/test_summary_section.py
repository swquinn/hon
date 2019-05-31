import pytest
from hon.structure.summary import Section, Part


def test_instantiate():
    actual = Section()
    assert actual.title is None
    assert actual.parts == []

    actual = Section(title='Table of Contents')
    assert actual.title == 'Table of Contents'
    assert actual.parts == []

    actual = Section(title='Table of Contents', parts=[Part('Foo')])
    assert actual.title == 'Table of Contents'
    assert len(actual.parts) == 1


def test_add_part():
    section = Section()
    part = Part('Foo')

    assert len(section.parts) == 0

    section.add_part(part)

    assert len(section.parts) == 1
    assert section.parts[0] == part


def test_add_parts():
    section = Section()
    parts = [Part('Foo'), Part('Bar')]

    assert len(section.parts) == 0

    section.add_parts(parts)

    assert len(section.parts) == 2
    assert section.parts == parts
