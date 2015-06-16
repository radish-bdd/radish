# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Step
"""

import re

from radish.model import Model
from radish.exceptions import RadishError, StepRegexError
from radish.terrain import world
from radish.stepregistry import StepRegistry
from radish.matcher import Matcher
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

    def __init__(self, id, sentence, path, line, parent, runable):
        super(Step, self).__init__(id, None, sentence, path, line, parent)
        self.table = []
        self.definition_func = None
        self.arguments = None
        self.state = Step.State.UNTESTED
        self.failure = None
        self.runable = runable

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
        if not self.runable:
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
            self.failure = utils.Failure(e)
        else:
            self.state = Step.State.PASSED
        return self.state

    def debug(self):
        """
            Debugs the step
        """
        if not self.runable:
            self.state = Step.State.UNTESTED
            return self.state

        self._validate()

        pdb = utils.get_debugger()

        try:
            pdb.runcall(self.definition_func, self, *self.arguments.groups(), **self.arguments.groupdict())
        except Exception as e:  # pylint: disable=broad-except
            self.state = Step.State.FAILED
            self.failure = utils.Failure(e)
        else:
            self.state = Step.State.PASSED
        return self.state

    def skip(self):
        """
            Skips the step
        """
        self.state = Step.State.SKIPPED

    def behave_like(self, sentence):
        """
            Make step behave like another one

            :param string sentence: the sentence of the step to behave like
        """
        # check if this step has already failed from a previous behave_like call
        if self.state is Step.State.FAILED:
            return

        # create step according to given sentence
        new_step = Step(None, sentence, self.path, self.line, self, True)
        Matcher.merge_step(new_step, StepRegistry().steps)

        # run or debug step
        if world.config.debug_steps:
            new_step.debug()
        else:
            new_step.run()

        # re-raise exception if the failed
        if new_step.state is Step.State.FAILED:
            raise new_step.failure.exception


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
