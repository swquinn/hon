import pytest
from hon.structure.title import Title


def test_title__repr__():
    t = Title(text="Foo")

    actual = repr(t)
    assert actual == "Title(text='Foo')"


def test_title__str__():
    t = Title(text="Foo")

    actual = str(t)
    assert actual == "Foo"
