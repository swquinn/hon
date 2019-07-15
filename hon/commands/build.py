"""
    hon.commands.build
    ~~~~~

    hon serve [OPTIONS] [BOOK] [OUTPUT]

    [BOOK]

    TBW

    [OUTPUT]

    The ``output`` argument is the directory that the book will be written into
    following generation. Relative paths are interpreted relative to the book's
    root directory. If omitted, hon will use the build.build-dir from .honrc or
    default to ./book.
"""
import click
import os

from hon import current_app
from ..cli import with_context

@click.command('build', short_help='Builds a book from its markdown files')
@click.argument('book', default=None, required=False)
@click.argument('output', default='book', required=False)
@with_context
def build_command(book, output):
    if book is None:
        book = os.getcwd()
    
    book_abspath = os.path.abspath(book)
    if not os.path.isdir(book_abspath):
        raise FileNotFoundError(f'Unable to find directory: {book_abspath}, does the directory exist?')

    print(current_app.config)
    print()
    current_app.load_books(source_path=book_abspath)
    #current_app.build(build_only=('epub', ))
    current_app.build(output_path_override=output)
