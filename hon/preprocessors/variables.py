import re
from collections import namedtuple
from hon.utils.numberutils import to_int_ns
from .preprocessor import Preprocessor


class VariablesPreprocessor(Preprocessor):
    """The variable preprocessor.

    The variable preprocessor takes the variables defined in the book's
    configuration file, i.e. ``book.yaml``, and adds them to the context.
    """
    _name = 'variables'

    def on_run(self, book, renderer, context):
        """
        """
        variables = book.config.get('variables', {})
        context.data['book'].update(variables)
