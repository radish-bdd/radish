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

    def __init__(self, absolute_id, id, keyword, sentence, path, line, parent, tags=None, preconditions=None):
        super(Scenario, self).__init__(id, keyword, sentence, path, line, parent, tags)
        self.absolute_id = absolute_id
        self.preconditions = preconditions or []
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
    def all_steps(self):
        """
            Returns all steps from all preconditions in the correct order
        """
        steps = []
        for precondition in self.preconditions:
            steps.extend(precondition.all_steps)
        steps.extend(self.steps)
        return steps

    @property
    def failed_step(self):
        """
            Returns the first failed step
        """
        for step in self.steps:
            if step.state == Step.State.FAILED:
                return step
        return None

    def has_to_run(self, scenario_choice, feature_tags, scenario_tags):
        """
            Returns wheiter the scenario has to run or not

            :param list scenario_choice: the scenarios to run. If None all will run
        """
        if not scenario_choice and not feature_tags and not scenario_tags:
            return True

        in_choice = self.absolute_id in (scenario_choice or [])

        in_tags = False
        if scenario_tags:
            in_tags = any(t for t in self.tags if t.name in scenario_tags)

        feature_has_to_run = False
        if feature_tags:
            feature_has_to_run = any(t for t in self.parent.tags if t in feature_tags)

        return in_choice or in_tags or feature_has_to_run
