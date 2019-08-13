import click
from ..cli import with_context

@click.command('watch', short_help='Watch the book source for changes and rebuild')
@with_context
def watch_command(ctx=None):
    pass
