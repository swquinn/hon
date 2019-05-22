import click
from ..cli import with_context

@click.command('serve')
@with_context
def serve_command(ctx=None):
    pass