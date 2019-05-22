import click
import os

from hon import current_app
from ..cli import with_context

@click.command('build', short_help='Builds a book from its markdown files')
@click.argument('source_dir', default=None, required=False)
@click.option('--dest-dir', '-d', 'dest_dir', default='book',
    help=("Output directory for the book. Relative paths are interpreted "
        "relative to the book's root directory. If omitted, hon will use the "
        "build.build-dir from .honrc or default to ./book."))
@with_context
def build_command(source_dir, dest_dir):
    if source_dir is None:
        source_dir = os.getcwd()
    
    source_dir_abspath = os.path.abspath(source_dir)
    if not os.path.isdir(source_dir_abspath):
        raise FileNotFoundError(f'Unable to find directory: {source_dir_abspath}, does the directory exist?')

    current_app.load_books(source_path=source_dir_abspath)
    current_app.build()
