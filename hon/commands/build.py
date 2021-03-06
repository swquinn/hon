"""
    hon.commands.build
    ~~~~~

    hon serve [OPTIONS] [BOOK] [OUTPUT]

    [BOOK]

    TBW

    [OUTPUT]

    The ``output`` argument is the directory that the book will be written into
    following generation. Relative paths are interpreted relative to the book's
    root directory. If omitted, hon will use the build.build-dir from .honrc or
    default to ./book.
"""
import click
import logging
import os
from functools import update_wrapper

from hon import current_app
from ..cli import with_context, ScriptInfo

logging.disable()


class BuildCommand(click.Command):
    """Custom Click Command for the build command.

    The build command relies on knowing about which renderers have been
    configured for the system. In order to get this information in the help, as
    well as expose it to the actual command when it is run, we needed to create
    a custom Command object and modify the params that are returned.
    """
    def get_params(self, ctx):
        rv = self.params
        with ctx.ensure_object(ScriptInfo).load_app().app_context():
            renderers = current_app.renderers
            rendering_options = []
            for r in renderers:
                rendering_options.append(r.get_build_render_option())
            rv = rv + rendering_options
        help_option = self.get_help_option(ctx)
        if help_option is not None:
            rv = rv + [help_option]
        return rv


@click.command('build', help="""
Builds a book.

The book is built using one or more of the configured renderers.
""", short_help='Builds a book from its markdown files', cls=BuildCommand)
@click.argument('book', default=None, required=False)
@click.argument('output', default=None, required=False)
@with_context
def build_command(book, output, **kwargs):
    """
    """
    #: The enabled/disabled renderers for this run of the build command are
    #: stored on the state object (ScriptInfo) for easier access, so this
    #: command grabs it early. We could, theoretically, pull these same values
    #: from the ``kwargs`` dictionary, but its not as nicely organized. [SWQ]
    logging.disable(logging.NOTSET)
    ctx = click.get_current_context()
    state = ctx.ensure_object(ScriptInfo)

    if book is None:
        book = os.getcwd()

    book_abspath = os.path.abspath(book)
    if not os.path.isdir(book_abspath):
        raise FileNotFoundError(('Unable to find directory: {book_abspath}, '
            'does the directory exist?').format(book_abspath=book_abspath))

    build_only = []
    for renderer, enabled in state.build_renderers.items():
        if enabled:
            build_only = build_only + [renderer]

    current_app.load_books(source_path=book_abspath)
    current_app.build(
        build_only=tuple(build_only),
        output_path_override=output
    )
