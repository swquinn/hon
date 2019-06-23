import os
import shutil
from jinja2 import (
    Environment,
    PackageLoader,
    Template,
    select_autoescape
)

from hon.parsing import MarkdownParser
from hon.utils.fileutils import copy_from
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
        assets_js_dir = os.path.join(assets_dir, 'js')
        copy_from(assets_js_dir, context.path, exclude=('**/__init__.py',))

        import hon.theme.light.website
        theme_dir = os.path.dirname(hon.theme.light.website.__file__)
        copy_from(theme_dir, context.path, include=('*.css', '*.js'))

        # TODO: Copy non-markdown files from source to output folder, retaining relative hierarchy


    def on_generate_pages(self, book, context):
        """
        """
        for item in book.items:
            filename = '{}.html'.format(item.filename)

            if item.is_readme:
                filename = 'index.html'
            write_to = os.path.join(context.path, filename)

            with open(write_to, 'w') as f:
                f.write(item.text)

    def on_init(self, book, context):
        """

        :param context: The rendering context for the book.
        :type context: hon.renderers.RenderingContext
        """
        context.configure_environment('theme/light/website/templates')
        return context
    
    def on_render_page(self, page, book, context):
        raw_text = str(page.raw_text)
        parser = MarkdownParser()
        markedup_text = parser.parse(raw_text)

        page_template = context.environment.get_template('page.html.jinja')

        if markedup_text:
            intermediate_template = Template(markedup_text)
            content = intermediate_template.render(book={})

            data = {
                'page': {
                    'title': page.name,
                    'content': content,
                    'previous_chapter': page.previous_chapter,
                    'next_chapter': page.next_chapter,
                }
            }
            data.update(context.data)

            print('*** context: {}'.format(context))
            content = page_template.render(data)
            page.text = content
