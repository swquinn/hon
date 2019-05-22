import os
import markdown

from collections.abc import Iterable, Iterator
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
    print("Processing: {}".format(items))
    flattened = []
    for item in items:
        print("Adding: {}".format(item))
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
    #     debug!("Loading the book from disk");
    #     let src_dir = src_dir.as_ref();

    #     let prefix = summary.prefix_chapters.iter();
    #     let numbered = summary.numbered_chapters.iter();
    #     let suffix = summary.suffix_chapters.iter();

    #     let summary_items = prefix.chain(numbered).chain(suffix);

    #     let mut chapters = Vec::new();

    #     for summary_item in summary_items {
    #         let chapter = load_summary_item(summary_item, src_dir, Vec::new())?;
    #         chapters.push(chapter);
    #     }

    #     Ok(Book {
    #         sections: chapters,
    #         __non_exhaustive: (),
    #     })
    # }
        print(self.summary.title)
        print(self.summary.numbered_parts)
        pass
    
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




# use std::collections::VecDeque;
# use std::fmt::{self, Display, Formatter};
# use std::fs::{self, File};
# use std::io::{Read, Write};
# use std::path::{Path, PathBuf};

# use config::BuildConfig;
# use errors::*;

# fn create_missing(src_dir: &Path, summary: &Summary) -> Result<()> {
#     let mut items: Vec<_> = summary
#         .prefix_chapters
#         .iter()
#         .chain(summary.numbered_chapters.iter())
#         .chain(summary.suffix_chapters.iter())
#         .collect();

#     while !items.is_empty() {
#         let next = items.pop().expect("already checked");

#         if let SummaryItem::Link(ref link) = *next {
#             let filename = src_dir.join(&link.location);
#             if !filename.exists() {
#                 if let Some(parent) = filename.parent() {
#                     if !parent.exists() {
#                         fs::create_dir_all(parent)?;
#                     }
#                 }
#                 debug!("Creating missing file {}", filename.display());

#                 let mut f = File::create(&filename)?;
#                 writeln!(f, "# {}", link.name)?;
#             }

#             items.extend(&link.nested_items);
#         }
#     }

#     Ok(())
# }

# /// Enum representing any type of item which can be added to a book.
# #[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
# pub enum BookItem {
#     /// A nested chapter.
#     Chapter(Chapter),
#     /// A section separator.
#     Separator,
# }

# impl From<Chapter> for BookItem {
#     fn from(other: Chapter) -> BookItem {
#         BookItem::Chapter(other)
#     }
# }

# impl Chapter {
#     /// Create a new chapter with the provided content.
#     pub fn new<P: Into<PathBuf>>(
#         name: &str,
#         content: String,
#         path: P,
#         parent_names: Vec<String>,
#     ) -> Chapter {
#         Chapter {
#             name: name.to_string(),
#             content,
#             path: path.into(),
#             parent_names,
#             ..Default::default()
#         }
#     }
# }

# fn load_summary_item<P: AsRef<Path>>(
#     item: &SummaryItem,
#     src_dir: P,
#     parent_names: Vec<String>,
# ) -> Result<BookItem> {
#     match *item {
#         SummaryItemSeparator => Ok(BookItem::Separator),
#         SummaryItem::Link(ref link) => {
#             load_chapter(link, src_dir, parent_names).map(BookItem::Chapter)
#         }
#     }
# }

# fn load_chapter<P: AsRef<Path>>(
#     link: &Link,
#     src_dir: P,
#     parent_names: Vec<String>,
# ) -> Result<Chapter> {
#     debug!("Loading {} ({})", link.name, link.location.display());
#     let src_dir = src_dir.as_ref();

#     let location = if link.location.is_absolute() {
#         link.location.clone()
#     } else {
#         src_dir.join(&link.location)
#     };

#     let mut f = File::open(&location)
#         .chain_err(|| format!("Chapter file not found, {}", link.location.display()))?;

#     let mut content = String::new();
#     f.read_to_string(&mut content)
#         .chain_err(|| format!("Unable to read \"{}\" ({})", link.name, location.display()))?;

#     let stripped = location
#         .strip_prefix(&src_dir)
#         .expect("Chapters are always inside a book");

#     let mut sub_item_parents = parent_names.clone();
#     let mut ch = Chapter::new(&link.name, content, stripped, parent_names);
#     ch.number = link.number.clone();

#     sub_item_parents.push(link.name.clone());
#     let sub_items = link
#         .nested_items
#         .iter()
#         .map(|i| load_summary_item(i, src_dir, sub_item_parents.clone()))
#         .collect::<Result<Vec<_>>>()?;

#     ch.sub_items = sub_items;

#     Ok(ch)
# }

# /// A depth-first iterator over the items in a book.
# ///
# /// # Note
# ///
# /// This struct shouldn't be created directly, instead prefer the
# /// [`Book::iter()`] method.
# ///
# /// [`Book::iter()`]: struct.Book.html#method.iter
# pub struct BookItems<'a> {
#     items: VecDeque<&'a BookItem>,
# }

# impl<'a> Iterator for BookItems<'a> {
#     type Item = &'a BookItem;

#     fn next(&mut self) -> Option<Self::Item> {
#         let item = self.items.pop_front();

#         if let Some(&BookItem::Chapter(ref ch)) = item {
#             // if we wanted a breadth-first iterator we'd `extend()` here
#             for sub_item in ch.sub_items.iter().rev() {
#                 self.items.push_front(sub_item);
#             }
#         }

#         item
#     }
# }

# impl Display for Chapter {
#     fn fmt(&self, f: &mut Formatter) -> fmt::Result {
#         if let Some(ref section_number) = self.number {
#             write!(f, "{} ", section_number)?;
#         }

#         write!(f, "{}", self.name)
#     }
# }
