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
    def __init__(self, title=None, readme=None, prefix_parts=None, numbered_parts=None, suffix_parts=None):
        self.title = title
        self.readme = readme
        self.prefix_parts = prefix_parts or []
        self.numbered_parts = numbered_parts or []
        self.suffix_parts = suffix_parts or []