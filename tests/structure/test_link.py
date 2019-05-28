import pytest
from hon.structure.link import Link


@pytest.fixture
def link():
    return Link(name='First', source='./first.md', level=0)


@pytest.fixture
def link_with_children(link):
    children = [
        Link(name='Second', source='./first/second.md', level=1),
        Link(name='Third', source='./first/third.md', level=1),
        Link(name='Fourth', source='./first/fourth.md', level=1),

    ]
    link.children = children
    return link


def test_instance(link):
    assert link.id == 'first'
    assert link.name == 'First'
    assert link.source == './first.md'


def test_to_json(link):
    actual = link.to_json()

    expected = {
        'id': 'first',
        'name': 'First',
        'source': './first.md',
        'level': 0,
        'children': []
    }
    assert actual == expected


def test_to_json_complex(link_with_children):
    actual = link_with_children.to_json()

    expected = {
        'id': 'first',
        'name': 'First',
        'source': './first.md',
        'level': 0,
        'children': [
            {
                'id': 'first-second',
                'name': 'Second',
                'source': './first/second.md',
                'level': 1,
                'children': []
            },
            {
                'id': 'first-third',
                'name': 'Third',
                'source': './first/third.md',
                'level': 1,
                'children': []
            },
            {
                'id': 'first-fourth',
                'name': 'Fourth',
                'source': './first/fourth.md',
                'level': 1,
                'children': []
            },
        ]
    }
    assert actual == expected
