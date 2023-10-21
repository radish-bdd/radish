# -*- coding: utf-8 -*-

"""
This module provides some functionality to diagnose thrown exceptions
"""

import sys
from functools import wraps


from .terrain import world
from .exceptions import (
    RadishError,
    FeatureFileSyntaxError,
    StepDefinitionNotFoundError,
    HookError,
    SameStepError,
)
from .utils import Failure

from .printer import Printer, styled_text
printer = Printer()

__RADISH_DOC__ = "https://github.com/radish-bdd/radish"


def write_error(text):
    """
    Writes the given text to the console
    """
    printer.write("{0}: {1}".format(styled_text("Error", "bold red"), styled_text(text, "red")))


def write_failure(failure):
    """
    Writes the failure to the console
    """
    printer.write("\n{0}".format(styled_text(failure.traceback, "red")))


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
        printer.write("Aborted by the user...")
        abort(1)
    else:
        write_error(exception)
        write_failure(Failure(exception))
        abort(2)
