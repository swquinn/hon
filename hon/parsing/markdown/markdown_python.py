"""
    hon.parsing.markdown.markdown
    ~~~~~
"""
from markdown import Markdown as MarkdownPython
from markdown import util
from xml.etree.ElementTree import Element, ElementTree

from ..parser import Parser


def _build_reverse(element, items):
    """Builds a shallow reverse representation of an element"""
    reversed_items = reversed(items)
    for item in reversed_items:
        element.append(item)
    return element


class _Markdown(MarkdownPython):
    @property
    def parse_tree(self):
        return self.elements

    @property
    def reverse_elements(self):
        """A shallow reverse representation of the Markdown tree."""
        items = list(self.elements)
        root = Element('div')
        _build_reverse(root, items)
        return root

    def __init__(self, **kwargs):
        super(_Markdown, self).__init__(**kwargs)
        self.elements = None

    def convert(self, source):
        """Convert markdown to serialized XHTML or HTML.

        This overrides the base Python Markdown ``convert`` function, to save
        off the element tree right before it is serialized to the XHTML or HTML
        output.

        Markdown processing takes place in five steps:

        1. A bunch of "preprocessors" munge the input text.
        2. BlockParser() parses the high-level structural elements of the
           pre-processed text into an ElementTree.
        3. A bunch of "treeprocessors" are run against the ElementTree. One
           such treeprocessor runs InlinePatterns against the ElementTree,
           detecting inline markup. After which the state of the parse tree is
           saved to the instance's ``parse_tree``.
        4. Some post-processors are run against the text after the ElementTree
           has been serialized into text.
        5. The output is written to a string.

        :param source: Source text as a Unicode string.
        """

        # Fixup the source text
        if not source.strip():
            return ''  # a blank unicode string

        try:
            source = util.text_type(source)
        except UnicodeDecodeError as e:  # pragma: no cover
            # Customise error message while maintaining original trackback
            e.reason += '. -- Note: Markdown only accepts unicode input!'
            raise

        # Split into lines and run the line preprocessors.
        self.lines = source.split("\n")
        for prep in self.preprocessors:
            self.lines = prep.run(self.lines)

        # Parse the high-level elements.
        root = self.parser.parseDocument(self.lines).getroot()

        # Run the tree-processors
        for treeprocessor in self.treeprocessors:
            newRoot = treeprocessor.run(root)
            if newRoot is not None:
                root = newRoot
        self.elements = root

        # Serialize _properly_.  Strip top-level tags.
        output = self.serializer(root)
        if self.stripTopLevelTags:
            try:
                start = output.index(
                    '<%s>' % self.doc_tag) + len(self.doc_tag) + 2
                end = output.rindex('</%s>' % self.doc_tag)
                output = output[start:end].strip()
            except ValueError:  # pragma: no cover
                if output.strip().endswith('<%s />' % self.doc_tag):
                    # We have an empty document
                    output = ''
                else:
                    # We have a serious problem
                    raise ValueError('Markdown failed to strip top-level '
                                     'tags. Document=%r' % output.strip())

        # Run the text post-processors
        for pp in self.postprocessors:
            output = pp.run(output)

        return output.strip()


class MarkdownParser(Parser):
    """A markdown parser implementing the Markdown-Python library.
    """

    def parse_front_matter(self):
        pass

    def parse(self, text):
        md = _Markdown()

        markedup_text = md.convert(text)
        self._parse_tree = md.parse_tree
        return markedup_text
