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
    s = "Some random text with {{foo}} and {{bar }} {{ baz }}..."

    actual = find_variables(s)
    # print("OUTPUT: {}".format(actual))

    assert actual == [
        Variable(
            start_index=22,
            end_index=29,
            name='foo',
            token_text='{{foo}}'
        ),
        Variable(
            start_index=34,
            end_index=42,
            name='bar',
            token_text='{{bar }}'
        ),
        Variable(
            start_index=43,
            end_index=52,
            name='baz',
            token_text='{{ baz }}'
        ),
    ]


def test_find_variables_with_namespace():
    s = "Some random text with {{ my.ns.foo }}..."
    actual = find_variables(s)

    #print("OUTPUT: {}".format(actual))
    assert actual == [
        Variable(
            start_index=22,
            end_index=37,
            name='my.ns.foo',
            token_text="{{ my.ns.foo }}",
        )
    ]


def test_find_variables_escaped_variable():
    s = "Some random text with escaped variable \\{{ foo }} ..."
    print(s)
    actual = find_variables(s)
    print("OUTPUT: {}".format(actual))

    assert actual == []
