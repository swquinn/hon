import re
from collections import namedtuple
from hon.utils.numberutils import to_int_ns
from .preprocessor import Preprocessor
# use utils::fs::file_to_string;
# use utils::take_lines;

ESCAPE_CHAR = '\\'

INCLUDE_TYPE_INCLUDE = 'include'
INCLUDE_TYPE_PLAYPEN = 'playpen'
INCLUDE_TYPE_TABLE = 'table'

#: The maximum depth for nested includes. This is to prevent us from going to
#: deep in processing includes. It may be unnecessary, we can re-evaluate in
#: the future.
MAX_INCLUDE_NESTED_DEPTH = 10

#: The ``SelectRange`` is a simple, light weight, object that can be used to
#: represent a selection range (from and to) in a body of text that is being
#: included.
SelectRange = namedtuple('SelectRange', ['start', 'stop'])
SelectRange.__new__.__defaults__ = (None, None)

IncludeMeta = namedtuple('IncludeMeta', ['text', 'start_index', 'end_index'])
IncludeMeta.__new__.__defaults__ = (None, None, None)


def _create_include_item(include_type, include_args=None, metadata=None):
    if include_type[0] == ESCAPE_CHAR:
        return IncludeItem(
            start_index=metadata.start_index,
            end_index=metadata.end_index,
            include_text=metadata.text,
            include=EscapedInclude()
        )

    file_target, file_props = _parse_include_arguments(include_args)

    #: Short circuit out of this if there's no target to include.
    if not file_target:
        return None

    file_path, selection_range = _parse_target(file_target)
    if include_type == INCLUDE_TYPE_INCLUDE:
        return IncludeItem(
            start_index=metadata.start_index,
            end_index=metadata.end_index,
            include_text=metadata.text,
            include=IncludeRange(path=file_path, select_range=selection_range)
        )
    elif include_type == INCLUDE_TYPE_PLAYPEN:
        return IncludeItem(
            start_index=metadata.start_index,
            end_index=metadata.end_index,
            include_text=metadata.text,
            include=Playpen(path=file_path)
        )
    return None


def _parse_include_arguments(s):
    """Given a string, returns the file target and list of properties.

    A file target may be the file path for the whole file, e.g.
    ``/path/to/my/file.md``, or it might specify some slice of the file e.g.
    ``/path/to/my/file.md:10:20``.

    The file target is separated from file properties by one or more spaces.

    :param s: The string being parsed for target and props.
    :return: A tuple of the file target and list of properties.
    """
    items = s.strip().split(' ')
    return (items[0], items[1:])


def _parse_target(target):
    """Parses a target string into the file path and selection range.

    :param target: The include target string.
    :return: A tuple of the file path and the selection range.
    """
    #: Split the target along the ``:`` character, but right pad the array with
    #: None-values, regardless of how many values, only take the first three.
    #: this ensures that we have a consistent size array to deal with, always
    #: and that the first element is always the file path, the second is the
    #: starting range, and the third is the ending range.
    target_parts = (target.strip().split(':') + (3 * [None]))[:3]

    file_path = target_parts[0]
    select_range = None

    start_range = to_int_ns(target_parts[1] or None)
    end_range = to_int_ns(target_parts[2] or None)
    if start_range or end_range:
        select_range = SelectRange(start=start_range, stop=end_range)
    return (file_path, select_range)


def process_matches(matches):
    results = []
    print(f'Found {len(matches)}')
    for index, match in enumerate(matches):
        meta = IncludeMeta(text=match.group(0), start_index=match.start(), end_index=match.end())

        filtered = [m for m in match.groups() if m]
        print(f'matching {index+1}: {filtered}')
        item = _create_include_item(*filtered, metadata=meta)
        if item:
            results.append(item)
    return results


def find_includes(contents):
    pattern = (
        r'(\\\{\{\#.+\}\})'             # match an escaped include, e.g. \{#include ...}
        r'|'                            # or
        r'\{\{\s*'                      # include opening parens and whitespace
        r'\#([a-zA-Z\d]+)'              # the include type
        r'\s+'                          # separating whitespace
        r'([a-zA-Z\d\s_\.\-:/\\]+)'     # the inclusion target, posibly including range limitations
        r'\s*\}\}'                      # whitespace and include closing parens
    )
    match_iter = re.finditer(pattern, contents, flags=(re.MULTILINE & re.IGNORECASE))
    matches = list(match_iter)
    return process_matches(matches)


class IncludeType(object):

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{class_name}()'.format(class_name=class_name)


