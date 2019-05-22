import click
from ..cli import with_context

@click.command('watch')
@with_context
def watch_command(ctx=None):
    pass
