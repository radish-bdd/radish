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

    def __init__(self, absolute_id, id, keyword, sentence, path, line, parent):
        super(Scenario, self).__init__(id, keyword, sentence, path, line, parent)
        self.absolute_id = absolute_id
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

    def has_to_run(self, scenario_choice):
        """
            Returns wheiter the scenario has to run or not

            :param list scenario_choice: the scenarios to run. If None all will run
        """
        if not scenario_choice:
            return True

        if self.absolute_id in scenario_choice:
            return True

        return False
