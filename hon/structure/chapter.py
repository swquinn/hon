"""
    hon.structure.chapter
    ~~~~~
"""
import os


class Chapter(object):
    """A ``Chapter`` represents an entry in a book.

    In many cases, a chapter usually maps to a single file on disk. However,
    a chapter may contain one-or-more subchapters as well.

    :type name: str
    :type raw_text: str
    :type children: []
    :type path: str
    """

    @property
    def content(self):
        return self.text

    @property
    def filename(self):
        filename, _ = os.path.splitext(os.path.basename(self.path))
        return filename

    @property
    def has_children(self):
        return len(self.children) >= 1

    @property
    def is_readme(self):
        filename = os.path.basename(self.path)
        root, _ = os.path.splitext(filename)
        if root.lower() == 'readme':
            return True
        return False

    @property
    def keywords(self):
        return []

    @property
    def search(self):
        return True

    @property
    def summary(self):
        return ''

    @property
    def title(self):
        return self.name

    def __init__(self, name=None, raw_text=None, path=None, link=None, parent=None, children=None):
        #: The name of the entry.
        self.name = name

        #: The page's location on the filesystem
        self.path = path

        #: The link to this chapter.
        self.link = link

        #: The entry's raw, unprocessed, text.
        self.raw_text = raw_text or ''

        #: The processed text.
        self.text = ''

        self.parent = parent

        #: The children of this page.
        self.children = children or []

    def __repr__(self):
        truncated_text = ''
        if self.raw_text:
            truncated_text = '{}...'.format(self.raw_text[:10])
        return ('<Chapter(name={name}, raw_text={raw_text}, path={path}, '
            'parent={parent}, children={children})>').format(
            name=self.name, raw_text=repr(truncated_text), path=self.path,
            parent=self.parent, children=repr(self.children))


class ChapterNode(object):
    """A node in a chapter graph.

    In order to navigate chapters, we represent each chapter as a node in a
    graph. When a chapter is added to the graph, a new node is created and the
    previous and next node references are set.

    Relative navigation for a chapter looks something like the following
    diagram:

    .. ::

                 parent
                   ^^
                   ||
            prev <----> next

    :type parent: Chapter
    :type previous_chapter: Chapter
    :type next_chapter: Chapter
    """

    def __init__(self, chapter, next_node=None, previous_node=None):
        #: The chapter represented by this node in the graph.
        self.chapter = chapter

        #: What is the previous node in the graph? If ``None`` there is no
        #: previous node, and this node is assumed to be the first entry in the
        #: graph.
        self.previous = previous_node

        #: What is the next node in the graph? If ``None`` there is no node that
        #: follows this one and this is the final node in the graph.
        self.next = next_node


class ChapterGraph(object):
    """A graph of all chapters in a book.
    """

    @property
    def first(self):
        return self._head

    @property
    def last(self):
        return self._tail

    def __init__(self, chapters=None):
        #: Used for tracking iteration state. This is reset to the head
        self._current = None
        self._head = None
        self._tail = None

        if chapters:
            self.extend(chapters)

    def __iter__(self):
        self._current = ChapterNode(None, next_node=self._head)
        return self

    def __next__(self):
        node = self._current.next
        if node is None:
            raise StopIteration
        self._current = node
        return self._current

    def append(self, chapter, include_children=True):
        """
        """
        node = ChapterNode(chapter)
        if self._head is None:
            self._head = self._tail = node
        else:
            node.previous = self._tail
            node.next = None

            self._tail.next = node
            self._tail = node

        if chapter.has_children:
            for child in chapter.children:
                self.append(child, include_children=include_children)

    def extend(self, chapters, include_children=True):
        for chapter in chapters:
            self.append(chapter, include_children=include_children)

    def get(self, chapter):
        node = self._head
        while node is not None:
            if node.chapter == chapter:
                return node
            node = node.next
        return None
