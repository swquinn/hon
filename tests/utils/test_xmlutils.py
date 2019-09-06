import pytest
from hon.utils.xmlutils import (
    find_first_element_by_tag,
    find_elements_by_tag
)
import xml.etree.ElementTree as ElementTree


@pytest.fixture
def link_element():
    source = '''<a href="the-past">A Link to</a>'''
    return ElementTree.fromstring(source)


@pytest.fixture
def list_element():
    source = '''
<ul>
  <li><a href="the-past">A Link to</a></li>
</ul>'''
    return ElementTree.fromstring(source)


@pytest.fixture
def list_element_with_multiple_links_in_one_list_item():
    source = '''
<ul>
  <li>
    <a href="the-past">A Link to</a> and <a href="awakening">Link's</a>
  </li>
</ul>'''
    return ElementTree.fromstring(source)


@pytest.fixture
def list_element_with_embedded_list():
    source = '''
<ul>
  <li>
    <ol>
      <li><a href="awakening">Link's</a></li>
    </ol>
    <p><a href="the-past">A Link to</a></p>
  </li>
  <li>This is some text</li>
  <li>
    <p>Another unordered list</p>
    <ul>
      <li><a href="notfound">Missing Link</a></li>
    </ul>
  </li>
</ul>'''
    return ElementTree.fromstring(source)


def test_find_first_element_by_tag_when_element_does_not_match_tag(link_element):
    actual = find_first_element_by_tag(link_element, 'p')
    assert actual is None


def test_find_first_element_by_tag_when_element_is_not_a_descendant(list_element):
    actual = find_first_element_by_tag(list_element, 'p')
    assert actual is None


def test_find_first_element_by_tag_when_element_is_the_tag_being_searched_for(link_element):
    actual = find_first_element_by_tag(link_element, 'a')
    assert actual == link_element


def test_find_first_element_by_tag_when_element_is_direct_child_of_element(list_element):
    list_item_element = list(list_element)[0]
    link_element = list(list_item_element)[0]

    actual = find_first_element_by_tag(list_item_element, 'a')
    assert actual is not None
    assert actual == link_element


def test_find_first_element_by_tag_when_element_is_descendant_of_element(list_element):
    list_item_element = list(list_element)[0]
    link_element = list(list_item_element)[0]

    actual = find_first_element_by_tag(list_element, 'a')

    assert actual is not None
    assert actual == link_element


def test_find_first_element_by_tag_when_element_is_descendant_of_element_and_multiple_matching_tags_exists(list_element_with_multiple_links_in_one_list_item):
    list_item_element = list(list_element_with_multiple_links_in_one_list_item)[0]
    link_element = list(list_item_element)[0]

    actual = find_first_element_by_tag(list_element_with_multiple_links_in_one_list_item, 'a')

    assert actual is not None
    assert actual == link_element


def test_find_first_element_by_tag_while_ignoring_some_element_traversals(list_element_with_embedded_list):
    list_item_element = list(list_element_with_embedded_list)[0]
    p_element = list(list_item_element)[1]
    link_element = list(p_element)[0]

    actual = find_first_element_by_tag(list_element_with_embedded_list, 'a', skip=['ol'])
    assert actual is not None
    assert actual == link_element


def test_find_elements_by_tag_should_match_any_element_when_tag_names_is_none(
        list_element_with_embedded_list):
    element = list_element_with_embedded_list

    actual = find_elements_by_tag(element, tag_names=None)
    assert len(actual) == 1
    assert actual == [element]


def test_find_elements_by_tag_should_match_any_element_when_tag_names_is_wildcard(
        list_element_with_embedded_list):
    element = list_element_with_embedded_list

    actual = find_elements_by_tag(element, tag_names='*')
    assert len(actual) == 1
    assert actual == [element]


def test_find_elements_by_tag_should_only_return_first_element_when_max_depth_is_0(
        list_element_with_embedded_list):
    element = list_element_with_embedded_list

    actual = find_elements_by_tag(element, tag_names=['ul'], max_depth=0)
    assert len(actual) == 1
    assert actual == [element]


def test_find_elements_by_tag_should_only_return_matching_elements_until_max_depth_is_reached(
        list_element_with_embedded_list):
    element = list_element_with_embedded_list

    actual = find_elements_by_tag(element, tag_names=['li'], max_depth=1)
    expected = [element[0], element[1], element[2]]
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


def test_find_elements_by_tag_should_only_return_matching_elements_until_all_children_are_exhausted(
        list_element_with_embedded_list):
    element = list_element_with_embedded_list

    actual = find_elements_by_tag(element, tag_names=['li'], max_depth=10)
    expected = [element[0], element[1], element[2], element[0][0][0], element[2][1][0]]
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)
