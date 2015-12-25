# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Scenario
"""

from .model import Model
from .stepmodel import Step


class Scenario(Model):
    """
        Represents a Scenario
    """
    def __init__(self, id, keyword, sentence, path, line, parent, tags=None, preconditions=None):
        super(Scenario, self).__init__(id, keyword, sentence, path, line, parent, tags)
        self.absolute_id = None
        self.preconditions = preconditions or []
        self.steps = []
        self.context = self.Context()

    @property
    def state(self):
        """
            Returns the state of the scenario
        """
        for step in self.steps:
            if step.state is not Step.State.PASSED:
                return step.state
        return Step.State.PASSED

    @property
    def constants(self):
        """
            Returns all constants
        """
        constants = self.context.constants
        for name, value in constants:
            for parent_name, parent_value in self.parent.constants:
                value = value.replace("${{{0}}}".format(parent_name), parent_value)
        constants.extend(self.parent.constants)
        return constants

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
            feature_has_to_run = any(t for t in self.parent.tags if t.name in feature_tags)

        return in_choice or in_tags or feature_has_to_run

    def after_parse(self):
        """
            This method is called after the scenario is completely parsed.
            Actions to do:
                * number steps
                * fix parent of precondition steps
        """
        for step_id, step in enumerate(self.all_steps, start=1):
            step.id = step_id
            if step.parent != self:
                step.as_precondition = step.parent
                step.parent = self
