import os
from datetime import datetime

class Renderer(object):
    default_config = {}

    @property
    def render_path(self):
        if 'output_dir' in self.config:
            return self.config['output_dir']
        return self.get_name()

    @property
    def name(self):
        return self.get_name()

    def __init__(self, app, config=None):
        self.app = app
        self.config = config or dict(self.default_config)
    
    @classmethod
    def get_name(cls):
        if not cls._name:
            raise ValueError(('The renderer: {} is missing a name. Did '
                'you forget to assign the `_name` property? All renderers '
                'must have a name. E.g. "html", "pdf", etc.').format(
                cls.__name__))
        return cls._name
    
    def finish(self, book, context):
        self.app.logger.debug('Finishing render...')
        self.on_before_finish(book, context)
        self.on_finish(book, context)

    def generate_assets(self, book, context):
        self.app.logger.debug('Generating assets...')
        self.on_generate_assets(book, context)
    
    def generate_pages(self, book, context):
        self.app.logger.debug('Generating pages...')
        # let mut is_index = true;
        for item in book.items:
            # create a render context? could fold book into that.
            self.on_render_page(item, book, context)
        self.on_generate_pages(book, context)

    def init(self, book):
        self.app.logger.debug('Initializing renderer...')
        context = dict()

        render_path = os.path.join(self.app.output_path, self.render_path)
        if not os.path.exists(render_path):
            os.makedirs(render_path, exist_ok=True)

        context['path'] = render_path
        self.on_init(book, context)
        return context

    def on_before_finish(self, book, context):
        pass

    def on_finish(self, book, context):
        pass
    
    def on_generate_assets(self, book, context):
        pass
    
    def on_generate_pages(self, book, context):
        pass

    def on_init(self, book, context):
        pass

    def on_render_page(self, page, book, context):
        pass

    def render(self, book):
        self.app.logger.info('Rendering book: {} with: {} renderer'
            .format(book.name, self.get_name()))

        start_time = datetime.now()

        context = self.init(book)
        self.generate_assets(book, context)
        self.generate_pages(book, context)
        self.finish(book, context)

        elapsed_time = datetime.now() - start_time
        self.app.logger.info('Rendering finished with success in {}s!'.format(elapsed_time))