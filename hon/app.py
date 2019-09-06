# -*- coding: utf-8 -*-
"""
    hon.app
    ~~~~~~~

    This module implements the central Hon application.
"""
import os
import configparser
import sys
from collections import namedtuple
from datetime import datetime
from functools import update_wrapper
from operator import attrgetter

from .book import Book
from .config import (_read_yaml_config, BookConfig)
from .ctx import _AppCtxGlobals, AppContext
from .helpers import locked_cached_property
from .logging import create_logger
from .plugins import Plugin
from .signals import before_build, after_build

# a singleton sentinel value for parameter defaults
_sentinel = object()

#: The default output path to use, if one was not passed by the command line
#: interface, or otherwise specified in the configuration.
DEFAULT_OUTPUT_PATH = 'book'

#: A collection of valid book configuration files which, if present, identify
#: a directory as being the root of a book.
VALID_BOOK_CONFIGURATIONS = ['book.yaml']  # TODO: ['book.json', 'book.toml', 'book.yaml']


#:
BookPath = namedtuple('BookPath', ['name', 'config_file', 'config_filepath', 'filepath'])


def get_default_preprocessors():
    """Return the collection of default preprocessors."""
    import hon.preprocessors as p
    return (
        p.IndexPreprocessor,
        p.VariablesPreprocessor,
        p.JinjaPreprocessor,
    )


def get_default_renderers():
    """Return the collection of default renderers."""
    import hon.renderers as r
    return (
        r.HtmlRenderer,
        r.PdfRenderer,
        r.EpubRenderer,
    )


#: TODO: Reword assertion error
def setupmethod(f):
    """Wraps a method so that it performs a check in debug mode if the
    first request was already handled.
    """
    def wrapper_func(self, *args, **kwargs):
        if self.debug and self._got_first_request:
            raise AssertionError('A setup function was called after the '
                'first request was handled.  This usually indicates a bug '
                'in the application where a module was not imported '
                'and decorators or other functionality was called too late.\n'
                'To fix this make sure to import all your view modules, '
                'database models and everything related at a central place '
                'before the application starts serving requests.')
        return f(self, *args, **kwargs)
    return update_wrapper(wrapper_func, f)


