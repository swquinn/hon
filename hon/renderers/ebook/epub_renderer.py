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

    def create_ebook_container(self, book, context):
        pass

    def generate_chapters(self, book, context):
        """
        """
        for item in book.items:
            filename = '{}.xhtml'.format(item.filename)

            write_to = os.path.join(context.path, filename)

            with open(write_to, 'w') as f:
                f.write(item.text)

    def generate_manifest(self):
        """Creates the ``content.opf`` manifest file for the ebook.
        """
        pass

    def generate_toc(self):
        """Creates the table of contents (``toc.ncx``) file for the ebook.
        """
        pass

    def on_generate_assets(self, book, context):
        import hon.renderers.ebook.epub_assets
        assets_path = os.path.dirname(hon.renderers.ebook.epub_assets.__file__) 

        copy_from(assets_path, context.path, exclude=('__init__.py', ))

    def on_generate_pages(self, book, context):
        """
        """
        self.generate_chapters(book, context)
        self.generate_toc()
        self.generate_manifest()
    
    def on_init(self, book, context):
        """

        :param context: The rendering context for the book.
        :type context: hon.renderers.RenderingContext
        """
        context.configure_environment('theme/light/templates/ebook')
        return context

    def on_render_page(self, page, book, context):
        raw_text = str(page.raw_text)
        parser = MarkdownParser()
        markedup_text = parser.parse(raw_text)

        page_template = context.environment.get_template('page.xhtml.jinja')

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
