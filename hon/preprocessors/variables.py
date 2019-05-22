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
    print(f'Found {len(matches)}')
    for index, match in enumerate(matches):
        meta = VariableMeta(token=match.group(0), start_index=match.start(), end_index=match.end())

        filtered = [m for m in match.groups() if m][:1]
        print(f'matching {index+1}: {filtered}')
        item = _create_variable(*filtered, metadata=meta)
        if item:
            results.append(item)
    return results


def find_variables(contents):
    pattern = (
        r'(\\\{\{.+\}\})'             # match an escaped variable, e.g. \{{ foo.bar }}
        r'|'                          # or
        r'\{\{\s*'                    # variable opening parens and whitespace
        r'([a-zA-Z\d\-\_\.]+)'        # the variable reference
        r'\s*\}\}'                    # whitespace and variable closing parens
    )
    match_iter = re.finditer(pattern, contents, flags=(re.MULTILINE & re.IGNORECASE))
    matches = list(match_iter)
    return process_matches(matches)


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

    def __eq__(self, other):
        if (self.start_index == other.start_index and
            self.end_index == other.end_index and
            self.name == other.name and
            self.token_text == other.token_text):
            return True
        return False

    def __repr__(self):
        return ('Variable(start_index={start_index}, end_index={end_index}, '
            'name={name}, token_text={token_text})').format(
            start_index=self.start_index, end_index=self.end_index,
            name=repr(self.name), token_text=repr(self.token_text))


class VariablesPreprocessor(Preprocessor):
    _name = 'variables'

    default_config = {
        'enabled': True
    }

    def run(self):
        pass
