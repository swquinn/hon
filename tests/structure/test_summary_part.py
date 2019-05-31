import pytest
from hon.structure.summary import Part


@pytest.fixture
def part():
    return Part('First', source='./first.md', level=0)


@pytest.fixture
def part_with_children(part):
    children = [
        Part('Second', source='./first/second.md', level=1),
        Part('Third', source='./first/third.md', level=1),
        Part('Fourth', source='./first/fourth.md', level=1),

    ]
    part.children = children
    return part


def test_instance(part):
    assert part.id == 'first'
    assert part.name == 'First'
    assert part.source == './first.md'
