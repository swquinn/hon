import os
import pytest
from hon.app import (
    get_default_preprocessors, get_default_renderers, Hon
)
from hon.config import _read_yaml_config
from hon.preprocessors import Preprocessor
from hon.renderers import Renderer

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
    expected = ['html', 'pdf', 'epub']
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
    preprocessor_config = actual['preprocessor']
    assert 'index' in preprocessor_config
    assert 'include' in preprocessor_config
    assert 'variables' in preprocessor_config

    output_conifg = actual['output']
    assert 'html' in output_conifg
    assert 'pdf' in output_conifg
    assert 'epub' in output_conifg


@pytest.mark.parametrize('preprocessor_config, expected', [
    (
        {},
        { 'foo': 'bar', 'piyo': 'poyo' }
    ),
    (
        { 'foo': 'baz' },
        { 'foo': 'baz', 'piyo': 'poyo' }
    )
])
def test_register_preprocessor(preprocessor_config, expected):
    """Tests that preprocessors are registered correctly, and have their
    configuration correctly assigned, both within the application's
    configuration and the preprocessor's configuration.
    """

    #: A test-case preprocessor, for evaluating the logic for registering
    #: preprocessors.
    class FooPreprocessor(Preprocessor):
        _name = 'foo'
        default_config = {
            'foo': 'bar',
            'piyo': 'poyo'
        }

    config_key = FooPreprocessor.get_name()

    app = Hon()
    app.config['preprocessor'][config_key] = preprocessor_config

    preprocessor = app.register_preprocessor(FooPreprocessor)
    assert preprocessor is not None
    assert preprocessor.config == expected

    app_config = app.config['preprocessor'][config_key]
    assert app_config is not None
    assert app_config == expected


def test_register_preprocessor_without_configuration():
    """Tests that a preprocessor is registered, only with the preprocessor's
    default configuration.
    """

    #: A test-case preprocessor, for evaluating the logic for registering
    #: preprocessors.
    class BarPreprocessor(Preprocessor):
        _name = 'bar'
        default_config = {
            'bar': 'foo',
            'quux': 'qaaz'
        }

    config_key = BarPreprocessor.get_name()

    app = Hon()

    expected = dict(BarPreprocessor.default_config)

    preprocessor = app.register_preprocessor(BarPreprocessor)
    assert preprocessor is not None
    assert preprocessor.config == expected

    app_config = app.config['preprocessor'][config_key]
    assert app_config is not None
    assert app_config == expected


@pytest.mark.parametrize('renderer_config, expected', [
    (
        {},
        { 'foo': 'bar', 'piyo': 'poyo' }
    ),
    (
        { 'foo': 'baz' },
        { 'foo': 'baz', 'piyo': 'poyo' }
    )
])
def test_register_renderer(renderer_config, expected):
    """Tests that renderers are registered correctly, and have their
    configuration correctly assigned, both within the application's
    configuration and the renderer's configuration.
    """

    #: A test-case renderer, for evaluating the logic for registering
    #: renderers.
    class FooRenderer(Renderer):
        _name = 'foo'
        default_config = {
            'foo': 'bar',
            'piyo': 'poyo'
        }

    config_key = FooRenderer.get_name()

    app = Hon()
    app.config['output'][config_key] = renderer_config

    renderer = app.register_renderer(FooRenderer)
    assert renderer is not None
    assert renderer.config == expected

    app_config = app.config['output'][config_key]
    assert app_config is not None
    assert app_config == expected


def test_register_renderer_without_configuration():
    """Tests that a renderer is registered, only with the renderer's
    default configuration.
    """

    #: A test-case renderer, for evaluating the logic for registering
    #: renderers.
    class BarRenderer(Renderer):
        _name = 'bar'
        default_config = {
            'bar': 'foo',
            'quux': 'qaaz'
        }

    config_key = BarRenderer.get_name()

    app = Hon()

    expected = dict(BarRenderer.default_config)

    renderer = app.register_renderer(BarRenderer)
    assert renderer is not None
    assert renderer.config == expected

    app_config = app.config['output'][config_key]
    assert app_config is not None
    assert app_config == expected
