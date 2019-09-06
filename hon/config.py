# -*- coding: utf-8 -*-
"""
    hon.config
    ~~~~~~~~~~
"""
import os
import json
import yaml

#: The latest version of the Hon config.
HON_VERSION_LATEST = '1.0'

HON_DEFAULT_LANGUAGE = 'en'


def _read_yaml_config(file_path):
    config_data = dict()
    try:
        with open(file_path, 'r') as f:
            config_data = yaml.safe_load(f)
    except:
        raise
    return config_data or {}


def _make_config_from_yaml(file_path):
    _yaml = _read_yaml_config(file_path)
    config_data = _yaml.get('book', {})

    #: We get the configuration version, so that we can handle legacy versions
    #: of the configuration and still have a working application. Right now
    #: there's only the one version, so we don't need to do anything special.
    #:
    #: In the future, if we need to support two or more versions this code might
    #: look like:
    #:
    #:   version = config_data.get('version', HON_VERSION_LATEST)
    #:   if version == HON_VERSION_LATEST:
    #:       return _make_latest_config(...)
    #:   else:
    #:       return _make_legacy_config(...)
    #:
    version = config_data.get('version', HON_VERSION_LATEST)

    config = BookConfig(title=config_data.get('title'), version=version)

    ignore_keys = ['title', 'version']
    for (key, value) in config_data.items():
        if not key in ignore_keys:
            config[key] = value
    return config


class BookConfig(dict):
    """A book's configuration details."""

    @property
    def author(self):
        return self.get('author', None)

    @property
    def language(self):
        return self.get('language', HON_DEFAULT_LANGUAGE)

    @property
    def preprocessors(self):
        return self.get('preprocessors', {})

    @property
    def title(self):
        return self.get('title')

    @property
    def variables(self):
        return self.preprocessors.get('variables', {})

    @property
    def version(self):
        return self.get('version', HON_VERSION_LATEST)

    @staticmethod
    def from_file(file_path):
        config = BookConfig()

        file_path = os.path.abspath(file_path)
        try:
            config = _make_config_from_yaml(file_path)
        except:
            # The lack of a configuration file shouldn't be the end of the
            # world, it just means we use the defaults.
            raise
        return config

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))