import os
import shutil
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
        import hon.theme.light
        light_theme_dir = os.path.dirname(hon.theme.light.__file__)
        js_dir = os.path.abspath(os.path.join(light_theme_dir, 'js'))
        css_dir = os.path.abspath(os.path.join(light_theme_dir, 'css'))
        
        js_output_dir = os.path.join(context['path'], 'js')
        os.makedirs(js_output_dir, exist_ok=True)

        css_output_dir = os.path.join(context['path'], 'css')
        os.makedirs(css_output_dir, exist_ok=True)

        # TODO: Copy theme assets to the output folder
        css_files = os.listdir(css_dir)
        for css_file in css_files:
            source = os.path.join(css_dir, css_file)
            if os.path.isfile(source):
                dest = os.path.join(css_output_dir, css_file)
                shutil.copyfile(source, dest)

        js_files = os.listdir(js_dir)
        for js_file in js_files:
            source = os.path.join(css_dir, js_file)
            if os.path.isfile(source):
                dest = os.path.join(js_output_dir, js_file)
                shutil.copyfile(source, dest)

        # TODO: Copy non-markdown files from source to output folder, retaining relative hierarchy


    def on_generate_pages(self, book, context):
        page_template = context['env'].get_template('page.html.jinja')
        for item in book.items:
            filename = '{}.html'.format(item.filename)
            if item.is_readme:
                filename = 'index.html'
            write_to = os.path.join(context['path'], filename)
            page_template.stream({
                'hon': {
                    'version': None
                },
                'config': {
                    'title': book.config.title,
                    'author': book.config.author,
                    'language': book.config.language,
                },
                'plugins': {
                    'resources': {}
                },
                'page': {
                    'title': item.name,
                    'content': item.text
                },
                'summary': book.summary
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
