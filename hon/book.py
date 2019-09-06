"""
    hon.book
    ~~~~~
"""
import os
import markdown

from collections.abc import Iterable, Iterator
from hon.structure import Chapter, Part
from hon.summary import parse_summary


#: TODO: Add iterable into this, mdBook's iterator was immutable
class Book(object):
    """A simple tree structure representing a book.

    A book is a collection of ``BookItems``, which are typically rendered as
    either ``Chapters`` or ``Separators``.

    :type name: str
    :type author: str or []
    :type language: str
    :type config: Config
    """

    @property
    def title(self):
        return self.name

    def __init__(self, app=None, name=None, path=None, author=None, language=None, config=None):
        #: The configuration associated with the book, if the configuration
        #: supplies overrides for the book's name, author, etc. it will
        #: overwrite the values that may have been passed down to the
        #: instantiated ``Book`` object.`
        self.config = config or {}

        #: The name of the book.
        self.name = name

        #: The author(s) associated with the book. This can be either a string
        #: or an array of author names.
        self.author = author

        #: The language that the book is written in. If no language is
        #: explicitly defined, this will be ``None``.`
        self.language = language

        #: The path to the book.
        self.path = path

        self.glossary = None
        self.readme = None
        self.summary = None

        if app:
            self.init_app(app)

        self._configure()

    def _configure(self):
        self.name = self.config.get('title') or self.name
        self.author = self.config.get('author') or self.author
        self.language = self.config.get('language') or self.language

    def init_app(self, app):
        self.app = app

    def load(self, app=None):
        """Load a book into memory."""
        if app:
            self.init_app(app)

        self.app.logger.info('Loading book: {}'.format(self.name))
        self.parse_structure()

    def parse_structure(self):
        """Parse a the structure files defining a book.

        First parse the ``README``, which acts as the book's cover page.

        Next, parse the summary.

        Finally, parse the book's glossary.
        """
        # parse_readme(self)
        parse_summary(self)
        # parse_glossary(self)

    def __repr__(self):
        return ('Book(name={name}, path={path}, author={author}, '
            'language={language}, config={config})').format(
            name=repr(self.name), path=repr(self.path),
            author=repr(self.author), language=repr(self.language),
            config=repr(self.config))
