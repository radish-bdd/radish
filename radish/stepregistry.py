# -*- coding: utf-8 -*-

"""
    This module provides a registry for all custom steps which were decorated with the @step-decorator.
"""

import re
import inspect
import parse
from singleton import singleton

from radish.argexpregistry import ArgumentExpression
from radish.exceptions import RadishError, SameStepError, StepRegexError


@singleton()
class StepRegistry(object):
    """
        Represents the step registry
    """
    def __init__(self):
        self.clear()

    def register(self, regex, func):
        """
            Registers a given regex with the given step function.
        """
        if regex in self._steps:
            raise SameStepError(regex, self._steps[regex], func)

        self._steps[regex] = func

    def register_object(self, steps_object):
        """
            Registers all public methods from the given object as steps.
            The step regex must be in the first line of the docstring

            :param instance steps_object: the object with step definition methods
        """
        ignore = getattr(steps_object, "ignore", [])
        for attr in dir(steps_object):
            if attr in ignore or not inspect.ismethod(getattr(steps_object, attr)):  # attribute should be ignored
                continue

            step_definition = getattr(steps_object, attr)
            step_regex = self._extract_regex(step_definition)
            self.register(step_regex, step_definition)

        return steps_object

    def _extract_regex(self, func):
        """
            Extracts a step regex from the docstring of the given func

            :param function func: the step definition function
        """
        docstr = func.__doc__.strip()
        if not docstr:
            raise RadishError("Step definition '{}' from class must have step regex in docstring".format(func.__name__))

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


def step(regex):
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
        try:
            if not isinstance(regex, ArgumentExpression):
                re.compile(regex)
        except re.error as e:
            raise StepRegexError(regex, func.__name__, e)
        else:
            StepRegistry().register(regex, func)
        return func
    return _decorator


def steps(cls):
    """
        Decorator for classes with step definitions inside
    """
    old_cls_init = getattr(cls, "__init__")

    def new_cls_init(self, *args, **kwargs):
        """
            New __init__ method for the given class which calls the old __init__ method
            and registers the steps
        """
        old_cls_init(self, *args, **kwargs)

        # register functions as step
        StepRegistry().register_object(self)

    setattr(cls, "__init__", new_cls_init)
    return cls

given = lambda regex: step("Given {}".format(regex))  # pylint: disable=invalid-name
when = lambda regex: step("When {}".format(regex))  # pylint: disable=invalid-name
then = lambda regex: step("Then {}".format(regex))  # pylint: disable=invalid-name
