"""
    hon.renderers.pdf.pdf_renderer
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
from weasyprint import HTML

from hon.parsing import MarkdownParser
from hon.utils.fileutils import copy_from
from ..renderer import Renderer

PAGE_BREAK = 'page break'
PAGE_BREAK = 'page break'

class PdfRenderer(Renderer):
    """Renders a book to a PDF file.

    The PDF renderer has the following default configuration::

        {
            'enabled': True,
            'styles': []
            'font_size': 12,
            'font_family': 'serif',
            'paper_size': 'a4',
            'chapter_mark': PAGE_BREAK
            'margin': {
                'right': 62,
                'left': 62,
                'top': 56,
                'bottom': 56
            }
            'page_numbers': True,
            'page_breaks_before': '/',
            'page_margin': {
                'right': 72,
                'left': 72,
                'top': 72,
                'bottom': 72,
            }
        }
    """
    _name = 'pdf'

    default_config = {
        'enabled': True,
        'styles': [],
        'font_size': 12,
        'font_family': 'serif',
        'paper_size': 'a4',
        'chapter_mark': PAGE_BREAK,
        'margin': {
            'right': 62,
            'left': 62,
            'top': 56,
            'bottom': 56,
        },
        'page_numbers': True,
        'page_breaks_before': '/',
        'page_margin': {
            'right': 72,
            'left': 72,
            'top': 72,
            'bottom': 72,
        }
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

        super(PdfRenderer, self).__init__(app, config=config)

    def on_generate_assets(self, book, context):
        import hon.theme.light.pdf
        theme_dir = os.path.dirname(hon.theme.light.pdf.__file__)

        theme_css_dir = os.path.join(theme_dir, 'css')
        copy_from(theme_css_dir, context.path, include=('*.css', ))

        user_styles = self.config.get('styles', [])
        for style in user_styles:
            context.add_style(os.path.basename(style))
            copy_from(style, context.path)

    def on_generate_pages(self, book, context):
        """
        """
        write_html_to = os.path.join(context.path, 'book.html')
        write_pdf_to = os.path.join(context.path, 'book.pdf')
        pdf_template = context.environment.get_template('pdf.html.jinja')

        data = {
            'pages': self.items
        }
        data.update(context.data)

        output = pdf_template.stream(data).dump(write_html_to)
        
        document = HTML(filename=write_html_to).render()
        document.write_pdf(write_pdf_to)
    
    def on_init(self, book, context):
        """

        :param context: The rendering context for the book.
        :type context: hon.renderers.RenderingContext
        """
        context.configure_environment('theme/light/pdf/templates')
        return context

    def on_render_page(self, page, book, context):
        raw_text = str(page.raw_text)
        parser = MarkdownParser()
        markedup_text = parser.parse(raw_text)

        page_template = context.environment.get_template('page.html.jinja')

        if markedup_text:
            intermediate_template = Template(markedup_text)
            content = intermediate_template.render(book={})

            node = self.chapter_graph.get(page)
            data = {
                'page': {
                    'title': page.name,
                    'content': content,
                    'previous_chapter': node.previous.chapter if node.previous else None,
                    'next_chapter': node.next.chapter if node.next else None,
                }
            }
            data.update(context.data)

            content = page_template.render(data)
            page.text = content
