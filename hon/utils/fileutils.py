"""
"""
import os
import shutil
from fnmatch import fnmatch

CURRENT_DIRECTORY = '.'


def _match(filepath, pattern):
    """
    """
    for p in tuple(pattern):
        if fnmatch(filepath, p):
            return True
    return False
    

def is_current_directory(path):
    """
    """
    return path == CURRENT_DIRECTORY


#: TODO: Add file globbing support to check to see if include/exclude patterns are met
def copy_from(source, destination, make_dirs=True, include='*', exclude=None):
    """

    An include pattern can be specified. The includsion pattern can be a simple
    string pattern, e.g. ``'*.js'``, indicating that all files with the ``.js``
    extension should be included. It may also be a collection of patterns,
    indicating that files which match any of the supplied patterns should be
    included e.g.::

        include=[
            '*.js',
            '*.css',
        ]

    If both inclusion and exclusion patterns are supplied, the inclusion pattern
    is evaluated first. The exclusion pattern is then applied to the already
    filtered list of 
    
    """
    if not os.path.isdir(source):
        raise FileNotFoundError('Source must be a directory.')

    if exclude is None:
        exclude = tuple()

    for dirpath, _, filenames in os.walk(source):
        relative_dir = os.path.relpath(dirpath, start=source)
        output_dir = os.path.join(destination, relative_dir)

        for filename in filenames:
            copy_file = os.path.join(dirpath, filename)
            included = _match(copy_file, pattern=include)
            excluded = _match(copy_file, pattern=exclude)

            if os.path.isfile(copy_file) and included and not excluded:
                #: Only create output directories if they don't already exist
                #: and we're going to write something to them. [SWQ]
                if not is_current_directory(relative_dir) and not os.path.isdir(output_dir) and make_dirs:
                    os.makedirs(output_dir, exist_ok=True)

                output_file = os.path.join(output_dir, filename)
                shutil.copyfile(copy_file, output_file)
