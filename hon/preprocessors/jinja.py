"""
    hon.preprocessors.jinja
    ~~~~~
"""
import errno
import os
import re
from collections import namedtuple
from jinja2 import Environment, BaseLoader, ChoiceLoader, DictLoader, select_autoescape, TemplateNotFound
from six import string_types

from .preprocessor import Preprocessor
from hon.utils.numberutils import to_int_ns


def resolve_template_filepath(paths, template_reference):
    """Resolves a template filepath, given a reference and a collection of
    possible paths where it might be found.

    This function returns the first matching resolved template filepath, if the
    chapter files and their children are ambiguously named you might find that
    using completely relative links results in the wrong files being included.
    You can always ensure that the correct file is loaded by being more specific
    about where the file should be loaded from.
    """
    for path in paths:
        filepath = os.path.abspath(os.path.join(path, template_reference))
        if os.path.exists(filepath):
            return filepath
    return None


class ChapterLoader(BaseLoader):
    """Loads templates from the filesystem in relation to the location of a
    chapter. This loader is dynamic and resolves templates as it comes across
    references to them.

    The loader is similar in many ways to the file system loader provided by
    Jinja2: it has one or more paths where it looks up templates on the file
    system and resolves them. Unlike the file system loader, however, the
    chapter loader dynamically discovers additional paths to look for templates
    under as it encounters template references.

    It does this by appending the directory name of every template file it
    finds to the path.

    When creating a new ``ChapterLoader``, you can either pass it a reference
    to a single chapter file, the directory that the chapter file is located in,
    or multiple directories containing chapter files::

    >>> loader = ChapterLoader('/path/to/chapters/chapter_file.md')
    >>> loader = ChapterLoader('/path/to/chapters')
    >>> loader = ChapterLoader(['/path/to/chapters', '/other/path'])

    Per default the template encoding is ``'utf-8'`` which can be changed
    by setting the `encoding` parameter to something else.

    To follow symbolic links, set the *followlinks* parameter to ``True``::

    >>> loader = FileSystemLoader('/path/to/templates', followlinks=True)
    """

    def __init__(self, chapter_path, encoding='utf-8', followlinks=False):
        #: If we've been given only a single chapter path (as a string), and
        #: that path points to a file (rather than a directory) we want to
        #: resolve the directory's name.
        if isinstance(chapter_path, string_types):
            if os.path.isfile(chapter_path):
                chapter_path = os.path.dirname(chapter_path)
            chapter_path = [chapter_path]

        self.chapter_path = chapter_path
        self.paths = list(chapter_path)
        self.encoding = encoding
        self.followlinks = followlinks

    def get_source(self, environment, template):
        # find the template, relative to the markdown file's path
        # record the last location of the
        filename = resolve_template_filepath(self.paths, template)
        if filename is None:
            raise TemplateNotFound(template)

        with open(filename, 'rb') as f:
            contents = f.read().decode(self.encoding)
            mtime = os.path.getmtime(filename)

            def uptodate():
                try:
                    return os.path.getmtime(filename) == mtime
                except OSError:
                    return False

        self.paths.append(os.path.dirname(filename))
        return contents, filename, uptodate

    def list_templates(self):
        raise TypeError('This loader is unable to iterate over all potential '
            'templates. This is because the ChapterLoader is dynamic, '
            'and resolves additional templates at runtime.')


class JinjaPreprocessor(Preprocessor):
    """
    """
    _name = 'jinja'


    def on_run(self, book, renderer, context):

        for item in renderer.items:
            path = os.path.dirname(item.path)

            env = Environment(
                loader=ChoiceLoader([
                    DictLoader({ '__markdown__': item.raw_text }),
                    ChapterLoader(item.path)
                ]),
                autoescape=False
            )
            template = env.get_template('__markdown__')
            content = template.render(context.data)
            item.raw_text = content
