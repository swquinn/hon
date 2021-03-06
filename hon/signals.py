# -*- coding: utf-8 -*-
"""
    hon.signals
    ~~~~~~~~~~~

    Implements signals based on blinker if available, otherwise
    falls silently back to a noop.
"""

signals_available = False
try:
    from blinker import Namespace
    signals_available = True
except ImportError:
    class Namespace(object):
        def signal(self, name, doc=None):
            return _FakeSignal(name, doc)

    class _FakeSignal(object):
        """If blinker is unavailable, create a fake class with the same
        interface that allows sending of signals but will fail with an
        error on anything else.  Instead of doing anything on send, it
        will just ignore the arguments and do nothing instead.
        """

        def __init__(self, name, doc=None):
            self.name = name
            self.__doc__ = doc
        def _fail(self, *args, **kwargs):
            raise RuntimeError('signalling support is unavailable '
                               'because the blinker library is '
                               'not installed.')
        send = lambda *a, **kw: None
        connect = disconnect = has_receivers_for = receivers_for = \
            temporarily_connected_to = connected_to = _fail
        del _fail

#: The namespace for code signals.  If you are not Hon code, do
#: not put signals in here.  Create your own namespace instead.
_signals = Namespace()


#: Core signals.
#: For usage examples grep the source code or consult the API documentation in
#: docs/signals.md
appcontext_tearing_down = _signals.signal('appcontext-tearing-down')
appcontext_pushed = _signals.signal('appcontext-pushed')
appcontext_popped = _signals.signal('appcontext-popped')

# before build book:
#   This signal is triggered before the build process for a book is started.
before_build = _signals.signal('before-build')

init_renderer = _signals.signal('init-renderer')
before_render = _signals.signal('before-render')
before_render_page = _signals.signal('before-render-page')
generate_assets = _signals.signal('generate-assets')
on_render_page = _signals.signal('on-render-page')
after_render_page = _signals.signal('after-render-page')
finish_render = _signals.signal('finish-render')
after_render = _signals.signal('after-render')

# after-build:
#   This signal is triggered after the book has completely built.
after_build = _signals.signal('after-build')
