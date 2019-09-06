# -*- coding: utf-8 -*-
"""
    hon.structure.parsing
    ~~~~~

"""

import os


def find_parsable_file(book, structure_filename):
    """Find and return the path of a parsable file.

    If structure file is not found under the path for a given book, simply
    return ``None``.
    """
    for path, dirs, filenames in os.walk(book.path):
        for f in filenames:
            if f == structure_filename:
                return os.path.join(path, f)
    return None


def lookup_structure_file(book, structure_type):
    """Lookup the structure file for a given type.

    Structure types and their corresponding filenames, e.g. ``summary`` and
    ``SUMMARY.md``, have the following default values:

    These structure files can be renamed by adding a ``structure:`` setting in
    the project's ``.honrc`` configuration file, e.g.

    structure:
        readme: README.md
        glossary: GLOSSARY.md
        summary: SUMMARY.md
    """
    app = book.app
    structure_config = app.config.get('structure')
    file_to_search = structure_config.get(structure_type)

    return find_parsable_file(book, file_to_search)


def parse_structure_file(book, structure_type):
    structure_file = lookup_structure_file(book, structure_type)

    #: TODO
    #: For future development. GitBook supported multiple types of parsers:
    #: ASCII Doc and Markdown. Theoretically more. Parsing a structure file,
    #: like SUMMARY.md, is dependent on the parser being used (e.g. Markdown).
    #:
    #: Currently, Hon only supports Markdown files so, parsing the structure
    #: file is going to be done in the parse call. This needs some more thought
    #: behind it, but that's for a later refactor.
    #:
    #: Thus, right now "parse_structure_file" will simply be a pass through for
    #: the lookup structure file function. [SWQ]
    return structure_file