class Hon():
    """

    :type plugins: list
    :type preprocessors: list
    :type renderers: list
    """
    #: The class that is used for the :data:`~hon.g` instance.
    #:
    #: Example use cases for a custom class:
    #:
    #: 1. Store arbitrary attributes on hon.g.
    #: 2. Add a property for lazy per-request database connectors.
    #: 3. Return None instead of AttributeError on unexpected attributes.
    #: 4. Raise exception if an unexpected attr is set, a "controlled" hon.g.
    app_ctx_globals_class = _AppCtxGlobals

    #: Default configuration parameters for the project.
    default_config = {
        'title': None,
        'description': None,
        'preprocessor': {},
        'output': {},
        'structure': {
            'readme': 'README.md',
            'glossary': 'GLOSSARY.md',
            'summary': 'SUMMARY.md'
        },
        'build': {
            'build-dir': 'book',
            'create-missing': True,
            'use-default-preprocessors': True,
        },
    }

    @locked_cached_property
    def logger(self):
        """The ``'hon'`` logger, a standard Python :class:`~logging.Logger`.

        In debug mode, the logger's :attr:`~logging.Logger.level` will be set
        to :data:`~logging.DEBUG`.

        If there are no handlers configured, a default handler will be added.
        See :ref:`logging` for more information.
        """
        return create_logger(self)

    @property
    def output_config(self):
        """Convenience property for accessing the output configuration."""
        return self.config.get('output', {})

    @property
    def output_path(self):
        output_path = self._output_path
        if not output_path:
            self.logger.warn('Output path was unset, falling back to default.')
            output_path = DEFAULT_OUTPUT_PATH
        return  os.path.join(self.root, output_path)

    @property
    def preprocessor_config(self):
        """Convenience property for accessing the preprocessor configuration."""
        return self.config.get('preprocessor', {})

    @property
    def root(self):
        return self._root

    @property
    def version(self):
        from . import __version__
        return __version__

    def __init__(self, root=None, honrc_filepath=None, debug=False):
        #: Hon differentiates between a project path and a source path. The
        #: project path is the folder that encompasses all things related to
        #: the Hon project, e.g. the source folder for the book, the .honrc
        #: configuration file, etc. If the project path is ``None``, Hon will
        #: make the assumption that whatever directory it is being run from
        #: is the project path. [SWQ]
        if not root:
            root = os.getcwd()

        self._root = root
        self._loaded_plugins = False
        self._loaded_renderers = False
        self.honrc_filepath = honrc_filepath

        #: Assign default values to the configuration. The default values do
        #: not include any of the default configuration for renderers (i.e.
        #: outputs), preprocessors, etc. These are treated like plugins, even
        #: if they are part of the core, so their default configuration is
        #: defined locally and injected into the application configuration when
        #: they are registered. This means that we need to register all of our
        #: plugins before we actually configure the application, or create the
        #: book.
        self.config = dict(self.default_config)

        self.debug = debug

        #: The books that are registered with the application. By design, Hon
        #: supports multiple books in a project; typically this is leveraged
        #: as different localizations for the same edition of a book.
        self.books = []

        self.preprocessors = []
        self.renderers = []
        self.plugins = []

        #: A list of functions that are called when the application context
        #: is destroyed.  Since the application context is also torn down
        #: if the request ends this is the place to store code that disconnects
        #: from databases.
        self.teardown_appcontext_funcs = []

        #: Instantiate the logger before anything else calls the logger property.
        create_logger(self)

    def init_app(self):
        """Initializes the ``hon`` application.

        Before we read the project's configuration and initialize the book(s),
        we want to load all of the preprocessors, renderers, etc. such that they
        are available to the application and have their default configuration
        loaded. When we run ``_configure()`` it will potentially overwrite these
        defaults.
        """
        self.logger.debug('Initializing Hon application...')
        self._configure()

        self._load_preprocessors()
        self._load_renderers()
        self._load_plugins()

    def _configure(self):
        """Configure the hon application environment.
        """
        self.logger.debug('Configuring Hon application...')
        try:
            config_filepath = self.honrc_filepath
            if config_filepath is None:
                config_filepath = os.path.abspath(os.path.join(self.root, '.honrc'))
                self.honrc_filepath = config_filepath

            self.logger.debug('Reading configuration file: {}'.format(config_filepath))
            config_dict = _read_yaml_config(config_filepath)
            self.config.update(config_dict.get('config', {}))

            #: Configure the output path...
            self._output_path = self.config.get('build') or DEFAULT_OUTPUT_PATH
            self.logger.info('Output path is: {}'.format(self.output_path))
        except:
            self.logger.warning('No .honrc file found, falling back to defaults.')
        return self.config

    def _load_preprocessors(self):
        """Loads the available preprocessors.
        """
        self.logger.debug('Loading preprocessors...')
        preprocessors = get_default_preprocessors()

        for p in preprocessors:
            self.register_preprocessor(p)
        self._load_plugin_preprocessors()

    def _load_renderers(self):
        """Loads the available renderers.
        """
        self.logger.debug('Loading renderers...')
        renderers = get_default_renderers()

        for r in renderers:
            self.register_renderer(r)
        self._load_plugin_renderers()

    def _load_plugins(self):
        """
        """
        self.logger.debug('Loading plugins...')
        if self._loaded_plugins:
            return
        try:
            import pkg_resources
        except ImportError:
            self._loaded_plugins = True
            return

        _plugin_entry_points = pkg_resources.iter_entry_points('hon.plugins')
        for entry_point in _plugin_entry_points:
            self.register_plugin(entry_point.load())
        self._loaded_plugins = True

    def _load_plugin_preprocessors(self):
        pass

    def _load_plugin_renderers(self):
        self.logger.debug('Loading plugin renderers...')
        if self._loaded_renderers:
            return

        try:
            import pkg_resources
        except ImportError:
            self._loaded_renderers = True
            return

        _plugin_renderer_entry_points = pkg_resources.iter_entry_points('hon.renderers')
        for entry_point in _plugin_renderer_entry_points:
            self.register_renderer(entry_point.load())
        self._loaded_renderers = True

    def app_context(self):
        """Create an :class:`~hon.ctx.AppContext`.

        Use as a ``with`` block to push the context, which will make
        :data:`current_app` point at this application.

        An application context is automatically when running a CLI command. Use
        this to manually create a context outside of these situations.

        ::

            with app.app_context():
                app.do_something()

        See :doc:`/appcontext`.
        """
        return AppContext(self)

    def build(self, output_path_override=None, build_only=None):
        """Build a book in one or more formats.

        The ``build_only`` argument specifies which book renderers should be
        run. If no book renderers are specified (i.e. ``book_only=None``), then
        all book renderers will be run. The book renders supported by Hon are:
        ``html``, ``pdf``, ``epub``, and ``mobi``. Hon extensions may make
        additional renderers available.
        """
        self.logger.info('Found {} books to build...'.format(len(self.books)))
        if output_path_override:
            self._output_path = output_path_override
            self.logger.info('Overriding output path. Output path is now: {}'.format(self.output_path))

        if build_only is None:
            build_only = tuple([renderer.name for renderer in self.renderers])

        # TODO: Get and create output directory
        start_time = datetime.now()
        for book in self.books:
            self.logger.info('Building book: {} ({})'.format(book.name, book.path))

            before_build.send(book)
            for renderer in self.renderers:
                if build_only and renderer.name in build_only:
                    renderer.render(book)
            after_build.send(book)

        elapsed_time = datetime.now() - start_time
        self.logger.info('Finished rendering all books in {}s!'.format(elapsed_time))

    def do_teardown_appcontext(self, exc=_sentinel):
        """Called right before the application context is popped.

        When handling a request, the application context is popped after the
        request context. See :meth:`do_teardown_request`.

        This calls all functions decorated with :meth:`teardown_appcontext`.
        Then the :data:`appcontext_tearing_down` signal is sent.

        This is called by :meth:`AppContext.pop() <hon.ctx.AppContext.pop>`.
        """
        if exc is _sentinel:
            exc = sys.exc_info()[1]
        for func in reversed(self.teardown_appcontext_funcs):
            func(exc)
        #: TODO: Add signal: appcontext_tearing_down.send(self, exc=exc)

    def find_books(self, directory):
        """Find one or more books at or under a given directory.

        Books cannot be embedded within one another, so the first time a book is
        found at a certain path, any additional book configurations below that path
        will be ignored.

        :param directory: The directory to begin searching for books in.
        :return: A set of found books.
        """
        book_paths = set()

        located_books = []
        for path, dirs, filenames in os.walk(directory):
            #: Iterate over the found book paths, if at any point the current path
            #: is a subpath of one of the already found books, we ignore it and
            #: continue processing the rest of the directory tree.
            if next((p for p in book_paths if p in path), None):
                self.logger.debug(f'Found embedded book: {path}. Ignoring it.')
                continue

            for f in filenames:
                if str(f).lower() in VALID_BOOK_CONFIGURATIONS:
                    book_paths.add(path)

                    name = os.path.basename(path)
                    config_filepath = os.path.join(path, f)
                    book_path = BookPath(
                        name=name,
                        config_file=f,
                        config_filepath=config_filepath,
                        filepath=path
                    )
                    located_books.append(book_path)
        return sorted(set(located_books), key=attrgetter('filepath'))

    def get_plugin(self, name):
        """
        """
        if issubclass(name, Plugin):
            name = name.get_name()

        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None

    def get_preprocessor(self, name):
        for preprocessor in self.preprocessors:
            if preprocessor.name == name:
                return preprocessor
        return None

    def load_books(self, source_path=None):
        """Initialize a project's books.
        """
        #: If the directory to the book source files was not specified, we make
        #: the assumption that the book source path is the same as the project
        #: path, which may be the directory in which the ``hon`` application
        #: was run from.
        self.logger.info('Loading books on: {}'.format(source_path))
        if not source_path:
            source_path = self.root

        book_paths = self.find_books(source_path)

        for book_path in book_paths:
            book_config = BookConfig.from_file(book_path.config_filepath)
            book = Book(name=book_path.name, path=book_path.filepath, config=book_config)
            book.init_app(self)

            book.load()

            self.books.append(book)
        return self

    def register_plugin(self, plugin):
        key = 'plugin.{}'.format(plugin.get_name())
        plugin_config = dict(plugin.default_config)

        if key in self.config:
            plugin_config.update(self.config[key])

        self.config[key] = plugin_config

        obj = plugin(app=self, config=plugin_config)
        self.plugins.append(obj)
        return obj

    def register_preprocessor(self, preprocessor):
        key = preprocessor.get_name()
        preprocessor_config = dict(preprocessor.default_config)

        if key in self.preprocessor_config:
            preprocessor_config.update(self.preprocessor_config[key])
        self.preprocessor_config[key] = preprocessor_config

        obj = preprocessor(app=self, config=preprocessor_config)
        self.preprocessors.append(obj)
        return obj

    def register_renderer(self, renderer):
        key = renderer.get_name()
        renderer_config = dict(renderer.default_config)

        if key in self.output_config:
            renderer_config.update(self.output_config[key])
        self.output_config[key] = renderer_config

        obj = renderer(app=self, config=renderer_config)
        self.renderers.append(obj)
        return obj

    def serve(self):
        pass

    @setupmethod
    def teardown_appcontext(self, f):
        """Registers a function to be called when the application context ends.

        These functions are typically also called when the request context is
        popped.

        Example::

            ctx = app.app_context()
            ctx.push()
            ...
            ctx.pop()

        When ``ctx.pop()`` is executed in the above example, the teardown
        functions are called just before the app context moves from the
        stack of active contexts.  This becomes relevant if you are using
        such constructs in tests.

        Since a request context typically also manages an application
        context it would also be called when you pop a request context.

        When a teardown function was called because of an unhandled exception
        it will be passed an error object. If an :meth:`errorhandler` is
        registered, it will handle the exception and the teardown will not
        receive it.

        The return values of teardown functions are ignored.
        """
        self.teardown_appcontext_funcs.append(f)
        return f


def create_app(root=None, honrc_filepath=None, debug=False):
    app = Hon(root=root, honrc_filepath=honrc_filepath, debug=True)
    app.init_app()
    return app
