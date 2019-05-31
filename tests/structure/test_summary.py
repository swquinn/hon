import pytest
from hon.structure.summary import Summary, Section


def test_instantiate():
    actual = Summary()
    assert actual.title is None
    assert actual.sections == []

    actual = Summary(title='Table of Contents')
    assert actual.title == 'Table of Contents'
    assert actual.sections == []

    actual = Summary(title='Table of Contents', sections=[Section()])
    assert actual.title == 'Table of Contents'
    assert len(actual.sections) == 1


def test_add_section():
    summary = Summary()
    section = Section()

    assert len(summary.sections) == 0

    summary.add_section(section)

    assert len(summary.sections) == 1
    assert summary.sections[0] == section


def test_add_sections():
    summary = Summary()
    sections = [Section(), Section()]

    assert len(summary.sections) == 0

    summary.add_sections(sections)

    assert len(summary.sections) == 2
    assert summary.sections == sections
