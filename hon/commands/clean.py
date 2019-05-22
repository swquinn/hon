import click
from ..cli import with_context

@click.command('clean')
@with_context
def clean_command(ctx=None):
    pass