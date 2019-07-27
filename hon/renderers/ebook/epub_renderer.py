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

IGNORED_FILES = ('**/__pycache__/*', '**/__init__.py', )


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
        try:
            handle, temp_filename = mkstemp()
            with open(temp_filename, 'w') as f:
                f.write(content)

            # actually add to the epub (zip file), override the archive name,
            # so we don't end up having the temp file as the name
            self.write(temp_filename, arcname=filename)
        finally:
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
        for item in self.items:
            filename = '{}.xhtml'.format(item.filename)
            if item.is_readme:
                continue

            #: Get the item's path, relative to the book's root. This allows
            #: us to actually write the transformed items to a structure that
            #: is similar to the source. [SWQ]
            relative_item_path = os.path.relpath(item.path, start=book.path)
            relative_item_dir = os.path.dirname(relative_item_path)

            output_path = os.path.join(context.path, relative_item_dir)
            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)

            write_to = os.path.join(output_path, filename)
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
            copy_from(style, context.path, exclude=IGNORED_FILES)

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
        
        def foo(parts, context):
            structure = []
            for part in parts:
                part_filepath = '{}.xhtml'.format(part.link_name)
                if part.is_readme:
                    part_filepath = 'titlepage.xhtml'

                path = os.path.abspath(os.path.join(context.path, part_filepath))
                relative_path = os.path.relpath(path, start=context.path)
                structure.append({
                    'name': 'Cover' if part.is_readme else part.name,
                    'href': relative_path,
                })
                if len(part.children) > 0:
                    structure.extend(foo(part.children, context))
            return structure
                
        # resolve all of the parts that we're working with,
        structure = foo(book.summary.all_parts, context)
        context.data['epub_chapters'] = structure
        return context

    def on_render_page(self, page, book, context):
        """

        :type page: hon.structure.chapter.Chapter
        """
        raw_text = str(page.raw_text)
        parser = MarkdownParser()
        markedup_text = parser.parse(raw_text)

        page_template = context.environment.get_template('page.xhtml.jinja')

        if markedup_text:
            intermediate_template = Template(markedup_text)
            content = intermediate_template.render(book={})

            relative_page_path = os.path.relpath(page.path, start=book.path)
            abs_page_path = os.path.join(context.path, relative_page_path)
            page_dir = os.path.dirname(abs_page_path)
            root_path = os.path.relpath(context.path, start=page_dir)

            node = self.chapter_graph.get(page)
            data = {
                'page': {
                    'title': page.name,
                    'content': content,
                    'root_path': root_path,
                    'previous_chapter': node.previous.chapter if node.previous else None,
                    'next_chapter': node.next.chapter if node.next else None,
                }
            }
            data.update(context.data)

            content = page_template.render(data)
            page.text = content
