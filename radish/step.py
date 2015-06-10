# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Step
"""

import re
import sys
import traceback

from radish.model import Model
from radish.exceptions import RadishError, StepRegexError
from radish.stepregistry import StepRegistry
import radish.utils as utils


class Step(Model):
    """
        Represents a step
    """
    class State(object):
        """
            Represents the step state

            FIXME: for the python3 version this should be an Enum
        """
        UNTESTED = "untested"
        SKIPPED = "skipped"
        PASSED = "passed"
        FAILED = "failed"

    class Failure(object):
        """
            Represents the fail reason for a step
        """
        def __init__(self, exception):
            """
                Initalizes the Step failure with a given Exception

                :param Exception exception: the exception shrown in the step
            """
            self.exception = exception
            self.reason = unicode(str(exception), "utf-8")
            self.traceback = traceback.format_exc()
            self.name = exception.__class__.__name__
            traceback_info = traceback.extract_tb(sys.exc_info()[2])[-1]
            self.filename = traceback_info[0]
            self.line = int(traceback_info[1])

    def __init__(self, id, sentence, path, line, parent, outlined):
        super(Step, self).__init__(id, None, sentence, path, line, parent)
        self.table = []
        self.definition_func = None
        self.arguments = None
        self.state = Step.State.UNTESTED
        self.failure = None
        self.outlined = outlined

    def _validate(self):
        """
            Checks if the step is valid to run or not
        """

        if not self.definition_func or not callable(self.definition_func):
            raise RadishError("The step '{}' does not have a step definition".format(self.sentence))

        if not self.arguments:
            raise RadishError("The step '{}' does not have a match with registered steps".format(self.sentence))

    def run(self):
        """
            Runs the step.
        """
        if self.outlined:
            self.state = Step.State.UNTESTED
            return self.state

        self._validate()

        keyword_arguments = self.arguments.groupdict()
        try:
            if keyword_arguments:
                self.definition_func(self, **keyword_arguments)  # pylint: disable=not-callable
            else:
                self.definition_func(self, *self.arguments.groups())  # pylint: disable=not-callable
        except Exception as e:  # pylint: disable=broad-except
            self.state = Step.State.FAILED
            self.failure = Step.Failure(e)
        else:
            self.state = Step.State.PASSED
        return self.state

    def debug(self):
        """
            Debugs the step
        """
        if self.outlined:
            self.state = Step.State.UNTESTED
            return self.state

        self._validate()

        pdb = utils.get_debugger()

        try:
            pdb.runcall(self.definition_func, self, *self.arguments.groups(), **self.arguments.groupdict())
        except Exception as e:  # pylint: disable=broad-except
            self.state = Step.State.FAILED
            self.failure = Step.Failure(e)
        else:
            self.state = Step.State.PASSED
        return self.state

    def skip(self):
        """
            Skips the step
        """
        self.state = Step.State.SKIPPED


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