class IncludeItem(IncludeType):

    def __init__(self, start_index=None, end_index=None, include=None, include_text=None):
        #: int - starting position where to begin swapping out the text
        self.start_index = start_index
        #: int - ending position where to begin swapping out the text
        self.end_index = end_index
        #: inclusion instance type, e.g. playpen, include, etc.
        self.include = include
        #: str
        self.include_text = include_text

    # fn from_capture(cap: Captures<'a>) -> Option<Link<'a>> {
    #     let link_type = match (cap.get(0), cap.get(1), cap.get(2)) {
    #         (_, Some(typ), Some(rest)) => {
    #             let mut path_props = rest.as_str().split_whitespace();
    #             let file_arg = path_props.next();
    #             let props: Vec<&str> = path_props.collect();

    #             match (typ.as_str(), file_arg) {
    #                 ("include", Some(pth)) => Some(parse_include_path(pth)),
    #                 ("playpen", Some(pth)) => Some(LinkType::Playpen(pth.into(), props)),
    #                 _ => None,
    #             }
    #         }
    #         (Some(mat), None, None) if mat.as_str().starts_with(ESCAPE_CHAR) => {
    #             Some(LinkType::Escaped)
    #         }
    #         _ => None,
    #     };

    #     link_type.and_then(|lnk| {
    #         cap.get(0).map(|mat| Link {
    #             start_index: mat.start(),
    #             end_index: mat.end(),
    #             link: lnk,
    #             link_text: mat.as_str(),
    #         })
    #     })
    # }

    def __eq__(self, other):
        if (self.start_index == other.start_index and
            self.end_index == other.end_index and
            self.include == other.include and
            self.include_text == other.include_text):
            return True
        return False

    def __repr__(self):
        return ('IncludeItem(start_index={start_index}, end_index={end_index}, '
            'include={include}, include_text={include_text})').format(
            start_index=self.start_index, end_index=self.end_index,
            include=repr(self.include), include_text=repr(self.include_text))


class EscapedInclude(IncludeType):

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return True
        return False


class IncludeRange(IncludeType):

    def __init__(self, path, select_range=None):
        self.path = path
        self.select_range = select_range
    
    def __eq__(self, other):
        if (self.__class__ == other.__class__ and
            self.path == other.path and
            self.select_range == other.select_range):
            return True
        return False
    
    def __repr__(self):
        return 'IncludeRange(path={path}, select_range={select_range})'.format(
            path=repr(self.path), select_range=repr(self.select_range))


class Playpen(IncludeType):

    def __init__(self, path):
        self.path = path
    
    def __eq__(self, other):
        if (self.__class__ == other.__class__ and
            self.path == other.path):
            return True
        return False

    def __repr__(self):
        return 'Playpen(path={path})'.format(path=repr(self.path))


# enum LinkType<'a> {
# Escaped,
# IncludeRange(PathBuf, Range<usize>),
# IncludeRangeFrom(PathBuf, RangeFrom<usize>),
# IncludeRangeTo(PathBuf, RangeTo<usize>),
# IncludeRangeFull(PathBuf, RangeFull),
# Playpen(PathBuf, Vec<&'a str>),
# }

# impl<'a> LinkType<'a> {
# fn relative_path<P: AsRef<Path>>(self, base: P) -> Option<PathBuf> {
#     let base = base.as_ref();
#     match self {
#         LinkType::Escaped => None,
#         LinkType::IncludeRange(p, _) => Some(return_relative_path(base, &p)),
#         LinkType::IncludeRangeFrom(p, _) => Some(return_relative_path(base, &p)),
#         LinkType::IncludeRangeTo(p, _) => Some(return_relative_path(base, &p)),
#         LinkType::IncludeRangeFull(p, _) => Some(return_relative_path(base, &p)),
#         LinkType::Playpen(p, _) => Some(return_relative_path(base, &p)),
#     }
# }
# }


class IncludePreprocessor(Preprocessor):
    """A preprocessor for expanding inclusion helpers in a chapter.

    The include preprocessor supports multiple different type of inclusion
    blocks, those are the Playpen block: ``{{# playpen ... }}``, the 
    Handlebars style include: ``{{# include ... }}``, and the Gitbook style
    include: ``{% include}``.
    """
    _name = 'include'

    def run(self, book):
        #: 1. Get the book source directory
        #: 
        pass
    # fn run(&self, ctx: &PreprocessorContext, mut book: Book) -> Result<Book> {
    #     let src_dir = ctx.root.join(&ctx.config.book.src);

    #     book.for_each_mut(|section: &mut BookItem| {
    #         if let BookItem::Chapter(ref mut ch) = *section {
    #             let base = ch
    #                 .path
    #                 .parent()
    #                 .map(|dir| src_dir.join(dir))
    #                 .expect("All book items have a parent");

    #             let content = replace_all(&ch.content, base, &ch.path, 0);
    #             ch.content = content;
    #         }
    #     });

    #     Ok(book)
    # }


# use super::{Preprocessor, PreprocessorContext};
# use book::{Book, BookItem};

# const ESCAPE_CHAR: char = '\\';




# }

