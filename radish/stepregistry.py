# -*- coding: utf-8 -*-

"""
    This module provides a registry for all custom steps which were decorated with the @step-decorator.
"""

from singleton import singleton

from radish.exceptions import SameStepError


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
