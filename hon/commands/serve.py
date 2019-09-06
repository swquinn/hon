"""
    hon.commands.serve
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
import os
from flask import Flask, send_from_directory

from hon import _app_ctx_stack, current_app as hon_app
from ..cli import with_context
from ..server import FlaskHon


def build_book(book_path):
    hon_app.load_books(source_path=book_path)
    hon_app.build()


def create_flask_app(serve_from=None):
    """Create the Flask app that will be used to serve the book."""
    static_folder = None
    if serve_from:
        static_folder = os.path.abspath(os.path.join(serve_from, 'html'))
    app = Flask('hon', static_url_path='', static_folder=static_folder)

    @app.route('/<path:path>')
    def send_html(path):
        if not path:
            path = 'index.html'
        return send_from_directory('.', path)
    return app


@click.command('serve', short_help='Serve the book as a website for testing')
@click.argument('book', default=None, required=False)
@click.argument('output', default='book', required=False)
@click.option('--port', 'port', default='4000',
    help=("Port for server to listen on (Default is 4000)"))
@click.option('--watch/--no-watch', 'watch', default=True,
    help=("Enable file watcher and live reloading (Default is true)"))
@with_context
def serve_command(book, output, port, watch):
    if book is None:
        book = os.getcwd()

    #: Resolve the book's absolute path, which will be used when actually
    #: building the book. The absolute path is passed into the initial build
    #: process, but also when creating the file system observer.
    book_abspath = os.path.abspath(book)
    if not os.path.isdir(book_abspath):
        raise FileNotFoundError(f'Unable to find directory: {book_abspath}, does the directory exist?')

    build_book(book_abspath)

    flask_app = None
    try:
        flask_app = create_flask_app(serve_from=output)
        flask_hon = FlaskHon(flask_app, hon_app=hon_app._get_current_object(),
            book_path=book_abspath, enable_watch=watch)

        flask_app.run(debug=True, port=port)
    except KeyboardInterrupt:
        flask_app['hon'].observer.stop()
    finally:
        flask_app.extensions['hon'].shutdown()