# fn replace_all<P1, P2>(s: &str, path: P1, source: P2, depth: usize) -> String
# where
# P1: AsRef<Path>,
# P2: AsRef<Path>,
# {
# // When replacing one thing in a string by something with a different length,
# // the indices after that will not correspond,
# // we therefore have to store the difference to correct this
# let path = path.as_ref();
# let source = source.as_ref();
# let mut previous_end_index = 0;
# let mut replaced = String::new();

# for playpen in find_links(s) {
#     replaced.push_str(&s[previous_end_index..playpen.start_index]);

#     match playpen.render_with_path(&path) {
#         Ok(new_content) => {
#             if depth < MAX_LINK_NESTED_DEPTH {
#                 if let Some(rel_path) = playpen.link.relative_path(path) {
#                     replaced.push_str(&replace_all(&new_content, rel_path, source, depth + 1));
#                 } else {
#                     replaced.push_str(&new_content);
#                 }
#             } else {
#                 error!(
#                     "Stack depth exceeded in {}. Check for cyclic includes",
#                     source.display()
#                 );
#             }
#             previous_end_index = playpen.end_index;
#         }
#         Err(e) => {
#             error!("Error updating \"{}\", {}", playpen.link_text, e);
#             for cause in e.iter().skip(1) {
#                 warn!("Caused By: {}", cause);
#             }

#             // This should make sure we include the raw `{{# ... }}` snippet
#             // in the page content if there are any errors.
#             previous_end_index = playpen.start_index;
#         }
#     }
# }

# replaced.push_str(&s[previous_end_index..]);
# replaced
# }

# fn return_relative_path<P: AsRef<Path>>(base: P, relative: P) -> PathBuf {
# base.as_ref()
#     .join(relative)
#     .parent()
#     .expect("Included file should not be /")
#     .to_path_buf()
# }

# fn parse_include_path(path: &str) -> LinkType<'static> {
# let mut parts = path.split(':');
# let path = parts.next().unwrap().into();
# // subtract 1 since line numbers usually begin with 1
# let start = parts
#     .next()
#     .and_then(|s| s.parse::<usize>().ok())
#     .map(|val| val.saturating_sub(1));
# let end = parts.next();
# let has_end = end.is_some();
# let end = end.and_then(|s| s.parse::<usize>().ok());
# match start {
#     Some(start) => match end {
#         Some(end) => LinkType::IncludeRange(path, Range { start, end }),
#         None => if has_end {
#             LinkType::IncludeRangeFrom(path, RangeFrom { start })
#         } else {
#             LinkType::IncludeRange(
#                 path,
#                 Range {
#                     start,
#                     end: start + 1,
#                 },
#             )
#         },
#     },
#     None => match end {
#         Some(end) => LinkType::IncludeRangeTo(path, RangeTo { end }),
#         None => LinkType::IncludeRangeFull(path, RangeFull),
#     },
# }
# }


# fn render_with_path<P: AsRef<Path>>(&self, base: P) -> Result<String> {
#     let base = base.as_ref();
#     match self.link {
#         // omit the escape char
#         LinkType::Escaped => Ok((&self.link_text[1..]).to_owned()),
#         LinkType::IncludeRange(ref pat, ref range) => {
#             let target = base.join(pat);

#             file_to_string(&target)
#                 .map(|s| take_lines(&s, range.clone()))
#                 .chain_err(|| {
#                     format!(
#                         "Could not read file for link {} ({})",
#                         self.link_text,
#                         target.display(),
#                     )
#                 })
#         }
#         LinkType::IncludeRangeFrom(ref pat, ref range) => {
#             let target = base.join(pat);

#             file_to_string(&target)
#                 .map(|s| take_lines(&s, range.clone()))
#                 .chain_err(|| {
#                     format!(
#                         "Could not read file for link {} ({})",
#                         self.link_text,
#                         target.display(),
#                     )
#                 })
#         }
#         LinkType::IncludeRangeTo(ref pat, ref range) => {
#             let target = base.join(pat);

#             file_to_string(&target)
#                 .map(|s| take_lines(&s, *range))
#                 .chain_err(|| {
#                     format!(
#                         "Could not read file for link {} ({})",
#                         self.link_text,
#                         target.display(),
#                     )
#                 })
#         }
#         LinkType::IncludeRangeFull(ref pat, _) => {
#             let target = base.join(pat);

#             file_to_string(&target).chain_err(|| {
#                 format!(
#                     "Could not read file for link {} ({})",
#                     self.link_text,
#                     target.display()
#                 )
#             })
#         }
#         LinkType::Playpen(ref pat, ref attrs) => {
#             let target = base.join(pat);

#             let contents = file_to_string(&target).chain_err(|| {
#                 format!(
#                     "Could not read file for link {} ({})",
#                     self.link_text,
#                     target.display()
#                 )
#             })?;
#             let ftype = if !attrs.is_empty() { "rust," } else { "rust" };
#             Ok(format!(
#                 "```{}{}\n{}\n```\n",
#                 ftype,
#                 attrs.join(","),
#                 contents
#             ))
#         }
#     }
# }
# }