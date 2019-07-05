import re
from collections import namedtuple
from hon.utils.numberutils import to_int_ns
from .preprocessor import Preprocessor
# use utils::fs::file_to_string;
# use utils::take_lines;

ESCAPE_CHAR = '\\'

VariableMeta = namedtuple('VariableMeta', ['token', 'start_index', 'end_index'])
VariableMeta.__new__.__defaults__ = (None, None, None)


def _create_variable(variable_name=None, metadata=None):
    if not variable_name or variable_name[0] == ESCAPE_CHAR:
        return None
    
    return Variable(
        start_index=metadata.start_index,
        end_index=metadata.end_index,
        name=variable_name,
        token_text=metadata.token,
    )


def process_matches(matches):
    results = []
    for index, match in enumerate(matches):
        meta = VariableMeta(token=match.group(0), start_index=match.start(), end_index=match.end())

        filtered = [m for m in match.groups() if m][:1]
        item = _create_variable(*filtered, metadata=meta)
        if item:
            results.append(item)
    return results


def find_variables(contents):
    pattern = (
        r'(\\\{\{.+\}\})'             # match an escaped variable, e.g. \{{ foo.bar }}
        r'|'                          # or
        r'\{\{\s*'                    # variable opening parens and whitespace
        r'book\.([a-zA-Z\d\-\_\.]+)'  # the variable reference
        r'\s*\}\}'                    # whitespace and variable closing parens
    )
    match_iter = re.finditer(pattern, contents, flags=(re.MULTILINE & re.IGNORECASE))
    matches = list(match_iter)
    return process_matches(matches)


def replace_all(text, book_variables):
    """
    """
    replaced = text

    for placeholder in find_variables(text):
        replacement_text = book_variables.get(placeholder.name, '')
        replaced = replaced.replace(placeholder.token_text, replacement_text)
    return replaced


class Variable(object):

    def __init__(self, start_index=None, end_index=None, name=None, token_text=None):
        #: int - starting position where to begin swapping out the text
        self.start_index = start_index
        #: int - ending position where to begin swapping out the text
        self.end_index = end_index
        #: inclusion instance type, e.g. playpen, include, etc.
        self.name = name
        #: str
        self.token_text = token_text
    
    def __hash_key(self):
        return (self.start_index, self.end_index, self.name, self.token_text)

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__hash_key() == other.__hash_key()

    def __repr__(self):
        return ('Variable(start_index={start_index}, end_index={end_index}, '
            'name={name}, token_text={token_text})').format(
            start_index=self.start_index, end_index=self.end_index,
            name=repr(self.name), token_text=repr(self.token_text))


class VariablesPreprocessor(Preprocessor):
    """
    """
    _name = 'variables'

    default_config = {
        'enabled': True,
        'data': {}
    }

    def __init__(self, app, config=None):
        super(VariablesPreprocessor, self).__init__(app, config=config)

    def on_run(self, book, renderer, context):
        """
        """
        variables = book.config.get('variables', {})
        context.data['book'].update(variables)

        for item in renderer.items:
            content = replace_all(item.raw_text, variables)
            item.raw_text = content
