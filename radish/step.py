# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Step
"""

import re

from radish.exceptions import StepRegexError
from radish.stepregistry import StepRegistry


class Step(object):
    """
        Represents a step
    """

    def __init__(self, sentence, path, line):
        self.sentence = sentence
        self.path = path
        self.line = line
        self.table = []
        self.definition_func = None
        self.arguments = None


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
            re.compile(regex)
        except re.error as e:
            raise StepRegexError(regex, func.__name__, e)
        else:
            StepRegistry().register(regex, func)
        return func
    return _decorator

given = lambda regex: step("Given {}".format(regex))  # pylint: disable=invalid-name
when = lambda regex: step("When {}".format(regex))  # pylint: disable=invalid-name
then = lambda regex: step("Then {}".format(regex))  # pylint: disable=invalid-name
