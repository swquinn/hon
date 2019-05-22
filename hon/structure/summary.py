"""
    hon.structure.summary
    ~~~~~
"""

class Summary():
    """The parsed ``SUMMARY.md``, specifying how the book should be laid out.
    """
    def __init__(self, title=None, prefix_parts=None, numbered_parts=None, suffix_parts=None):
        self.title = title
        self.prefix_parts = prefix_parts or []
        self.numbered_parts = numbered_parts or []
        self.suffix_parts = suffix_parts or []