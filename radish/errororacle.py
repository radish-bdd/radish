"""
    This module provides some functionality to diagnose thrown exceptions
"""


import sys
from functools import wraps

import colorful

from .exceptions import (
    RadishError,
    HookError,
)
from .utils import Failure


__RADISH_DOC__ = "https://github.com/radish-bdd/radish"


def write_error(text):
    """
        Writes the given text to the console
    """
    print("{0}: {1}".format(colorful.bold_red("Error"), colorful.red(text)))


def write_failure(failure):
    """
        Writes the failure to the console
    """
    print("\n{0}".format(colorful.red(failure.traceback)))


def abort(return_code):
    """
        Aborts the program with the given return_code
    """
    sys.exit(return_code)


def error_oracle(func):
    """
        Decorator to diagnose thrown exceptions
    """

    @wraps(func)
    def _decorator(*args, **kwargs):
        """
            The actual decorator
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            handle_exception(e)

    return _decorator


def catch_unhandled_exception(exc_type, exc_value, traceback):
    """
        Catch all unhandled exceptions
    """
    handle_exception(exc_value)


def handle_exception(exception):
    """
        Handle the given exception

        This will print more information about the given exception

        :param Exception exception: the exception to handle
    """
    if isinstance(exception, HookError):
        write_error(exception)
        write_failure(exception.failure)
        abort(1)
    elif isinstance(exception, RadishError):
        write_error(exception)
        abort(1)
    elif isinstance(exception, KeyboardInterrupt):
        print("Aborted by the user...")
        abort(1)
    else:
        write_error(exception)
        write_failure(Failure(exception))
        abort(2)
