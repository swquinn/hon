import os
from jinja2 import Environment, PackageLoader, select_autoescape

from hon.markdown import Markdown
from ..renderer import Renderer

class HtmlRenderer(Renderer):

    _name = 'html'

    #: The default configuration state for the HTML renderer, this is loaded
    #: into the application configuration.
    default_config = {
        'theme': None,

        #: The default theme to use, defaults to 'light'
        'default_theme': 'light',

        #: Use "smart quotes" instead of the usual `"` character.
        'curly_quotes': True,

        #: Should mathjax be enabled?
        #'mathjax_support': bool,
    
        #: An optional google analytics code.
        'google_analytics': None,
        
        #: Additional CSS stylesheets to include in the rendered page's
        #: `<head>`.
        'additional_css': [],
    
        #: Additional JS scripts to include at the bottom of the rendered page's
        #: `<body>`.
        'additional_js': [],
    }

    @property
    def livereload_url(self):
        return None
    
    def on_finish(self, book, context):
        print('in finish')

    def on_generate_assets(self, book, context):
        pass

    def on_generate_pages(self, book, context):
        page_template = context['env'].get_template('page.html.jinja')
        for item in book.items:
            write_to = os.path.join(context['path'], '{}.html'.format(item.filename))
            page_template.stream({
                'page': {
                    'content': item.text
                }
            }).dump(write_to)

    def on_init(self, book, context):
        env = Environment(
            loader=PackageLoader('hon', 'theme/light/templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        context['env'] = env
        return context
    
    def on_render_page(self, page, book, context):
        raw_text = str(page.raw_text)
        md = Markdown()
        markedup_text = md.convert(raw_text)

        if markedup_text:
            page.text = markedup_text
