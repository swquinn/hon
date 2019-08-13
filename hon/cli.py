# -*- coding: utf-8 -*-
"""
    hon.cli
    ~~~~~~~~~

    A simple command line application to run hon.
"""

from __future__ import print_function

import ast
import click
import os
import platform
import re
import sys
import traceback
from functools import update_wrapper

from . import __version__, create_app
from .helpers import get_debug_flag, get_load_dotenv

try:
    import dotenv
except ImportError:
    dotenv = None


class NoAppException(click.UsageError):
    """Raised if an application cannot be found or loaded."""


def honrc_filepath_option():
    """The ``--config`` option for specifying the path to the ``.honrc`` file.
    """
    def callback(ctx, param, value):
        state = ctx.ensure_object(ScriptInfo)
        state.honrc_filepath = value
        return value
    return click.Option(
        ['-c', '--config'],
        help='Specify the location of the .honrc config',
        callback=callback)


def debug_option():
    """The debug option."""
    def callback(ctx, param, value):
        state = ctx.ensure_object(ScriptInfo)
        # TODO: state.debug = value
        return value
    return click.Option(
        ['--debug', '--no-debug'],
        help='Enables or disables debugging output.',
        expose_value=False,
        callback=callback,
        is_flag=True,
        is_eager=False)


def version_option():
    """The version option."""

    def callback(ctx, param, value):
        """
        """
        if not value or ctx.resilient_parsing:
            return
        message = (
            'Python %(python)s\n'
            'Hon %(hon)s'
        )
        click.echo(message % {
            'python': platform.python_version(),
            'hon': __version__,
        }, color=ctx.color)
        ctx.exit()
    return click.Option(
        ['--version'],
        help='Show the version',
        expose_value=False,
        callback=callback,
        is_flag=True,
        is_eager=True)


def get_default_commands():
    """Return an iterable of all the default command functions.

    Instead of resolving these commands with all of the other imports, we're
    doing it here to avoid circular imports, since our commands are separated
    from this CLI module to increase legibility.
    """
    import hon.commands as cmd
    return (
        cmd.build_command, cmd.clean_command, cmd.init_command,
        cmd.serve_command, cmd.test_command, cmd.watch_command
    )


def with_context(f):
    """Wraps a callback so that it is guaranteed to have context."""
    @click.pass_context
    def decorator(__ctx, *args, **kwargs):
        with __ctx.ensure_object(ScriptInfo).load_app().app_context():
            return __ctx.invoke(f, *args, **kwargs)
    return update_wrapper(decorator, f)


class AppGroup(click.Group):
    """Extension of the regular click :class:`~click.Group`.
    
    The AppGroup changes the behavior of the :meth:`command` decorator so that
    it automatically wraps the functions in the :func:`with_context` decorator.

    Not to be confused with :class:`HonGroup`, which is an extension of this
    class.
    """

    def command(self, *args, **kwargs):
        """This works exactly like the method of the same name on a regular
        :class:`click.Group` but it wraps callbacks in :func:`with_appcontext`
        unless it's disabled by passing ``with_appcontext=False``.
        """
        wrap_for_ctx = kwargs.pop('with_context', True)
        def decorator(f):
            if wrap_for_ctx:
                f = with_context(f)
            return click.Group.command(self, *args, **kwargs)(f)
        return decorator

    def group(self, *args, **kwargs):
        """This works exactly like the method of the same name on a regular
        :class:`click.Group` but it defaults the group class to
        :class:`AppGroup`.
        """
        kwargs.setdefault('cls', AppGroup)
        return click.Group.group(self, *args, **kwargs)


