import pytest
import xml.etree.ElementTree as ElementTree
from hon.utils.mdutils import flatten_tree


@pytest.fixture
def document():
    source = '''<div>
<h1>Hello World!</h1>
<p>
This is a test. <a href="">This is a link</a>. This is <em>emphasized</em>.
</p>
<ol>
<li>First List Item</li>
<li>Second List Item</li>
</ol></div>'''
    return ElementTree.fromstring(source)


def test_flatten_tree(document):
    actual = flatten_tree(document)

    actual_tags = tuple([e.tag for e in actual])
    expected_tags = ('h1', 'p', 'a', 'em', 'ol', 'li', 'li')

    assert len(actual) == len(expected_tags)
    assert actual_tags == expected_tags
