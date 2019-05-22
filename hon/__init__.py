# -*- coding: utf-8 -*-
"""
    hon
    ~~~~

    Hon is a tool for building a book from markdown files.

    :copyright: © 2019 by Sean Quinn.
    :license: MIT, see LICENSE for more details.
"""

__version__ = '0.1.0-dev'

from .app import Hon, create_app
from .globals import _app_ctx_stack, current_app, g
