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
    def all_parts(self):
        parts = []
        parts.append(self.readme)
        for section in self.sections:
            parts.extend(section.parts)
        return parts

    def __init__(self, title=None, readme=None, sections=None):
        self.title = title
        self.readme = readme
        self.sections = sections or []
    
    def add_section(self, section):
        self.sections.append(section)
    
    def add_sections(self, sections):
        self.sections.extend(sections)
    
    def to_json(self):
        sections_json = []

        sections_json.append({
            'parts': [
                {
                    'articles': [self.readme.to_json()]
                }
            ]
        })

        for section in self.sections:
            sections_json.append(section.to_json())
        return { 'sections': sections_json }


class Section():
    """A section of the summary, which contains parts.
    """
    def __init__(self, title=None, parts=None):
        self.title = title
        self.parts = parts or []

    def __hash_key(self):
        return (self.title, self.parts)

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__hash_key() == other.__hash_key()

    def __repr__(self):
        return '<Section(title={title}), parts={parts}>'.format(
            title=repr(self.title), parts=repr(self.parts))

    def add_part(self, part):
        self.parts.append(part)
    
    def add_parts(self, parts):
        self.parts.extend(parts)
    
    def to_json(self):
        parts_json = []
        for part in self.parts:
            parts_json.append(part.to_json())
        return { 'title': self.title, 'parts': parts_json }


class Part():

    @property
    def id(self):
        root, _ = os.path.splitext(self.source)
        return slugify(root)
    
    @property
    def link(self):
        root, _ = os.path.splitext(self.source)
        return '{}.html'.format(root)

    @property
    def link_name(self):
        root, _ = os.path.splitext(self.source)
        return root

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

    def __hash_key(self):
        return (self.name, self.source, self.level, self.children)

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__hash_key() == other.__hash_key()

    def __repr__(self):
        return ('<Part(name={name}, source={source}, level={level})>'.format(
            name=repr(self.name), source=repr(self.source),
            level=repr(self.level)))
    
    def add_child(self, child):
        self.children.append(child)
    
    def add_children(self, children):
        self.children.extend(children)

    def to_json(self):
        part_json = { 'name': self.name, 'source': self.source, 'level': self.level, 'children': [] }
        for part in self.children:
            part_json['children'].append(part.to_json())
        return part_json
