"""
    hon.parsers.summary_parser
    ~~~~~
"""
import os

from hon.parsing import MarkdownParser
from hon.structure import Part, Section, Summary
from hon.utils import xmlutils


def stringify_events(element):
    """Removes the styling from a list of Markdown events and returns just the
    plain text.
    """
    return ''.join(element.itertext()).strip()


class SummaryParser():
    """A recursive descent (-ish) parser for a `SUMMARY.md`.
   
   
    # Grammar
   
    The `SUMMARY.md` file has a grammar which looks something like this:
   
    ```text
    summary           ::= title prefix_chapters numbered_chapters suffix_chapters
    title             ::= "# " TEXT
                        | EPSILON
    prefix_chapters   ::= item*
    suffix_chapters   ::= item*
    numbered_chapters ::= dotted_item+
    dotted_item       ::= INDENT* DOT_POINT item
    item              ::= link
                        | separator
    separator         ::= "---"
    link              ::= "[" TEXT "]" "(" TEXT ")"
    DOT_POINT         ::= "-"
                        | "*"
    ```
   
    > **Note:** the `TEXT` terminal is "normal" text, and should (roughly)
    > match the following regex: "[^<>\n[]]+".
    """
    def __init__(self, app=None, src=None, book=None):
        self.app = app
        self.book = book
        self.src = src
        self.stream = MarkdownParser()
        self.stream.parse(self.src or '')

    def parse(self):
        """Parse the text the `SummaryParser` was created with."""
        title = self.parse_title()

        readme = self.parse_readme()
        glossary = self.parse_glossary()
        sections = self.parse_sections()

        return Summary(title=title, readme=readme, sections=sections)

    def parse_glossary(self):
        return None

    def parse_readme(self):
        readme_file = os.path.join(self.book.path, 'README.md')
        if not os.path.exists(readme_file):
            raise FileNotFoundError('README.md not found.')
        return Part('README', source=os.path.relpath(readme_file, self.book.path))

    def parse_sections(self):
        sections = []

        section_heading_tags = ['h2', 'h3', 'h4', 'h5', 'h6', 'hr']
        section_body_tags = ['ul', 'ol', 'p', 'a']

        tags = tuple(section_heading_tags + section_body_tags)
        events = xmlutils.find_elements_by_tag(self.stream.parse_tree, tag_names=tags, max_depth=1)

        for e in events:
            if e.tag in section_heading_tags:
                title = None
                if e.tag in ('h2', 'h3', 'h4', 'h5', 'h6'):
                    title = stringify_events(e)
                section = Section(title=title)
                sections.append(section)
            elif e.tag == 'ul' or e.tag == 'ol':
                if not sections:
                    section = Section()
                    sections.append(section)
                parts = self.parse_parts(e)
                sections[-1].add_parts(parts)
            elif e.tag == 'p':
                if not sections:
                    section = Section()
                    sections.append(section)
                parts = self.parse_parts(e)
                sections[-1].add_parts(parts)
        return sections
    
    def parse_parts(self, parent, level=0):
        self.app.logger.debug(f'(LEVEL {level}) Parsing parts for: {parent}')
        parts = []

        for e in list(parent):
            if e.tag == 'a':
                part = self.create_part(e)
                parts.append(part)
            elif e.tag == 'li':
                part = self.parse_part(e, level=level)
                if part:
                    self.app.logger.debug(f'(LEVEL {level}) Adding part link: {part}')
                    parts.append(part)
            else:
                if len(parts) < 1:
                    raise IndexError('Encountered nested list before any parts were parsed')
                bunch_of_parts = self.parse_parts(e, level=level+1 if level else None)
                parts[-1].extend(bunch_of_parts)
        return parts

    def parse_part(self, list_item, level=0):
        self.app.logger.debug(f'(LEVEL {level}) Parsing part from : {list_item}')

        part = None
        link_element = xmlutils.find_first_element_by_tag(list_item, 'a', skip=['ul', 'ol'])
        if link_element is not None:
            self.app.logger.debug(f'(LEVEL {level}) Found chapter link: {link_element} for: {link_element.text}')
            part = self.create_part(link_element, level=level)

        if part:
            children = []
            subparts = xmlutils.find_elements_by_tag(list_item, tag_names=('ul', 'ol'), max_depth=1)
            for e in list(subparts):
                if e.tag in ('ul', 'ol'):
                    children = self.parse_parts(e, level=level+1)
            part.children = children
        return part

    def create_part(self, element, level=None):
        href = element.get('href')
        if not href:
            raise ValueError("You can't have an empty link.")
        return Part(name=element.text, source=href, level=level)

    def parse_title(self):
        """Try to parse the title line."""
        if self.stream.parse_tree:
            title_tag = self.stream.parse_tree.find('h1')
            return stringify_events(title_tag)
        return ''


class SummaryItem():
    """An item in `SUMMARY.md` which could be either a separator or a ``Link``."""

    #: A separator (`---`).
    SEPARATOR = 'Separator'


class SummaryItemSeparator(SummaryItem):
    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return True
        return False

    def __repr__(self):
        return 'SummaryItemSeparator()'


class SectionNumber():
    """A section number like "1.2.3", basically just a newtype'd `Vec<u32>` with
    a pretty `Display` impl."""
    def __init__(self, vector):
        self.vector = vector

    def __str__(self):
        if not self.vector:
            return '0'
        else:
            s = ''
            for item in self.vector:
                s += '{}.'.format(item)
            return s
    
    # impl Deref for SectionNumber {
    #     type Target = Vec<u32>;
    #     fn deref(&self) -> &Self::Target {
    #         &self.0
    #     }
    # }

    # impl DerefMut for SectionNumber {
    #     fn deref_mut(&mut self) -> &mut Self::Target {
    #         &mut self.0
    #     }
    # }

    # impl FromIterator<u32> for SectionNumber {
    #     fn from_iter<I: IntoIterator<Item = u32>>(it: I) -> Self {
    #         SectionNumber(it.into_iter().collect())
    #     }
    # }
    def __repr__(self):
        return 'SectionNumber({})'.format(repr(self.vector))