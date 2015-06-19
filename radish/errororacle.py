# -*- coding: utf-8 -*-

"""
    This module provides some functionality to diagnose thrown exceptions
"""


import sys
from functools import wraps
from colorful import colorful

from radish.terrain import world
from radish.exceptions import RadishError, FeatureFileSyntaxError, StepDefinitionNotFoundError, HookError


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
    write("{}: {}".format(colorful.bold_red("Error"), colorful.red(text)))


def write_failure(failure):
    """
        Writes the failure to the console
    """
    write("\n{}".format(colorful.red(failure.traceback)))


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
        except HookError as e:  # handle exception from hook
            write_error(e)
            write_failure(e.failure)
            abort(1)
        except FeatureFileSyntaxError as e:
            write("""You have a SyntaxError in your feature file!
Please have a look into the radish documentation to found out which
features radish supports and how you could use them:
Link: {}
                  """.format(__RADISH_DOC__))
            write_error(e)
            abort(1)
        except StepDefinitionNotFoundError as e:
            write("""There is no step defintion for '{}'.
All steps should be declared in a module located in {}.
For example you could do:

@step(r"{}")
def my_step(step):
    raise NotImplementedError("This step is not implemented yet")
            """.format(e.step.sentence, world.config.basedir, e.step.sentence))
            write_error(e)
            abort(1)
        except RadishError as e:
            write_error(e)
            abort(1)
        except KeyboardInterrupt:
            write("Aborted by the user...")
            abort(1)
        except Exception as e:  # pylint: disable=broad-except
            write_error(e)
            raise
            abort(2)

    return _decorator
