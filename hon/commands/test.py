import click
from ..cli import with_context

@click.command('test')
@with_context
def test_command(ctx=None):
    pass