import os
import pytest
from hon.app import (
    get_default_preprocessors, get_default_renderers, Hon
)
from hon.config import _read_yaml_config

#: Used for scoping function mocks from other modules to the module that they
#: are actually being invoked in.
#:
#: Alternatively:
#:   from hon.app import __name__ as module_prefix
module_prefix = 'hon.app'

@pytest.fixture
def mock__read_yaml_config(mocker):
    _mock = mocker.patch('{}._read_yaml_config'.format(module_prefix))
    _mock.return_value = dict(config={
        'title': 'Test',
        'build': {},
        'output.html': {
            'theme': './themes/monty_python.css'
        },
        'preprocessor.variables': {
            'enabled': False
        }
    })
    return _mock


@pytest.mark.parametrize('book_dir, config_path', [
    ('single-book', [
        'src',
    ]),
    ('multi-book', [
        'src/en',
        'src/fr',
        'src/jp',
    ]),
    ('single-book-with-embedded-books', [
        'src',
    ])
])
def test_find_books(book_dir, config_path):
    app = Hon()

    assets_path = os.path.abspath(os.path.join(os.getcwd(), 'tests/_assets'))
    path = os.path.abspath(os.path.join(assets_path, book_dir))

    books = app.find_books(path)

    actual = [book.filepath for book in books]
    expected = [os.path.abspath(os.path.join(path, p)) for p in config_path]

    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


def test_get_default_preprocessors():
    preprocessors = get_default_preprocessors()

    actual = [p.get_name() for p in preprocessors]
    expected = ['index', 'include', 'variables']
    assert set(actual) == set(expected)


def test_get_default_renderers():
    renderers = get_default_renderers()
    
    actual = [r.get_name() for r in renderers]
    expected = ['html', 'pdf', 'ebook']
    assert set(actual) == set(expected)


def test_configured_initialized_instance(mocker, mock__read_yaml_config):
    app = Hon()
    app.init_app()

    actual = app.config
    assert actual['title'] == 'Test'
    assert actual['output.html']['theme'] == './themes/monty_python.css'
    assert actual['preprocessor.variables']['enabled'] == False
    mock__read_yaml_config.assert_called_once_with(mocker.ANY)


def test_default_initialized_instance():
    """It should instantiate a default Hon application."""
    app = Hon()
    app.init_app()

    actual = app.config
    assert 'title' in actual
    assert 'description' in actual
    assert 'build' in actual

    #: We care less about what is in these configurations, as those could
    #: change and make this test more brittle. The individual preprocessor and
    #: renderer tests should validate that their default configuration settings
    #: are accurate. [SWQ]
    assert 'preprocessor.index' in actual
    assert 'preprocessor.include' in actual
    assert 'preprocessor.variables' in actual
    assert 'output.html' in actual
    assert 'output.pdf' in actual
    assert 'output.ebook' in actual


