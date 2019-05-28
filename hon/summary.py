"""
    hon.summary
    ~~~~~
"""
import logging
from hon.exc import InvalidBookError
from hon.markdown import Markdown
from hon.parsers.summary_parser import SummaryParser
from hon.structure import Link, Summary, parse_structure_file
from hon.utils.mdutils import flatten_tree
from hon.utils import xmlutils

#: TODO: Pull this from an app instance?
logger = logging.getLogger('hon')


def parse_summary(book):
    """Parse the text to create a ``Summary`` object.
    
    The ``text``, read from a ``SUMMARY.md`` file, is parsed into a ``Summary``
    object, which acts as a sort of "recipe" to be used when loading a book's
    contents from disk. It represents the structure of the book, in-so-far as
    how the chapters will be compiled and in what order.

    Summary Format
    --------------

    The format of the ``SUMMARY.md`` might contain the following elements:

    - **Title:** It's common practice to begin with a title, e.g. ``# Summary``.
      It's not mandatory and the parser (currently) ignores it, so you can too
      if you feel like it.
    - **Prefix Chapters:** Before the main numbered chapters you can add one or
      more chapter elements that will not be numbered.
      
      This is useful for forewords, introductions, etc. There are however some
      constraints: (1) You can not nest prefix chapters, they should all be on
      the root level, and (2) you can not add prefix chapters once you have
      added numbered chapters.::

        [Title of prefix element](relative/path/to/markdown.md)

    - **Numbered Chapter:** Numbered chapters are the main content of the book,
      they will be numbered and can be nested, resulting in a nice hierarchy
      (chapters, sub-chapters, etc.).::

        - [Title of the Chapter](relative/path/to/markdown.md)

      You can either use - or * to indicate a numbered chapter, the parser
      doesn't care but you'll probably want to stay consistent.

    - **Suffix Chapter:** After the numbered chapters you can add a couple of
      non-numbered chapters. They are the same as prefix chapters but come after
      the numbered chapters instead of before.

    All other elements are unsupported and will be ignored at best, or result in
    an error at worst.

    Summary Example
    ---------------

    ::

      # Table of Contents

      [Introduction](./indtroduction.md)

      [Preface](./preface.md)

      - [Chapter 1](./chapter1.md)
      - [Chapter 2](./chapter2.md)
      - [Chapter 3](./chapter3.md)
      - [Chapter 4](./chapter4.md)

      [Appendix A](./appendix-a.md)

      [Appendix B](./appendix-b.md)
    """
    if not book:
        raise InvalidBookError('Unable to parse summary for unknown book.')

    summary = None

    app = book.app
    summary_file = parse_structure_file(book, 'summary')
    if not summary_file:
        app.logger.warn('no summary file in this book')
        summary = Summary()
    else:
        app.logger.debug('summary file found at: {}'.format(summary_file))
        with open(summary_file) as f:
            summary_content = f.read()
            if not summary_content:
              summary = Summary()
            else:
              parser = SummaryParser(app, summary_content, book=book)
              summary = parser.parse()
    
    # Insert README as first entry if not in SUMMARY.md
    # var readmeArticle = summary.getByPath(readmeFile.getPath());

    # if (readmeFile.exists() && !readmeArticle) {
    #     summary = SummaryModifier.unshiftArticle(summary, {
    #         title: 'Introduction',
    #         ref: readmeFile.getPath()
    #     });
    # }
    book.summary = summary
    return summary
