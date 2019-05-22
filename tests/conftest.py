# -*- coding: utf-8 -*-
"""
    tests.conftest
    ~~~~~
"""

#import gc
import os
#import pkgutil
#import sys
#import textwrap

import pytest
#from _pytest import monkeypatch

import hon
from hon import Hon as _Hon

import logging

logging.getLogger('hon').setLevel(logging.DEBUG)
logging.getLogger('hon.utils').setLevel(logging.DEBUG)

@pytest.fixture
def app():
    app = _Hon()
    return app


@pytest.fixture
def app_ctx(app):
    with app.app_context() as ctx:
        yield ctx


@pytest.fixture
def assets_path():
    return os.path.abspath(os.path.join(os.getcwd(), 'tests/_assets'))
