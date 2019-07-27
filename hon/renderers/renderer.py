"""
    hon.renderers.renderer
    ~~~~~
"""
import os
from datetime import datetime

import hon
from hon.structure import Chapter, ChapterGraph, Link, Part
from .render_context import RenderContext


class Renderer(object):
    default_config = {}

    @property
    def items(self):
        chapters = []
        for node in iter(self.chapter_graph):
            chapters.append(node.chapter)
        return tuple(chapters)

    @property
    def render_path(self):
        if 'output_dir' in self.config:
            return self.config['output_dir']
        return self.get_name()

    @property
    def name(self):
        return self.get_name()

    def __init__(self, app, config=None):
        self.app = app
        self.config = config or dict(self.default_config)
        self.chapters = []
        self.chapter_graph = ChapterGraph()
    
    def add_chapter(self, chapter):
        """Adds a chapter to the renderer."""
        self.chapters.append(chapter)
    
    def add_chapters(self, chapters):
        """Adds all chapters to a book, updating the graph."""
        for chapter in chapters:
            self.add_chapter(chapter)

    @classmethod
    def get_name(cls):
        if not cls._name:
            raise ValueError(('The renderer: {} is missing a name. Did '
                'you forget to assign the `_name` property? All renderers '
                'must have a name. E.g. "html", "pdf", etc.').format(
                cls.__name__))
        return cls._name
    
    def finish(self, book, context):
        self.app.logger.debug('Finishing render...')
        self.on_before_finish(book, context)
        self.on_finish(book, context)
        hon.finish_render.send(self.app, book=book, renderer=self, context=context)

    def generate_assets(self, book, context):
        """Generate assets.
        """
        self.app.logger.debug('Generating assets...')
        self.on_generate_assets(book, context)

        #: 
        hon.generate_assets.send(self.app, book=book, renderer=self, context=context)
    
    def generate_pages(self, book, context):
        self.app.logger.debug('Generating pages...')
        
        # TODO: Write the README.md to file
        # TODO: Write the SUMMARY.md to file
        # TODO: Write the GLOSSARY.md to file

        for item in self.items:
            hon.before_render_page.send(self.app, book=book, renderer=self, page=item)
            self.on_render_page(item, book, context)
            hon.after_render_page.send(self.app, book=book, renderer=self, page=item)
        self.on_generate_pages(book, context)

    def init(self, book):
        self.app.logger.debug('Initializing renderer...')
        context = RenderContext(book=book, render_path=self.render_path)

        self.on_init(book, context)
        return context

    def init_chapters(self, book):
        """Use the book's summary to load the book's pages from disk."""
        self.app.logger.debug('Loading chapters from disk')

        summary_items = book.summary.all_parts
        for item in summary_items:
            if type(item) == Part:
                chapter = self.load_chapter(book, item)
                self.add_chapter(chapter)
        self.chapter_graph.extend(self.chapters)
        return self.chapters
    
    def load_chapter(self, book, item, parent=None):
        chapter = None
        chapter_path = os.path.abspath(os.path.join(book.path, item.source))
        
        if not os.path.exists(chapter_path):
            raise FileNotFoundError('File: {} not found.'.format(chapter_path))
                
        with open(chapter_path) as f:
            raw = f.read()
            chapter = Chapter(name=item.name, raw_text=raw, path=chapter_path, link=item.link, parent=parent)
        
        if not chapter:
            raise TypeError('Chapter not created')

        sub_chapters = []
        if item.children:
            for sub_item in item.children:
                sub_chapter = self.load_chapter(book, sub_item, parent=item)
                sub_chapters.append(sub_chapter)
        
        if sub_chapters:
            chapter.children = sub_chapters
        return chapter

    def on_before_finish(self, book, context):
        pass

    def on_finish(self, book, context):
        pass
    
    def on_generate_assets(self, book, context):
        pass
    
    def on_generate_pages(self, book, context):
        pass

    def on_init(self, book, context):
        pass

    def on_render_page(self, page, book, context):
        pass

    def render(self, book):
        """
        """
        self.app.logger.info('Rendering book: {} with: {} renderer'
            .format(book.name, self.get_name()))

        start_time = datetime.now()

        chapters = self.init_chapters(book)
        self.app.logger.debug('Successfully loaded {} chapters.'.format(len(chapters)))

        context = self.init(book)

        #: We now preprocess for each renderer, this gives our preprocessors
        #: access to the not only the book, but also the context. [SWQ]
        for preprocessor in self.app.preprocessors:
            if preprocessor.enabled:
                self.app.logger.debug("Running the {} preprocessor.".format(preprocessor.name))
                preprocessor.run(book, self, context)

        #: After the context has been established and the preprocessors have
        #: been run, but before any of the actual rendering has commenced,
        #: trigger the "before_render" signal. This will allow more general
        #: plugins the opportunity to do some pre-render work. They can modify
        #: the context, or even make changes to the render items. [SWQ]
        hon.before_render.send(self.app, book=book, renderer=self, context=context)

        #: Run the logic for the renderer, this includes generating assets,
        #: pages, and finalizing the book's renderering.
        self.generate_assets(book, context)
        self.generate_pages(book, context)
        self.finish(book, context)

        #: After the book has been rendered, do any final clean up.
        hon.after_render.send(self.app, book=book, renderer=self, context=context)

        elapsed_time = datetime.now() - start_time
        self.app.logger.info('Finished rendering book: {} with: {} successfully in {}s!'.format(
            book.name, self.get_name(), elapsed_time))