class HonGroup(AppGroup):
    """Special subclass of the :class:`AppGroup` group that supports
    loading more commands from the configured Hon app.  Normally a
    developer does not have to interface with this class but there are
    some very advanced use cases for which it makes sense to create an
    instance of this.

    For information as of why this is useful see :ref:`custom-scripts`.

    :param add_default_commands: if this is True then the default run and
        shell commands wil be added.
    :param add_version_option: adds the ``--version`` option.
    :param create_app: an optional callback that is passed the script info and
        returns the loaded app.
    :param load_dotenv: Load the nearest :file:`.env` and :file:`.honenv`
        files to set environment variables. Will also change the working
        directory to the directory containing the first file found.
    :param set_debug_flag: Set the app's debug flag based on the active
        environment
    """

    def __init__(self, add_default_commands=True, add_debug_options=True,
            add_honrc_filepath_option=True, add_version_option=True,
            load_dotenv=True, set_debug_flag=True, **extra):
        #: Pop the params, if any were defined for this group, and then check
        #: to see if we should be adding the version option.
        params = list(extra.pop('params', None) or ())
        if add_version_option:
            params.append(version_option())
        
        if add_debug_options:
            params.append(debug_option())

        if add_honrc_filepath_option:
            params.append(honrc_filepath_option())

        #: Initialize the underlying app command group with the params and
        #: anything else in the **extra kwargs.
        #super(HonGroup, self).__init__(params=params, **extra)
        AppGroup.__init__(self, params=params, **extra)
        self.load_dotenv = load_dotenv
        self.set_debug_flag = set_debug_flag

        if add_default_commands:
            default_commands = get_default_commands()
            for cmd in default_commands:
                self.add_command(cmd)

        self._loaded_plugin_commands = False

    def _load_plugin_commands(self):
        if self._loaded_plugin_commands:
            return
        try:
            import pkg_resources
        except ImportError:
            self._loaded_plugin_commands = True
            return

        for ep in pkg_resources.iter_entry_points('hon.commands'):
            self.add_command(ep.load(), ep.name)
        self._loaded_plugin_commands = True

    def get_command(self, ctx, name):
        self._load_plugin_commands()

        # We load built-in commands first as these should always be the
        # same no matter what the app does.
        rv = AppGroup.get_command(self, ctx, name)
        if rv is not None:
            return rv

    def list_commands(self, ctx):
        #self._load_plugin_commands()

        # The commands available is the list of both the application (if
        # available) plus the builtin commands.
        rv = set(click.Group.list_commands(self, ctx))
        return sorted(rv)

    def main(self, *args, **kwargs):
        """Overrides the behavior of the group's :func:`main` method.
        """
        if get_load_dotenv(self.load_dotenv):
            load_dotenv()

        obj = kwargs.get('obj')
        if obj is None:
            obj = ScriptInfo(set_debug_flag=self.set_debug_flag)

        kwargs['obj'] = obj
        kwargs.setdefault('auto_envvar_prefix', 'HON')
        return super(HonGroup, self).main(*args, **kwargs)


#: TODO: This object is what maintains state, sooooo... let's us it!
class ScriptInfo(object):
    """Helper object to deal with Hon applications.
    
    Used internally for the dispatching commands to click. Typically it's
    created automatically by the :class:`HonGroup` but you can also manually
    create it and pass it onwards as click object.

    Inspired by Flask's own ScriptInfo.
    """

    def __init__(self, set_debug_flag=True):
        self.set_debug_flag = set_debug_flag
        self._loaded_app = None
        self.honrc_filepath = None
        self.build_renderers = {}

    def load_app(self):
        """Loads the hon app (if not yet loaded) and returns it.
        
        Calling this multiple times will just result in the already loaded app
        to be returned.
        """
        __traceback_hide__ = True

        if self._loaded_app is not None:
            return self._loaded_app

        honrc_filepath = self.honrc_filepath
        if honrc_filepath:
            honrc_filepath = os.path.abspath(honrc_filepath)

        app = create_app(honrc_filepath=honrc_filepath)
        if not app:
            raise NoAppException('Could not instantiate the Hon application.')

        # TODO: This is overwriting whatever debug flag we would set above.
        if self.set_debug_flag:
            #: Update the app's debug flag through the descriptor so that
            #: other values repopulate as well.
            app.debug = get_debug_flag()

        self._loaded_app = app
        return app


def load_dotenv(path=None):
    """Load "dotenv" files in order of precedence to set environment variables.

    If an env var is already set it is not overwritten, so earlier files in the
    list are preferred over later files.

    Changes the current working directory to the location of the first file
    found, with the assumption that it is in the top level project directory
    and will be where the Python path should import local packages from.

    This is a no-op if `python-dotenv`_ is not installed.

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    :param path: Load the file at this location instead of searching.
    :return: ``True`` if a file was loaded.
    """
    if dotenv is None:
        if path or os.path.isfile('.env') or os.path.isfile('.honenv'):
            click.secho(
                ' * Tip: There are .env or .honenv files present.'
                ' Do "pip install python-dotenv" to use them.',
                fg='yellow')
        return

    if path is not None:
        return dotenv.load_dotenv(path)

    new_dir = None

    for name in ('.env', '.honenv'):
        path = dotenv.find_dotenv(name, usecwd=True)

        if not path:
            continue

        if new_dir is None:
            new_dir = os.path.dirname(path)

        dotenv.load_dotenv(path)

    if new_dir and os.getcwd() != new_dir:
        os.chdir(new_dir)

    return new_dir is not None  # at least one file was located and loaded


cli = HonGroup(help="Transforms markdown files into a book.")


def main(as_module=False):
    """Proxy for the CLI's main entry point, which is on the HonGroup."""
    args = sys.argv[1:]

    if as_module:
        this_module = 'hon'

        if sys.version_info < (2, 7):
            this_module += '.cli'

        name = 'python -m ' + this_module

        # Python rewrites "python -m hon" to the path to the file in argv.
        # Restore the original command so that the reloader works.
        sys.argv = ['-m', this_module] + args
    else:
        name = None

    cli.main(args=args)


if __name__ == '__main__':
    main(as_module=True)