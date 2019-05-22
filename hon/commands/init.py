import click
from ..cli import with_context

@click.command('init')
@with_context
def init_command(ctx=None):
    pass