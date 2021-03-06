"""
"""
import os
from datetime import datetime
from jinja2 import (
    Environment,
    PackageLoader,
    select_autoescape
)
from six import string_types


class RenderContext():
    """A render context that is passed to each rendering stage.

    :param book: The book that this render context will be associated with, the
        render context will not be initialized until a book is associated with
        the rendering context.
    """

    #: The default data state for the render context.
    _default_data = {
        '_hon': {},
        '_plugins': {
            'resources': {
                'js': [],
                'css': [],
            }
        },
        'styles': []
    }

    @property
    def environment(self):
        return self._environment

    @property
    def is_initialized(self):
        return self._initialized

    @property
    def path(self):
        return self._path

    def __init__(self, book=None, render_path=None):
        #: Whether the render context is initialized or not.
        self._initialized = False

        #: The rendering environment. This is a Jinja2 environment. Initializing
        #: a rendering context does not directly instantiate the environment.
        #: The environment is instantiated when ``configure_environment`` is
        #: called.`
        self._environment = None

        #: The path that the rendering context writes to.
        self._path = None

        #: The mutable dictionary of data
        self.data = self._default_data

        self.render_path = render_path

        if book:
            self.init_book(book)

    def add_plugin_resource(self, resource, resource_type):
        """Appends a resource to the collection of resources for a given type.
        """
        if not self.data['_plugins']['resources'][resource_type]:
            self.data['_plugins']['resources'][resource_type] = []
        self.data['_plugins']['resources'][resource_type].append(resource)

    def add_style(self, style):
        if not self.data['styles']:
            self.data['styles'] = []
        self.data['styles'].append(style)

    def init_book(self, book):
        app = book.app

        #: Assign the path
        self._path = os.path.join(app.output_path, self.render_path)
        if not os.path.exists(self._path):
            os.makedirs(self._path, exist_ok=True)

        #: Populate the data for the render context.
        self.data['_hon']['version'] = app.version
        self.data['_book'] = book
        self.data['_root'] = self.path
        self.data['title'] = book.title
        if isinstance(book.author, string_types):
            self.data['author'] = (book.author, )
        else:
            self.data['author'] = tuple(book.author)
        self.data['language'] = book.language
        self.data['isbn'] = '000-0000000000'
        self.data['date'] = datetime.now().isoformat()
        self.data['publisher'] = 'Hon'
        self.data['book'] = {}
        self.data['summary'] = book.summary

        #: Complete initialization and mark context as initialized.
        self._initialized = True

    def configure_environment(self, template_path, pkg='hon'):
        """
        """
        self._environment = Environment(
            loader=PackageLoader(pkg, template_path),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.load_filters()

    def load_filters(self):
        from hon.filters import relative_path
        self._environment.filters['relative_path'] = relative_path
