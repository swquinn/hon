import click
from ..cli import with_context

@click.command('test', short_help='Run a suite of tests to validate the correctness of a book')
@with_context
def test_command(ctx=None):
    pass