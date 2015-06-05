# -*- coding: utf-8 -*-

"""
    This module provides some functionality to diagnose thrown exceptions
"""


import sys
from functools import wraps
from colorful import colorful

from radish.exceptions import RadishError


def write_error(text):
    """
        Writes the given text to the console
    """
    print("{}: {}".format(colorful.bold_red("Error"), colorful.red(text)))


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
        except RadishError as e:
            write_error(e)
            abort(1)
        except Exception as e:  # pylint: disable=broad-except
            write_error(e)
            raise
            abort(2)

    return _decorator
