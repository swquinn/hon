"""
    hon.server.middleware
    ~~~~~
"""
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class _FlaskHonStateMixin(object):
    """A mixin for the FlaskHon middleware."""

    def shutdown(self):
        """Shutdown the middleware.

        As part of the shutdown process, this attempts to join the observer
        thread back to the main thread. If the observer thread hasn't been
        started it might error out, but this OK. We can safely ignore that
        error. If ``flask.Flask.debug`` is ``True``, we will render the
        exception, otherwise we supress the error message.
        """
        try:
            self.observer.join()
        except RuntimeError:
            if self.flask_hon.app.debug:
                self.flask_hon.app.logger.exception('A runtime exception '
                    'occurred when trying to join the file system observer '
                    'in the Flask-Hon middleware back to the main thread.')


class _FlaskHonState(_FlaskHonStateMixin):
    """A stateful representation of the configured file system watcher."""

    @property
    def observer(self):
        return self.flask_hon.observer

    def __init__(self, flask_hon):
        self.flask_hon = flask_hon


class FlaskHon(_FlaskHonStateMixin):
    """This class manages the integration between Hon and Flask.

    When serving a :class:`~hon.Hon` application directly from your local
    environment for development, it is sometimes helpful to have access to a
    number of features. Among the features that the Flask-Hon middleware
    exposes is a watch-mode for a book's content.

    Watchmode for a Hon book can be enabled, and is enabled by default. If
    ``enable_watch`` is ``True`` then before the first request is processed
    the event handler will be scheduled with the file system observer and
    the observer will be started.

    .. admonition:: Hon is required!

        This integration requires that the ``hon_app`` and ``book_path``
        arguments be passed. Otherwise any feature that relies on the current
        Hon application will fail. Although these arguments are defined as
        keyword arguments with default values of ``None``, instantiating the
        extension without them will trigger errors.

    :type app: flask.Flask
    :type book_path: str
    :type enable_watch: bool
    :type event_handler: watchdog.events.FileSystemEventHandler
    :type hon_app: hon.Hon
    :type observer: watchdog.observers.Observer
    """

    def __init__(self, app=None, hon_app=None, book_path=None, enable_watch=True):
        if hon_app is None:
            raise ValueError('FlaskHon requires an instance of the Hon '
                'application. Please ensure that the ``hon_app`` keyword '
                'argument was specified and set to the Hon application.')

        if not book_path:
            raise ValueError('FlaskHon requires a path to a book\'s source '
                'files. Please ensure that the ``book_path`` keyword argument '
                'is specified and points to the directory where the book '
                'content is located.')

        #: On any file system event, trigger a build.
        def _on_fs_event():
            self.build()

        #: A custom file system event handler that operates on any event. This
        #: class will be instantiated and assigned to the ``event_handler``
        #: instance. It passes any file system event to the ``_on_fs_event``
        #: function. [SWQ]
        class _CustomHandler(FileSystemEventHandler):
            def on_any_event(self, event):
                _on_fs_event()

        self.app = app
        self.hon_app = hon_app
        self.book_path = book_path
        self.enable_watch = enable_watch
        self.observer = Observer()
        self.event_handler = _CustomHandler()

        if app is not None:
            self.init_app(app)

    def build(self):
        self.app.logger.debug('Detected changes in book on path: {}. Rebuilding...'.format(self.book_path))

        self.hon_app.load_books(source_path=self.book_path)
        self.hon_app.build()

    def init_app(self, app):
        app.logger.debug('Initializing Hon for Flask application: {}'.format(app))

        if self.enable_watch:
            self.init_watch(app)

        app.extensions['hon'] = _FlaskHonState(self)

    def init_watch(self, app):
        """Initializes Flask-Hon's file system watch mode.

        If the ``FlaskHon`` middleware was registered to the Flask application
        with watch-mode enabled, then we also need to setup a hook with Flask
        to start the file system observer. The observer itself was instantiated
        earlier, and is instance of :class:`~watchdog.observers.Observer`. The
        observer will only be started _before_ the first request.

        :param app: The :class:`~flask.Flask` application.
        :type app: flask.Flask
        """
        @app.before_first_request
        def start_watchmode():
            self.app.logger.debug('Watching book content for changes')
            self.observer.schedule(self.event_handler, self.book_path, recursive=True)
            self.observer.start()
