# -*- coding: utf-8 -*-
"""
    hon._compat
    ~~~~~~~~~~~~~

    Some extra py2/py3 compatibility support.
"""

import sys
from six import (
    integer_types, string_types, text_type,
    iterkeys, itervalues, iteritems, reraise,
    StringIO,
)

PY2 = sys.version_info[0] == 2
_identity = lambda x: x

if not PY2:
    from inspect import getfullargspec as getargspec

    def implements_bool(cls):
        cls.__nonzero__ = cls.__bool__
        del cls.__bool__
        return cls

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode("utf-8")
        return cls
else:
    from inspect import getargspec

    implements_bool = _identity
    implements_to_string = _identity

# Certain versions of pypy have a bug where clearing the exception stack
# breaks the __exit__ function in a very peculiar way.  The second level of
# exception blocks is necessary because pypy seems to forget to check if an
# exception happened until the next bytecode instruction?
#
# Relevant PyPy bugfix commit:
# https://bitbucket.org/pypy/pypy/commits/77ecf91c635a287e88e60d8ddb0f4e9df4003301
# According to ronan on #pypy IRC, it is released in PyPy2 2.3 and later
# versions.
#
# Ubuntu 14.04 has PyPy 2.2.1, which does exhibit this bug.
BROKEN_PYPY_CTXMGR_EXIT = False
if hasattr(sys, 'pypy_version_info'):
    class _Mgr(object):
        def __enter__(self):
            return self
        def __exit__(self, *args):
            if hasattr(sys, 'exc_clear'):
                # Python 3 (PyPy3) doesn't have exc_clear
                sys.exc_clear()
    try:
        try:
            with _Mgr():
                raise AssertionError()
        except:
            raise
    except TypeError:
        BROKEN_PYPY_CTXMGR_EXIT = True
    except AssertionError:
        pass
