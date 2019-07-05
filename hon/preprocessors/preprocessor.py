#: TODO: There needs to be a better way of configuring preprocessors.
#:       right now the preprocessor instance is unaware of configuration loaded
#:       by the app.
class Preprocessor(object):
    """

    Preprocessors receive their configuration from two sources: global .honrc
    configuration which applies to all preprocessors and then book specific
    configuration which is read from the book.yaml file.

    :param app: The instance of the hon application.
    :type app: hon.app.Hon
    """
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
            raise ValueError(('The preprocessor: {} is missing a name. Did '
                'you forget to assign the `_name` property? All preprocessors '
                'must have a name. E.g. "index", "links", etc.').format(
                cls.__name__))
        return cls._name

    def run(self, book, renderer, context):
        if self.enabled:
            self.on_run(book, renderer, context)

    def on_run(self, book, renderer, context):
        raise NotImplementedError('A preprocessor must implement this method.')
