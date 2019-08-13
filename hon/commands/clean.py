import click
from ..cli import with_context

@click.command('clean', short_help="Cleans a book' output directories")
@with_context
def clean_command(ctx=None):
    pass