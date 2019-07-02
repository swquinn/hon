"""
    hon.renderers.ebook.epub_renderer
    ~~~~~
"""
import os
import shutil
from fnmatch import fnmatch
from jinja2 import Template
from tempfile import mkstemp
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

from hon.parsing import MarkdownParser
from hon.utils.fileutils import copy_from, filename_matches_pattern
from .ebook_renderer import EbookRenderer

IGNORED_FILES = ('**/__init__.py', )


class EpubContainer(ZipFile):

    def writecontent(self, filename, content):
        ''' writestr(filename, content) seems to cause problems,
            content is ok, but the permission are wrong (atleast on OSX)

            so, what we do is:
                a) create a temp file
                b) write content to the temp file
                c) add temp file to zip
                d) remove the temp file

        '''

        handle, temp_filename = mkstemp()

        f = open(temp_filename, 'w')
        f.write(content)
        f.close()

        # actually add to the epub (zip file), override the archive name,
        # so we don't end up having the temp file as the name
        self.write(temp_filename, arcname=filename)

        # remove tempfile, we are done
        os.remove(temp_filename)


class EpubRenderer(EbookRenderer):
    """Renders a book to an epub file.
    """
    _name = 'epub'

    default_config = {
        'enabled': True,
        'styles': []
    }

    def __init__(self, app, config=None):
        styles = config.get('styles', [])
        if styles:
            resolved_styles = []
            root = os.path.dirname(app.honrc_filepath)
            for style in styles:
                resolved_style_filepath = os.path.abspath(
                    os.path.join(root, style))
                resolved_styles.append(resolved_style_filepath)
            config['styles'] = resolved_styles

        super(EpubRenderer, self).__init__(app, config=config)

    def create_ebook_container(self, book, context):
        write_to = os.path.join(context.path, 'book.epub')

        with EpubContainer(write_to, 'w', ZIP_STORED) as container:
            mimetype_filepath = os.path.join(context.path, 'mimetype')
            container.write(mimetype_filepath, arcname='mimetype')

            for dirpath, _, filenames in os.walk(context.path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)

                    ignore = filename_matches_pattern(filepath, ('**/mimetype', '*.epub'))
                    if os.path.isfile(filepath) and not ignore:
                        relative_filepath = os.path.relpath(filepath, start=context.path)
                        container.write(filepath, arcname=relative_filepath)

    def generate_chapters(self, book, context):
        """
        """
        for item in book.items:
            filename = '{}.xhtml'.format(item.filename)

            write_to = os.path.join(context.path, filename)

            with open(write_to, 'w') as f:
                f.write(item.text)

    def generate_manifest(self, book, context):
        """Creates the ``content.opf`` manifest file for the ebook.
        """
        template = context.environment.get_template('content.opf.jinja')
        write_to = os.path.join(context.path, 'content.opf')

        data = {}
        data.update(context.data)
        template.stream(data).dump(write_to)

    def generate_titlepage(self, book, context):
        template = context.environment.get_template('titlepage.xhtml.jinja')
        write_to = os.path.join(context.path, 'titlepage.xhtml')

        data = {}
        data.update(context.data)
        template.stream(data).dump(write_to)

    def generate_toc(self, book, context):
        """Creates the table of contents (``toc.ncx``) file for the ebook.
        """
        template = context.environment.get_template('toc.ncx.jinja')
        write_to = os.path.join(context.path, 'toc.ncx')

        data = {}
        data.update(context.data)
        template.stream(data).dump(write_to)

    def on_finish(self, book, context):
        self.create_ebook_container(book, context)

    def on_generate_assets(self, book, context):
        import hon.renderers.ebook.epub_assets
        assets_path = os.path.dirname(hon.renderers.ebook.epub_assets.__file__) 
        copy_from(assets_path, context.path, exclude=IGNORED_FILES)

        import hon.theme.light.epub
        theme_path = os.path.dirname(hon.theme.light.epub.__file__)
        theme_css_path = os.path.join(theme_path, 'css')
        copy_from(theme_css_path, context.path, include=('*.css', ))

        user_styles = self.config.get('styles', [])
        for style in user_styles:
            context.add_style(os.path.basename(style))
            copy_from(style, context.path)
            

    def on_generate_pages(self, book, context):
        """
        """
        self.generate_titlepage(book, context)
        self.generate_chapters(book, context)
        self.generate_toc(book, context)
        self.generate_manifest(book, context)
    
    def on_init(self, book, context):
        """

        :param context: The rendering context for the book.
        :type context: hon.renderers.RenderingContext
        """
        context.configure_environment('theme/light/epub/templates')
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
