import click
from ..cli import with_context


@click.command('init', short_help='Initializes a new Hon project')
@with_context
def init_command(ctx=None):
    pass
