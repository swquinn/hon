"""
    hon.structure.summary
    ~~~~~
"""
import os
from pydash.strings import slugify


class Summary():
    """The parsed ``SUMMARY.md`` indicating the structure of the book.
    
    The ``Summary`` represents the structure of the book, and how the book
    should be laid out. It is the table of contents and the book's navigation.

    :type str: title
    :type prefix_parts: list
    :type numbered_parts: list
    :type suffix_parts: list
    """

    @property
    def legacy_parts(self):
        readme = tuple([self.readme])
        prefix = tuple(self.prefix_parts)
        numbered = tuple(self.numbered_parts)
        suffix = tuple(self.suffix_parts)
        return readme + prefix + numbered + suffix

    def __init__(self, title=None, readme=None, prefix_parts=None, numbered_parts=None, suffix_parts=None, sections=None):
        self.title = title
        self.readme = readme
        self.prefix_parts = prefix_parts or []
        self.numbered_parts = numbered_parts or []
        self.suffix_parts = suffix_parts or []

        self.sections = sections or []
    
    def add_section(self, section):
        self.sections.append(section)
    
    def add_sections(self, sections):
        self.sections.extend(sections)
    
    def to_json(self):
        parts_json = []

        parts_json.append({
            'articles': [self.readme.to_json()]
        })

        prefix_part = { 'articles': [] }
        for part in self.prefix_parts:
            prefix_part['articles'].append(part.to_json())
        parts_json.append(prefix_part)

        numbered_part = { 'articles': [] }
        for part in self.numbered_parts:
            numbered_part['articles'].append(part.to_json())
        parts_json.append(numbered_part)

        suffix_part = { 'articles': [] }
        for part in self.suffix_parts:
            suffix_part['articles'].append(part.to_json())
        parts_json.append(suffix_part)

        return { 'parts': parts_json }


class Section():
    """A section of the summary, which contains parts.
    """
    def __init__(self, title=None, parts=None):
        self.title = title
        self.parts = parts or []

    def add_part(self, part):
        self.parts.append(part)
    
    def add_parts(self, parts):
        self.parts.extend(parts)


class Part():

    @property
    def id(self):
        root, _ = os.path.splitext(self.source)
        return slugify(root)
    
    @property
    def link(self):
        return None

    def __init__(self, name, source=None, level=None, children=None):
        #: The name of the part.
        self.name = name

        #: The part's source file, or if an external link the URL.
        self.source = source

        #: The part's level; not all parts are in a hierarchy. If the part is
        #: within a hierarchy of parts, this is an integer value, starting at 0.
        #: Every child of the part has a level one greater than its parent.
        self.level = level

        #: Any nested items this part contains.
        self.children = children or []

    def __eq__(self, other):
        if (self.name == other.name and
            self.source == other.source and
            self.level == other.level and
            self.children == other.children):
            return True
        return False

    def __repr__(self):
        return ('<Part(name={name}, source={source}, level={level})>'.format(
            name=repr(self.name), source=repr(self.source),
            level=repr(self.level)))
    
    def add_child(self, child):
        self.children.append(child)
    
    def add_children(self, children):
        self.children.extend(children)
