"""
    hon.renderers.ebook.epub_renderer
    ~~~~~
"""
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
from .ebook_renderer import EbookRenderer

IGNORED_FILES = ('__init__.py', )

class EpubRenderer(EbookRenderer):
    _name = 'epub'

    def on_generate_assets(self, book, context):
        import hon.renderers.ebook.epub_assets
        assets_path = os.path.dirname(hon.renderers.ebook.epub_assets.__file__) 

        copy_from(assets_path, context['path'], exclude=('__init__.py', ))

    def on_generate_pages(self, book, context):
        """
        """
        for item in book.items:
            filename = '{}.xhtml'.format(item.filename)

            write_to = os.path.join(context['path'], filename)

            with open(write_to, 'w') as f:
                f.write(item.text)
    
    def on_init(self, book, context):
        env = Environment(
            loader=PackageLoader('hon', 'theme/light/templates/ebook'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        context['env'] = env
        return context

    def on_render_page(self, page, book, context):
        raw_text = str(page.raw_text)
        parser = MarkdownParser()
        markedup_text = parser.parse(raw_text)

        page_template = context['env'].get_template('page.xhtml.jinja')

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