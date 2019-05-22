class Renderer(object):
    default_config = {}

    def __init__(self, app, config=None):
        self.app = app
        self.config = config or dict(self.default_config)
        
    @property
    def name(self):
        return self.get_name()
    
    @classmethod
    def get_name(cls):
        if not cls._name:
            raise ValueError(('The renderer: {} is missing a name. Did '
                'you forget to assign the `_name` property? All renderers '
                'must have a name. E.g. "html", "pdf", etc.').format(
                cls.__name__))
        return cls._name
    
    def finish(self, book):
        pass

    def init(self, book):
        pass

    def render(self, book):
        self.init(book)
        self.finish(book)