"""
    hon.structure.summary
    ~~~~~
"""

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
    def parts(self):
        readme = tuple([self.readme])
        prefix = tuple(self.prefix_parts)
        numbered = tuple(self.numbered_parts)
        suffix = tuple(self.suffix_parts)
        return readme + prefix + numbered + suffix

    def __init__(self, title=None, readme=None, prefix_parts=None, numbered_parts=None, suffix_parts=None):
        self.title = title
        self.readme = readme
        self.prefix_parts = prefix_parts or []
        self.numbered_parts = numbered_parts or []
        self.suffix_parts = suffix_parts or []
    
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
        