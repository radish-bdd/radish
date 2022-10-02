# -*- coding: utf-8 -*-

"""
This module provides a registry for all custom steps which were decorated with the @step-decorator.
"""

import re
import inspect
from singleton import singleton

from .exceptions import RadishError, SameStepError, StepRegexError
from .compat import re_pattern


@singleton()
class StepRegistry(object):
    """
    Represents the step registry
    """

    def __init__(self):
        self._steps = {}

    def register(self, pattern, func):
        """
        Registers a given regex with the given step function.
        """
        if pattern in self._steps:
            raise SameStepError(pattern, self._steps[pattern], func)

        self._steps[pattern] = func

    def get_pattern(self, func):
        """
        Get step pattern from a given function.
        """
        return next((k for k, v in self._steps.items() if v == func), "Unknown")

    def register_object(self, steps_object):
        """
        Registers all public methods from the given object as steps.
        The step regex must be in the first line of the docstring

        :param instance steps_object: the object with step definition methods
        """
        ignore = getattr(steps_object, "ignore", [])
        for attr in dir(steps_object):
            if attr in ignore or not inspect.ismethod(
                getattr(steps_object, attr)
            ):  # attribute should be ignored
                continue

            step_definition = getattr(steps_object, attr)
            step_regex = self._extract_regex(step_definition)
            self.register(step_regex, step_definition)

        return steps_object

    @staticmethod
    def _extract_regex(func):
        """
        Extracts a step regex from the docstring of the given func

        :param function func: the step definition function
        """
        docstr = func.__doc__.strip() if func.__doc__ else None
        if not docstr:
            raise RadishError(
                "Step definition '{0}' from class must have step regex in docstring".format(
                    func.__name__
                )
            )

        regex = docstr.splitlines()[0]
        try:
            re.compile(regex)
        except re.error as e:
            raise StepRegexError(regex, func.__name__, e)

        return regex

    def clear(self):
        """
            Clears all registered steps
        """
        self._steps = {}

    @property
    def steps(self):
        """
            Returns all registered steps
        """
        return self._steps


def step(pattern):
    """
        Step decorator for custom steps

        :param string regex: this is the regex to match the steps in the feature file

        :returns: the decorated function
        :rtype: function
    """

    def _decorator(func):
        """
            Represents the actual decorator
        """
        StepRegistry().register(pattern, func)
        return func

    return _decorator


def steps(cls):
    """
        Decorator for classes with step definitions inside
    """
    old_cls_init = getattr(cls, "__init__")

    # ignore new_cls_init method
    if not hasattr(cls, "ignore"):
        cls.ignore = []

    cls.ignore.append("__init__")

    def new_cls_init(self, *args, **kwargs):
        """
            New __init__ method for the given class which calls the old __init__ method
            and registers the steps
        """
        old_cls_init(self, *args, **kwargs)

        # register functions as step
        StepRegistry().register_object(self)

    setattr(cls, "__init__", new_cls_init)
    # create instance in order to register object in step registry
    cls()
    return cls


def given(pattern):
    """
        Step decorator prefixed with the Given-keyword.
    """
    if isinstance(pattern, re_pattern):  # pylint: disable=protected-access
        return step(re.compile(r"Given {0}".format(pattern.pattern)))
    return step("Given {0}".format(pattern))


def when(pattern):
    """
        Step decorator prefixed with the When-keyword.
    """
    if isinstance(pattern, re_pattern):  # pylint: disable=protected-access
        return step(re.compile(r"When {0}".format(pattern.pattern)))
    return step("When {0}".format(pattern))


def then(pattern):
    """
        Step decorator prefixed with the Then-keyword.
    """
    if isinstance(pattern, re_pattern):  # pylint: disable=protected-access
        return step(re.compile(r"Then {0}".format(pattern.pattern)))
    return step("Then {0}".format(pattern))
