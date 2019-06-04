import os
import markdown

from collections.abc import Iterable, Iterator
from hon.structure import Link, Part
from hon.summary import parse_summary


def _flatten_book_items(items):
    """Flattens all book items into a single array.

    :param items: A collection of book items.
    :type items: []
    """
    flattened = []
    for item in items:
        flattened.append(item)
        if hasattr(item, 'children') and item.children:
            flattened.extend(_flatten_book_items(item.children))
    return flattened


#: TODO: Add iterable into this, mdBook's iterator was immutable
class Book(object):
    """A simple tree structure representing a book.

    A book is a collection of ``BookItems``, which are typically rendered as
    either ``Chapters`` or ``Separators``.

    :type name: str
    :type authors: str or []
    :type language: str
    :type config: Config
    :type sections: []
    """

    @property
    def items(self):
        #: TODO: This presents a view of the flattened book of all the sections.
        flattened_book = _flatten_book_items(self.sections)
        return list(flattened_book)

    def __init__(self, app=None, name=None, path=None, authors=None, language=None, config=None):
        #: The configuration associated with the book, if the configuration
        #: supplies overrides for the book's name, authors, etc. it will
        #: overwrite the values that may have been passed down to the
        #: instantiated ``Book`` object.`
        self.config = config or {}

        #: The name of the book.
        self.name = name

        #: The author(s) associated with the book. This can be either a string
        #: or an array of author names.
        self.authors = authors

        #: The language that the book is written in. If no language is
        #: explicitly defined, this will be ``None``.`
        self.language = language

        #: The path to the book.
        self.path = path

        #: 
        self.sections = []

        self.glossary = None
        self.readme = None
        self.summary = None

        if app:
            self.init_app(app)

        self._configure()

    def _configure(self):
        self.name = self.config.get('title') or self.name
        self.authors = self.config.get('authors') or self.authors
        self.language = self.config.get('language') or self.language

    def add(self, item):
        self.sections.append(item)
    
    def add_all(self, items):
        self.sections.extend(items)

    def init_app(self, app):
        self.app = app

    def load(self, app=None):
        """Load a book into memory."""
        if app:
            self.init_app(app)

        print()
        self.app.logger.info('Loading book: {}'.format(self.name))
        self.parse_contents()

        # if cfg.create_missing {
        #     create_missing(&src_dir, &summary).chain_err(|| "Unable to create missing chapters")?;
        # }

        self.load_book_from_disk()

    def load_book_from_disk(self):
        """Use the book's summary to load the book's pages from disk."""
        self.app.logger.debug('Loading book from disk')

        summary_items = self.summary.all_parts
        print('**** summary items: {}'.format(summary_items))

        for item in summary_items:
            if type(item) == Part:
                chapter = self.load_chapter(item)
                self.sections.append(chapter)
    
    def load_chapter(self, item, parent=None):
        chapter = None
        chapter_path = os.path.abspath(os.path.join(self.path, item.source))
        
        if not os.path.exists(chapter_path):
            raise FileNotFoundError('File: {} not found.'.format(chapter_path))
                
        with open(chapter_path) as f:
            raw = f.read()
            chapter = Chapter(name=item.name, raw_text=raw, path=chapter_path, number=item.level, parent=parent)
        
        if not chapter:
            raise TypeError('Chapter not created')

        sub_chapters = []
        if item.children:
            for sub_item in item.children:
                sub_chapter = self.load_chapter(sub_item, parent=item)
                sub_chapters.append(sub_chapter)
        
        if sub_chapters:
            chapter.children = sub_chapters
        return chapter

    def parse_contents(self):
        # parse_readme(self)
        parse_summary(self)
        # parse_glossary(self)
    
    def __repr__(self):
        return ('Book(name={name}, path={path}, authors={authors}, '
            'language={language}, config={config})').format(
            name=repr(self.name), path=repr(self.path),
            authors=repr(self.authors), language=repr(self.language),
            config=repr(self.config))


class BookItem(object):
    """The base class for all book items."""
    PART = 'Chapter'
    SEPARATOR = 'Separator'

    def __init__(self, book_item_type):
        #: All book items have a type associated with them, this can be used
        #: to control logic specific to that type.
        self.type = book_item_type


class Chapter(BookItem):
    """A Chapter represents an entry in a book.

    FROM mdBook:
        A Chapter is a representation of a "chapter", usually mapping to
        a single file on disk however it may contain multiple sub-chapters.

    :type name: str
    :type raw_text: str
    :type children: []
    :type path: str
    """

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

    def __init__(self, name=None, raw_text=None, path=None, number=None, parent=None, children=None):
        super(Chapter, self).__init__(BookItem.PART)

        #: The name of the entry.
        self.name = name

        #: The page's location on the filesystem
        self.path = path        

        #: The entry's raw, unprocessed, text.
        self.raw_text = raw_text

        #: The processed text.
        self.text = None

        #: The children of this page.
        self.children = children or []
    
    def __repr__(self):
        return ('Chapter(name={name}, raw_text=..., path={path}, '
            'number=..., parent=..., children=...)').format(
            name=self.name, path=self.path)


class Separator(BookItem):
    def __init__(self):
        super(Separator, self).__init__(BookItem.SEPARATOR)
    
    def __repr__(self):
        return 'Separator()'
