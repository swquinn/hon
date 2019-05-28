import pytest
from hon.structure.link import Link


@pytest.fixture
def link():
    return Link(name='First', source='./first.md', level=0)


def test_instance(link):
    assert link.id == 'first'
    assert link.name == 'First'
    assert link.source == './first.md'

