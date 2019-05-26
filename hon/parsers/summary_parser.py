"""
    hon.parsers.summary_parser
    ~~~~~
"""
from hon.markdown import Markdown
from hon.structure import Link, Summary
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
    def __init__(self, app=None, src=None):
        self.app = app
        self.src = src
        self.stream = Markdown()
        self.stream.convert(self.src or '')
        print(self.stream)

    def parse(self):
        """Parse the text the `SummaryParser` was created with."""
        title = self.parse_title()

        prefix_chapters = self.parse_affix(is_prefix=True)
        #     .chain_err(|| "There was an error parsing the prefix chapters")?;

        numbered_chapters = self.parse_numbered()
        #     .chain_err(|| "There was an error parsing the numbered chapters")?;

        suffix_chapters = self.parse_affix(is_prefix=False)
        #     .chain_err(|| "There was an error parsing the suffix chapters")?;

        return Summary(title=title, prefix_parts=prefix_chapters,
            numbered_parts=numbered_chapters, suffix_parts=suffix_chapters)

    def parse_affix(self, is_prefix=False):
        """Parse chapters outside of a list.

        Parse the affix chapters. This expects the first event (start of
        paragraph) to have already been consumed by the previous parser.
        """
        items = []
        affix_type = "prefix" if is_prefix else "suffix"
        self.app.logger.debug("Parsing {} items".format(affix_type))

        events = self.stream.elements if is_prefix else self.stream.reverse_elements
        print("{}".format(list(events)))
        for e in events.iter():
            if e.tag == 'a':
                link = self.parse_link(e)
                items.append(link)
            elif e.tag == 'hr':
                sep = SummaryItemSeparator()
                items.append(sep)
            elif e.tag == 'ul' or e.tag == 'ol':
                # if not is_prefix and len(items) < 1:
                #     raise ValueError('Lists cannot come after suffix elements.')
                break
        if not is_prefix:
            items.reverse()
        
        if not items:
            self.app.logger.debug('No {} items found.'.format(affix_type))
        return items

    def parse_link(self, element, level=None):
        href = element.get('href')
        if not href:
            raise ValueError("You can't have an empty link.")
        return Link(name=element.text, source=href, level=level)


    def parse_numbered(self):
        """
        Parse the numbered chapters. This assumes the opening list tag has
        already been consumed by a previous parser.
        """
        self.app.logger.debug('[START] Begin parsing structured chapters')
        items = []
        root_items = 0

        events = xmlutils.find_elements_by_tag(self.stream.elements, tag_names=['ul', 'ol', 'hr', 'p'], max_depth=1)
        print(events)
        for e in events:
            if e.tag == 'ul' or e.tag == 'ol':
                bunch_of_items = self.parse_chapters(e)
                root_items += len(bunch_of_items)
                items.extend(bunch_of_items)
            elif e.tag == 'p':
                break
            elif e.tag == 'hr':
                self.app.logger.debug(f'Adding separator between lists')
                items.append(SummaryItemSeparator())
        self.app.logger.debug('[END] Finished parsing structured chapters')
        return items

    def parse_chapters(self, parent, level=0):
        self.app.logger.debug(f'(LEVEL {level}) Parsing chapters for: {parent}')
        items = []

        for e in list(parent):
            if e.tag == 'li':
                print('Parsing list item: {}'.format(e))
                item = self.parse_chapter_link_from_list_item(e, level=level)
                if item:
                    self.app.logger.debug(f'(LEVEL {level}) Adding chapter link: {item}')
                    items.append(item)
            elif e.tag == 'ul' or e.tag == 'ol':
                if len(items) < 1:
                    raise IndexError('Encountered nested list before any links were parsed')
                bunch_of_items = self.parse_chapters(e, level=level+1)
                items[-1].extend(bunch_of_items)
            elif e.tag == 'hr':
                self.app.logger.debug(f'(LEVEL {level}) Adding summary item separator')
                items.append(SummaryItemSeparator())
        return items

    def parse_chapter_link_from_list_item(self, list_item, level=0):
        self.app.logger.debug(f'(LEVEL {level}) Parsing chapter link from : {list_item}')

        chapter_link = None
        link_element = xmlutils.find_first_element_by_tag(list_item, 'a', skip=['ul', 'ol'])
        if link_element is not None:
            self.app.logger.debug(f'(LEVEL {level}) Found chapter link: {link_element} for: {link_element.text}')
            chapter_link = self.parse_link(link_element, level=level)

        for e in list(list_item):
            if e.tag == 'ul' or e.tag == 'ol':
                if chapter_link is None: 
                    raise TypeError('Unable to append sublinks to an undefined link.')

                children = self.parse_chapters(e, level=level + 1)
                chapter_link.children = children
        return chapter_link

    def parse_title(self):
        """Try to parse the title line."""
        if self.stream.parse_tree:
            title_tag = self.stream.parse_tree.find('h1')
            return stringify_events(title_tag)
        return ''


class SummaryItem():
    """An item in `SUMMARY.md` which could be either a separator or a ``Link``."""
    #: A link to a chapter.
    LINK = 'Link'

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