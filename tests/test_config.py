import os.path
import yaml
import pytest
from hon.config import (
    _read_yaml_config, _make_config_from_yaml,
)


@pytest.fixture
def complex_config_stub():
    yaml_doc = """
        book:
            title: Test
            description: A full configuration example.
            preprocessors:
                links:
                    quux: qaaz
                variables:
                    var: pico
                    ns.var: puyo
    """
    return yaml.safe_load(yaml_doc)


@pytest.fixture
def mock__read_yaml_config(mocker, complex_config_stub):
    module = _read_yaml_config.__module__
    _mock = mocker.patch('{}._read_yaml_config'.format(module))
    _mock.return_value = complex_config_stub
    return _mock


@pytest.fixture
def simple_config_file():
    return os.path.abspath('./tests/_configs/simple.yaml')


def test__read_yaml_config(simple_config_file):
    actual = _read_yaml_config(simple_config_file)

    expected = {
        'book': {
            'title': 'Test',
            'description': 'A simple test config.'
        }
    }
    assert actual == expected


def test__make_config_from_yaml(mock__read_yaml_config):
    actual = _make_config_from_yaml('config.yaml')

    expected = {
        'title': 'Test',
        'version': '1.0',
        'description': 'A full configuration example.',
        'preprocessors': {
            'links': {
                'quux': 'qaaz'
            },
            'variables': {
                'var': 'pico',
                'ns.var': 'puyo'
            }
        }
    }
    assert actual == expected
