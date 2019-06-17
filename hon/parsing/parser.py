"""
    hon.parsing.parser
    ~~~~~

    Parsers provide a standard interface for converting a book's source
    to a target output, e.g. HTML, eBooks, and PDFs.
"""


class Parser(object):
    """

    :type parse_tree: []
    """

    @property
    def parse_tree(self):
        return self._parse_tree

    def __init__(self):
        self._parse_tree = None

    def parse(self, text):
        """Parse the given text.
        """
        raise NotImplementedError('Parsers must implement the parse method.')
