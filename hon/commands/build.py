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
@click.argument('output', default=None, required=False)
@click.option('--epub/--no-epub', 'include_epub', is_flag=True, default=True)
@click.option('--html/--no-html', 'include_html', is_flag=True, default=True)
@click.option('--pdf/--no-pdf', 'include_pdf', is_flag=True, default=True)
@with_context
def build_command(book, output, include_epub=True, include_html=True, include_pdf=True):
    if book is None:
        book = os.getcwd()
    
    book_abspath = os.path.abspath(book)
    if not os.path.isdir(book_abspath):
        raise FileNotFoundError(f'Unable to find directory: {book_abspath}, does the directory exist?')

    print(current_app.config)
    print()

    build_only = []
    if include_epub:
        build_only.append('epub')
    
    if include_html:
        build_only.append('html')

    if include_pdf:
        build_only.append('pdf')

    current_app.load_books(source_path=book_abspath)
    current_app.build(
        build_only=tuple(build_only),
        output_path_override=output
    )
