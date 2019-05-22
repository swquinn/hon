class Preprocessor(object):
    """
    :param app: The instance of the hon application.
    :type app: hon.app.Hon
    """
    _name = None

    default_config = {
        'enabled': True
    }

    def __init__(self, app):
        self.app = app

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

    def run(self):
        raise NotImplementedError('A preprocessor must implement this method.')