import pytest
from hon.book import (
    Book, BookItem, Chapter, Separator
)

@pytest.fixture
def chapter_content():
    return """static str = "
# Dummy Chapter

this is some dummy text.

And here is some \
                                     more text.
"""


@pytest.fixture
def philosophy_book():
    book = Book(
        name='Groundwork of the Metaphysic of Morals',
        authors=[
            'Immanual Kant'
        ]
    )
    return book


@pytest.fixture
def sample_chapter(chapter_content):
    chapter = Chapter(name='Chapter 1', raw_text=chapter_content)
    return chapter


@pytest.fixture
def sample_chapter_with_nested_items(chapter_content):
    nested_items = [
        Chapter(name='Hello, World!'),
        Separator(),
        Chapter(name='Goodbye, Cruel World!')
    ]
    chapter = Chapter(
        name='Chapter 1',
        raw_text=chapter_content,
        path='Chapter_1/index.md',
        children=nested_items,
        number=None,
        parent=None
    )
    return chapter


def test_book_iter_iterates_over_sequential_items(philosophy_book, sample_chapter):
    philosophy_book.add_all([sample_chapter, Separator()])

    expected = philosophy_book.sections
    actual = philosophy_book.items
    assert actual == expected


def test_iterate_over_nested_book_items(philosophy_book, sample_chapter_with_nested_items):
    philosophy_book.add_all([
        sample_chapter_with_nested_items,
        Separator()
    ])

    actual = philosophy_book.items
    assert len(actual) == 5
    
    chapter_names = [item.name for item in actual if item.type == BookItem.PART]
    assert chapter_names == ['Chapter 1', 'Hello, World!', 'Goodbye, Cruel World!']


# #[cfg(test)]
# mod tests {
#     use super::*;
#     use std::io::Write;
#     use tempfile::{Builder as TempFileBuilder, TempDir};

#     const DUMMY_SRC: &'static str = "
# # Dummy Chapter

# this is some dummy text.

# And here is some \
#                                      more text.
# ";

#     /// Create a dummy `Link` in a temporary directory.
#     fn dummy_link() -> (Link, TempDir) {
#         let temp = TempFileBuilder::new().prefix("book").tempdir().unwrap();

#         let chapter_path = temp.path().join("chapter_1.md");
#         File::create(&chapter_path)
#             .unwrap()
#             .write(DUMMY_SRC.as_bytes())
#             .unwrap();

#         let link = Link::new("Chapter 1", chapter_path);

#         (link, temp)
#     }

#     /// Create a nested `Link` written to a temporary directory.
#     fn nested_links() -> (Link, TempDir) {
#         let (mut root, temp_dir) = dummy_link();

#         let second_path = temp_dir.path().join("second.md");

#         File::create(&second_path)
#             .unwrap()
#             .write_all("Hello World!".as_bytes())
#             .unwrap();

#         let mut second = Link::new("Nested Chapter 1", &second_path);
#         second.number = Some(SectionNumber(vec![1, 2]));

#         root.nested_items.push(second.clone().into());
#         root.nested_items.push(SummaryItemSeparator);
#         root.nested_items.push(second.clone().into());

#         (root, temp_dir)
#     }

#     #[test]
#     fn load_a_single_chapter_from_disk() {
#         let (link, temp_dir) = dummy_link();
#         let should_be = Chapter::new(
#             "Chapter 1",
#             DUMMY_SRC.to_string(),
#             "chapter_1.md",
#             Vec::new(),
#         );

#         let got = load_chapter(&link, temp_dir.path(), Vec::new()).unwrap();
#         assert_eq!(got, should_be);
#     }

#     #[test]
#     fn cant_load_a_nonexistent_chapter() {
#         let link = Link::new("Chapter 1", "/foo/bar/baz.md");

#         let got = load_chapter(&link, "", Vec::new());
#         assert!(got.is_err());
#     }

