import logging
import sys

#: Log messages to stdout with the format:
#:   [%(asctime)s] %(levelname)s in %(module)s: %(message)s
default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)

# We assign the default handler to the root logger, this prevents other code
# from initializing a root logger which can result in double logging. [SWQ]
logging.basicConfig(handlers=(default_handler, ))


def has_level_handler(logger):
    """Check if there is a handler in the logging.

    Returns ``True`` if there is a handler in the logging chain that will handle
    the given logger's :meth:`effective level <~logging.Logger.getEffectiveLevel>`.
    """
    level = logger.getEffectiveLevel()
    current = logger

    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True
        if not current.propagate:
            break
        current = current.parent
    return False


def create_logger(app):
    """Get the ``'hon.app'`` logger and configure it if needed.

    When :attr:`~hon.Hon.debug` is enabled, set the logger level to
    :data:`logging.DEBUG` if it is not set.

    If there is no handler for the logger's effective level, add a
    :class:`~logging.StreamHandler` for :func:`~sys.stdout` with a basic
    format.
    """
    logger = logging.getLogger("hon")

    if app.debug and logger.level == logging.NOTSET:
        logger.setLevel(logging.DEBUG)

    if not has_level_handler(logger):
        logger.addHandler(default_handler)
    return logger