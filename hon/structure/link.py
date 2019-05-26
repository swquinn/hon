"""
    hon.structure.link
    ~~~~~

    Module representing a ``Link`` structural element.
"""


class Link():
    """A structure representing links to chapters within ``SUMMARY.md``.

    Links have a ``name``, ``source`` (roughly equivalent to the ``href=``
    attribute on an HTML anchor link tag), a ``level`` which indicates link
    hierarchy, and links may possible contain nested links.

    Below is a representation of a valid link structure for the summary.

    ::

      [Foreward](./path/to/foreward.md)

      - [Chapter 1](./path/to/chapter1.md)
      - [Chapter 2](./path/to/chapter2.md)
        - [Chapter 2.1](./path/to/chapter2-1.md)
      - [Chapter 3](./path/to/chapter3.md)

      [Epilogue](./path/to/epilogue.md)
    
    Both the ``Foreward`` and ``Epilogue`` links will have no level associated
    with them, as they are interpretted outside of a hierarchical structure.

    The chapters, however, being part of a list structure will have levels of
    hierarchy (``level=0`` for chapters 1, 2, and 3, and ``level=1`` for chapter
    2.1).
    
    In the above example, chapter 2 will also have a single nested item.

    :type name: str
    :type source: str
    :type level: int
    :type children: list
    """

    def __init__(self, name=None, source=None, level=None, children=None):
        #: The name of the chapter.
        self.name = name

        #: The source of the chapter's source file, taking the book's `src`
        #: directory as the root.
        self.source = source

        #: The section level, if this chapter is in the leveled section.
        self.level = level

        #: Any nested items this chapter may contain.
        self.children = children or []
    
    def __eq__(self, other):
        if (self.name == other.name and
            self.source == other.source and
            self.level == other.level and
            self.children == other.children):
            return True
        return False

    def __repr__(self):
        return ('Link(name={name}, source={source}, level={level})'.format(
            name=repr(self.name), source=repr(self.source),
            level=repr(self.level)))
    
    def append(self, link):
        self.children.append(link)
    
    def extend(self, links):
        self.children.extend(links)