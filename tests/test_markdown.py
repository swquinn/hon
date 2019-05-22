import pytest
from hon.markdown import Markdown


@pytest.fixture
def document():
    return """
# A Title

[First](./first.md)

---

[Second](./second.md)

- List Item A
- List Item B
- List Item C

[Third](./third.md)

With some text in between and a **bolded** item with _emphasis_.

[Foruth](./fourth.md)

---

[Fifth](./fifth.md)"""


def test_markdown_elements(document):
    md = Markdown()
    md.convert(document)

    actual_tags = [e.tag for e in list(md.elements)]
    expected_tags = ['h1', 'p', 'hr', 'p', 'ul', 'p', 'p', 'p', 'hr', 'p']

    assert len(md.elements) == len(expected_tags)
    assert actual_tags == expected_tags


def test_markdown_reverse_elements(document):
    md = Markdown()
    md.convert(document)

    actual_tags = [e.tag for e in list(md.reverse_elements)]
    expected_tags = ['p', 'hr', 'p', 'p', 'p', 'ul', 'p', 'hr', 'p', 'h1']

    assert len(md.elements) == len(expected_tags)
    assert actual_tags == expected_tags
