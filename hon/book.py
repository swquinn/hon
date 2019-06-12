"""
    hon.book
    ~~~~~
"""
import os
import markdown

from collections.abc import Iterable, Iterator
from hon.structure import Chapter, Link, Part
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
    :type chapters: []
    """

    @property
    def items(self):
        #: TODO: This presents a view of the flattened book of all the chapters.
        flattened_book = _flatten_book_items(self.chapters)
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
        self.chapters = []

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

    def add_chapter(self, chapter):
        """Adds a chapter to the book, updating the graph."""
        last_chapter = self.chapters[-1] if self.chapters else None

        #: If we're adding a new chapter, and it isn't the first chapter, we
        #: need to Update the chapter we're adding to point to the previous
        #: chapter AND the previous chapter's next chapter pointer to reference
        #: the chapter being added.
        if last_chapter:
            chapter.previous_chapter = last_chapter
            last_chapter.next_chapter = chapter
        self.chapters.append(chapter)
    
    def add_chapters(self, chapters):
        """Adds all chapters to a book, updating the graph."""
        for chapter in chapters:
            self.add_chapter(chapter)

    def get_variables(self):
        if not self.app:
            return {}
        
        variables_preprocessor = self.app.get_preprocessor('variables')
        if variables_preprocessor and variables_preprocessor.enabled:
            return variables_preprocessor.variables
        return {}

    def init_app(self, app):
        self.app = app

    def load(self, app=None):
        """Load a book into memory."""
        if app:
            self.init_app(app)

        for preprocessor in self.app.preprocessors:
            preprocessor.init_book(self)

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
                self.add_chapter(chapter)
    
    def load_chapter(self, item, parent=None):
        chapter = None
        chapter_path = os.path.abspath(os.path.join(self.path, item.source))
        
        if not os.path.exists(chapter_path):
            raise FileNotFoundError('File: {} not found.'.format(chapter_path))
                
        with open(chapter_path) as f:
            raw = f.read()
            chapter = Chapter(name=item.name, raw_text=raw, path=chapter_path, link=item.link, parent=parent)
        
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
