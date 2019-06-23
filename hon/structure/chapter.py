"""
    hon.structure.chapter
    ~~~~~
"""
import os


class Chapter(object):
    """A ``Chapter`` represents an entry in a book.

    In many cases, a chapter usually maps to a single file on disk. However,
    a chapter may contain one-or-more subchapters as well.

    Chapters not only represent their own content (both raw and processed text),
    but also serve as a node in a graph that represents the book. When a chapter
    is rendered by some renderers it needs to know what is the previous chapter
    as well as the next chapter, to provide better navigation.

    Relative navigation for a chapter looks something like the following
    diagram:

    .. ::

                 parent
                   ^^
                   ||
            prev <----> next

    :type name: str
    :type raw_text: str
    :type children: []
    :type path: str
    :type parent: Chapter
    :type previous_chapter: Chapter
    :type next_chapter: Chapter
    """

    @property
    def content(self):
        return self.text

    @property
    def filename(self):
        filename, _ = os.path.splitext(os.path.basename(self.path))
        return filename

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

        #: What was the previous chapter? If ``None`` there is no previous 
        #: chapter, and this chapter is assumed to be the first entry in the
        #: book.
        self.previous_chapter = None

        #: What is the next chapter? If ``None`` there is no chapter that
        #: follows this one and this chapter is assumed to be the final entry
        #: in the book.
        self.next_chapter = None

    def __repr__(self):
        truncated_text = ''
        if self.raw_text:
            truncated_text = '{}...'.format(self.raw_text[:10])
        return ('<Chapter(name={name}, raw_text={raw_text}, path={path}, '
            'parent={parent}, children={children})>').format(
            name=self.name, raw_text=repr(truncated_text), path=self.path,
            parent=self.parent, children=repr(self.children))

