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
from ..renderer import Renderer

class PdfRenderer(Renderer):
    _name = 'pdf'

    def on_generate_assets(self, book, context):
        pass

    def on_generate_pages(self, book, context):
        """
        """
        write_html_to = os.path.join(context.path, 'book.html')
        write_pdf_to = os.path.join(context.path, 'book.pdf')
        pdf_template = context.environment.get_template('pdf.html.jinja')

        data = {
            'pages': book.items
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
        context.configure_environment('theme/light/templates/pdf')
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

            content = page_template.render(data)
            page.text = content
