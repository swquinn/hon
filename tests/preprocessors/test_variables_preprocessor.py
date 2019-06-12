import pytest
from hon.preprocessors.variables import (
    find_variables,
    Variable, VariablesPreprocessor
)


def test_find_variables_no_variable():
    s = "Some random text without variable..."

    actual = find_variables(s) 
    assert actual == []


def test_find_variables_partial_variable():
    s = "Some random text with {{ foo..."
    actual = find_variables(s)
    assert actual == []

    s = "Some random text with {{ foo.bar..."
    actual = find_variables(s)
    assert actual == []

    s = "Some random text with \\{{ foo.bar.baz..."
    actual = find_variables(s)
    assert actual == []


def test_find_variables_empty_variable():
    s = "Some random text with {{}} ..."
    actual = find_variables(s)
    assert actual == []


def test_find_variables_simple_variable():
    s = "Some random text with {{book.foo}} and {{book.bar }} {{ book.baz }}..."

    actual = find_variables(s)
    # print("OUTPUT: {}".format(actual))

    assert actual == [
        Variable(
            start_index=22,
            end_index=34,
            name='foo',
            token_text='{{book.foo}}'
        ),
        Variable(
            start_index=39,
            end_index=52,
            name='bar',
            token_text='{{book.bar }}'
        ),
        Variable(
            start_index=53,
            end_index=67,
            name='baz',
            token_text='{{ book.baz }}'
        ),
    ]


def test_find_variables_with_namespace():
    s = "Some random text with {{ book.my.ns.foo }}..."
    actual = find_variables(s)

    #print("OUTPUT: {}".format(actual))
    assert actual == [
        Variable(
            start_index=22,
            end_index=42,
            name='my.ns.foo',
            token_text="{{ book.my.ns.foo }}",
        )
    ]


def test_find_variables_escaped_variable():
    s = "Some random text with escaped variable \\{{ foo }} ..."
    print(s)
    actual = find_variables(s)
    print("OUTPUT: {}".format(actual))

    assert actual == []
