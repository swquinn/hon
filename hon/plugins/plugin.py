"""
"""


class Plugin(object):
    _name = None

    default_config = {
        'enabled': True
    }

    def __init__(self, app, config=None):
        self.app = app
        self.config = config or dict(self.default_config)

    @property
    def enabled(self):
        return self.config.get('enabled', True)

    @property
    def name(self):
        return self.get_name()

    @classmethod
    def get_name(cls):
        if not cls._name:
            raise ValueError(('The plugin: {} is missing a name. Did you '
                'forget to assign the `_name` property? All preprocessors '
                'must have a name. E.g. "index", "links", etc.').format(
                cls.__name__))
        return cls._name

    def init_book(self, book):
        """
        """
        pass
