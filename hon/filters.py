import os
from jinja2 import contextfilter


@contextfilter
def relative_path(context, path):
    """Resolve the path, relative to the output root.
    """
    output_root = context['_root']

    page = context.get('page', {})
    page_path = page.get('path')
    page_dir = os.path.dirname(page_path)

    _target = os.path.abspath(os.path.join(output_root, path))
    _target_path = os.path.relpath(_target, start=os.path.dirname(page_path))
    return _target_path
