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
        write_html_to = os.path.join(context['path'], 'book.html')
        write_pdf_to = os.path.join(context['path'], 'book.pdf')
        pdf_template = context['env'].get_template('pdf.html.jinja')
        output = pdf_template.stream({
            'hon': {
                'version': None
            },
            'config': {
                'title': book.config.title,
                'author': book.config.author,
                'language': book.config.language,
            },
            'plugins': context.get('plugins'),
            'pages': book.items,
            'book': {},
            'summary': book.summary
        }).dump(write_html_to)
        
        document = HTML(filename=write_html_to).render()
        document.write_pdf(write_pdf_to)
    
    def on_init(self, book, context):
        env = Environment(
            loader=PackageLoader('hon', 'theme/light/templates/pdf'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        context['env'] = env
        return context

    def on_render_page(self, page, book, context):
        raw_text = str(page.raw_text)
        parser = MarkdownParser()
        markedup_text = parser.parse(raw_text)

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