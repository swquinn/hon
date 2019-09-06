# -*- coding: utf-8 -*-
"""
    hon.helpers
    ~~~~~~~~~~~~~

    Implements various helpers.

"""
import os
from threading import RLock

# sentinel
_missing = object()


class locked_cached_property(object):
    """A decorator that converts a function into a lazy property.

    The function wrapped is called the first time to retrieve the result and
    then that calculated result is used the next time you access the value.
    """
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func
        self.lock = RLock()

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        with self.lock:
            value = obj.__dict__.get(self.__name__, _missing)
            if value is _missing:
                value = self.func(obj)
                obj.__dict__[self.__name__] = value
        return value


def get_debug_flag(default=False):
    """Get whether debug mode should be enabled for the app, indicated
    by the :envvar:`HON_DEBUG` environment variable. The default is
    ``True`` if :func:`.get_env` returns ``'development'``, or ``False``
    otherwise.
    """
    val = os.environ.get('HON_DEBUG')

    if not val:
        return default

    return val.lower() not in ('0', 'false', 'no')


def get_load_dotenv(default=True):
    """Get whether the user has disabled loading dotenv files by setting
    :envvar:`HON_SKIP_DOTENV`. The default is ``True``, load the
    files.

    :param default: What to return if the env var isn't set.
    """
    val = os.environ.get('HON_SKIP_DOTENV')

    if not val:
        return default

    return val.lower() in ('0', 'false', 'no')
