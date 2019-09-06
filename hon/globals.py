from functools import partial
from .local import LocalStack, LocalProxy

_app_ctx_err_msg = '''\
Working outside of application context.
This typically means that you attempted to use functionality that needed
to interface with the current application object in some way. To solve
this, set up an application context with app.app_context().  See the
documentation for more information.\
'''


def _lookup_app_object(name):
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return getattr(top, name)


def _find_app():
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return top.app


_app_ctx_stack = LocalStack()
current_app = LocalProxy(_find_app)
g = LocalProxy(partial(_lookup_app_object, 'g'))
