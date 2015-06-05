# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Scenario
"""

from radish.model import Model
from radish.step import Step


class Scenario(Model):
    """
        Represents a Scenario
    """

    def __init__(self, id, keyword, sentence, path, line, parent):
        super(Scenario, self).__init__(id, keyword, sentence, path, line, parent)
        self.steps = []

    @property
    def state(self):
        """
            Returns the state of the scenario
        """
        for step in self.steps:
            if step.state in [Step.State.UNTESTED, Step.State.SKIPPED, Step.State.FAILED]:
                return step.state
        return Step.State.PASSED

    @property
    def failed_step(self):
        """
            Returns the first failed step
        """
        for step in self.steps:
            if step.state == Step.State.FAILED:
                return step
        return None
