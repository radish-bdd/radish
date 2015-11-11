# -*- coding: utf-8 -*-

"""
    This module provides some functionality to diagnose thrown exceptions
"""


import sys
from functools import wraps
from colorful import colorful

from .terrain import world
from .exceptions import RadishError, FeatureFileSyntaxError, StepDefinitionNotFoundError, HookError, SameStepError


__RADISH_DOC__ = "https://github.com/radish-bdd/radish"


def write(text):
    """
        Writes the given text to the console
    """
    print(text)


def write_error(text):
    """
        Writes the given text to the console
    """
    write("{0}: {1}".format(colorful.bold_red("Error"), colorful.red(text)))


def write_failure(failure):
    """
        Writes the failure to the console
    """
    write("\n{0}".format(colorful.red(failure.traceback)))


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
    if isinstance(exception, HookError):  # handle exception from hook
        write_error(exception)
        write_failure(exception.failure)
        abort(1)
    elif isinstance(exception, FeatureFileSyntaxError):
        write_error(exception)
        write("\nError Oracle says:")
        write("""You have a SyntaxError in your feature file!
Please have a look into the radish documentation to found out which
features radish supports and how you could use them:
Link: {0}
              """.format(__RADISH_DOC__))
        abort(1)
    elif isinstance(exception, StepDefinitionNotFoundError):
        write_error(exception)
        write("\nError Oracle says:")
        write("""There is no step defintion for '{0}'.
All steps should be declared in a module located in {1}.
For example you could do:

@step(r"{2}")
def my_step(step):
    raise NotImplementedError("This step is not implemented yet")
        """.format(exception.step.sentence, world.config.basedir, exception.step.sentence))
        abort(1)
    elif isinstance(exception, SameStepError):
        write_error(exception)
        write("\nError Oracle says:")
        write("""You have defined two step definitions with the same Regular Expression.
This is invalid since radish does not know which one is the one to go with.
If you have two similar step definition expressions but ones sentence is a subset of the other
you may want to add a $ to mark the sentence's end - take care of the code order - first comes first serves.
              """)
        abort(1)
    elif isinstance(exception, RadishError):
        write_error(exception)
        abort(1)
    elif isinstance(exception, KeyboardInterrupt):
        write("Aborted by the user...")
        abort(1)
    else:
        write_error(str(exception))
        abort(2)