#     #[test]
#     fn load_recursive_link_with_separators() {
#         let (root, temp) = nested_links();

#         let nested = Chapter {
#             name: String::from("Nested Chapter 1"),
#             content: String::from("Hello World!"),
#             number: Some(SectionNumber(vec![1, 2])),
#             path: PathBuf::from("second.md"),
#             parent_names: vec![String::from("Chapter 1")],
#             sub_items: Vec::new(),
#         };
#         let should_be = BookItem::Chapter(Chapter {
#             name: String::from("Chapter 1"),
#             content: String::from(DUMMY_SRC),
#             number: None,
#             path: PathBuf::from("chapter_1.md"),
#             parent_names: Vec::new(),
#             sub_items: vec![
#                 BookItem::Chapter(nested.clone()),
#                 BookItem::Separator,
#                 BookItem::Chapter(nested.clone()),
#             ],
#         });

#         let got = load_summary_item(&SummaryItem::Link(root), temp.path(), Vec::new()).unwrap();
#         assert_eq!(got, should_be);
#     }

#     #[test]
#     fn load_a_book_with_a_single_chapter() {
#         let (link, temp) = dummy_link();
#         let summary = Summary {
#             numbered_chapters: vec![SummaryItem::Link(link)],
#             ..Default::default()
#         };
#         let should_be = Book {
#             sections: vec![BookItem::Chapter(Chapter {
#                 name: String::from("Chapter 1"),
#                 content: String::from(DUMMY_SRC),
#                 path: PathBuf::from("chapter_1.md"),
#                 ..Default::default()
#             })],
#             ..Default::default()
#         };

#         let got = load_book_from_disk(&summary, temp.path()).unwrap();

#         assert_eq!(got, should_be);
#     }
#     #[test]
#     fn for_each_mut_visits_all_items() {
#         let mut book = Book {
#             sections: vec![
#                 BookItem::Chapter(Chapter {
#                     name: String::from("Chapter 1"),
#                     content: String::from(DUMMY_SRC),
#                     number: None,
#                     path: PathBuf::from("Chapter_1/index.md"),
#                     parent_names: Vec::new(),
#                     sub_items: vec![
#                         BookItem::Chapter(Chapter::new(
#                             "Hello World",
#                             String::new(),
#                             "Chapter_1/hello.md",
#                             Vec::new(),
#                         )),
#                         BookItem::Separator,
#                         BookItem::Chapter(Chapter::new(
#                             "Goodbye World",
#                             String::new(),
#                             "Chapter_1/goodbye.md",
#                             Vec::new(),
#                         )),
#                     ],
#                 }),
#                 BookItem::Separator,
#             ],
#             ..Default::default()
#         };

#         let num_items = book.iter().count();
#         let mut visited = 0;

#         book.for_each_mut(|_| visited += 1);

#         assert_eq!(visited, num_items);
#     }

#     #[test]
#     fn cant_load_chapters_with_an_empty_path() {
#         let (_, temp) = dummy_link();
#         let summary = Summary {
#             numbered_chapters: vec![SummaryItem::Link(Link {
#                 name: String::from("Empty"),
#                 location: PathBuf::from(""),
#                 ..Default::default()
#             })],
#             ..Default::default()
#         };

#         let got = load_book_from_disk(&summary, temp.path());
#         assert!(got.is_err());
#     }

#     #[test]
#     fn cant_load_chapters_when_the_link_is_a_directory() {
#         let (_, temp) = dummy_link();
#         let dir = temp.path().join("nested");
#         fs::create_dir(&dir).unwrap();

#         let summary = Summary {
#             numbered_chapters: vec![SummaryItem::Link(Link {
#                 name: String::from("nested"),
#                 location: dir,
#                 ..Default::default()
#             })],
#             ..Default::default()
#         };

#         let got = load_book_from_disk(&summary, temp.path());
#         assert!(got.is_err());
#     }
# }
