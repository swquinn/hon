import os
import markdown

from collections.abc import Iterable, Iterator
from hon.structure import Link
from hon.summary import parse_summary


# pub fn for_each_mut<'a, F, I>(func: &mut F, items: I)
# where
#     F: FnMut(&mut BookItem),
#     I: IntoIterator<Item = &'a mut BookItem>,
# {
#     for item in items {
#         if let &mut BookItem::Chapter(ref mut ch) = item {
#             for_each_mut(func, &mut ch.sub_items);
#         }
#         func(item);
#     }
# }

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
    either ``Parts`` or ``Separators``.

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

    #: TODO: Add a function that can iterate over the items in a book and mutate them with a [closure]
    # for_each_mutate(self, func):
    #     /// Recursively apply a closure to each item in the book, allowing you to
    #     /// mutate them.
    #     ///
    #     /// # Note
    #     ///
    #     /// Unlike the `iter()` method, this requires a closure instead of returning
    #     /// an iterator. This is because using iterators can possibly allow you
    #     /// to have iterator invalidation errors.
    #     pub fn for_each_mut<F>(&mut self, mut func: F)
    #     where
    #         F: FnMut(&mut BookItem),
    #     {
    #         for_each_mut(&mut func, &mut self.sections);
    #     }

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

    # /// Use the provided `Summary` to load a `Book` from disk.
    # ///
    # /// You need to pass in the book's source directory because all the links in
    # /// `SUMMARY.md` give the chapter locations relative to it.
    # fn load_book_from_disk<P: AsRef<Path>>(summary: &Summary, src_dir: P) -> Result<Book> {
    def load_book_from_disk(self):
        self.app.logger.debug('Loading book from disk')
        prefix = tuple(self.summary.prefix_parts)
        numbered = tuple(self.summary.numbered_parts)
        suffix = tuple(self.summary.suffix_parts)

        summary_items = prefix + numbered + suffix

        for item in summary_items:
            if type(item) == Link:
                chapter = self.load_chapter(item)
                self.sections.append(chapter)
            elif type(item) == Separator:
    
    def load_chapter(self, item, parent=None):
        part = None
        chapter_path = os.path.abspath(os.path.join(self.path, item.location))
        
        if not os.path.exists(chapter_path):
            raise FileNotFoundError('File: {} not found.'.format(chapter_path))
                
        with open(chapter_path) as f:
            raw = f.read()
            part = Part(name=item.name, raw_text=raw, path=chapter_path, number=item.level, parent=parent)
        
        if not part:
            raise TypeError('Part not created')

        sub_parts = []
        if item.children:
            for sub_item in item.children:
                sub_part = self.load_chapter(sub_item, parent=item)
                sub_parts.append(sub_part)
        
        if sub_parts:
            part.children = sub_parts
        return part

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
    PART = 'Part'
    SEPARATOR = 'Separator'

    def __init__(self, book_item_type):
        #: All book items have a type associated with them, this can be used
        #: to control logic specific to that type.
        self.type = book_item_type


class Part(BookItem):
    """A Part represents an entry in a book.

    FROM mdBook:
        A Part is a representation of a "chapter", usually mapping to
        a single file on disk however it may contain multiple sub-chapters.

    :type name: str
    :type raw_text: str
    :type children: []
    :type path: str
    """

    # TODO: Add ``number`` ?? (The chapter's section number, if it has one.)
    # TODO: Add ``parent_names`` ?? (An ordered list of the names of each chapter above this one, in the hierarchy.)
    def __init__(self, name=None, raw_text=None, path=None, number=None, parent=None, children=None):
        super(Part, self).__init__(BookItem.PART)

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
        return ('Part(name={name}, raw_text=..., path={path}, '
            'number=..., parent=..., children=...)').format(
            name=self.name, path=self.path)


class Separator(BookItem):
    def __init__(self):
        super(Separator, self).__init__(BookItem.SEPARATOR)
    
    def __repr__(self):
        return 'Separator()'
