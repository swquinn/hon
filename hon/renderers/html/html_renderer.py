import os
import shutil
from jinja2 import (
    Environment,
    PackageLoader,
    Template,
    select_autoescape
)

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
        import hon.renderers.html.assets
        assets_dir = os.path.dirname(hon.renderers.html.assets.__file__) 
        assets_js_dir = os.path.abspath(os.path.join(assets_dir, 'js'))

        js_files = os.listdir(assets_js_dir)
        for js_file in js_files:
            source = os.path.join(assets_js_dir, js_file)
            if os.path.isfile(source):
                dest = os.path.join(context['path'], js_file)
                shutil.copyfile(source, dest)

        import hon.theme.light
        theme_dir = os.path.dirname(hon.theme.light.__file__)
        theme_js_dir = os.path.abspath(os.path.join(theme_dir, 'js'))
        theme_css_dir = os.path.abspath(os.path.join(theme_dir, 'css'))
        
        js_output_dir = os.path.join(context['path'], 'js')
        os.makedirs(js_output_dir, exist_ok=True)

        css_output_dir = os.path.join(context['path'], 'css')
        os.makedirs(css_output_dir, exist_ok=True)

        theme_css_files = os.listdir(theme_css_dir)
        for css_file in theme_css_files:
            source = os.path.join(theme_css_dir, css_file)
            if os.path.isfile(source):
                dest = os.path.join(css_output_dir, css_file)
                shutil.copyfile(source, dest)

        theme_js_files = os.listdir(theme_js_dir)
        for js_file in theme_js_files:
            source = os.path.join(theme_js_dir, js_file)
            if os.path.isfile(source):
                dest = os.path.join(js_output_dir, js_file)
                shutil.copyfile(source, dest)

        # TODO: Copy non-markdown files from source to output folder, retaining relative hierarchy


    def on_generate_pages(self, book, context):
        """
        """
        for item in book.items:
            filename = '{}.html'.format(item.filename)

            if item.is_readme:
                filename = 'index.html'
            write_to = os.path.join(context['path'], filename)

            with open(write_to, 'w') as f:
                f.write(item.text)

    def on_init(self, book, context):
        env = Environment(
            loader=PackageLoader('hon', 'theme/light/templates/website'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        context['env'] = env
        return context
    
    def on_render_page(self, page, book, context):
        raw_text = str(page.raw_text)
        md = Markdown()
        markedup_text = md.convert(raw_text)

        page_template = context['env'].get_template('page.html.jinja')

        if markedup_text:
            intermediate_template = Template(markedup_text)
            content = intermediate_template.render(book={})

            book_context = {}
            book_context.update(book.get_variables())

            print('*** context: {}'.format(context))
            content = page_template.render({
                'hon': {
                    'version': None
                },
                'config': {
                    'title': book.config.title,
                    'author': book.config.author,
                    'language': book.config.language,
                },
                'plugins': context.get('plugins'),
                'page': {
                    'title': page.name,
                    'content': content,
                    'previous_chapter': page.previous_chapter,
                    'next_chapter': page.next_chapter,
                },
                'book': book_context,
                'summary': book.summary
            })
            page.text = content
