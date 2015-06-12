# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Feature from a parsed feature file.
"""

from radish.model import Model
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.step import Step


class Feature(Model):
    """
        Represent a Feature
    """

    def __init__(self, id, keyword, sentence, path, line):
        super(Feature, self).__init__(id, keyword, sentence, path, line)
        self.description = []
        self.scenarios = []

    @property
    def all_scenarios(self):
        """
            Returns all scenarios from the feature
            The ScenarioOutline scenarios will be extended to the normal scenarios
        """
        scenarios = []
        for scenario in self.scenarios:
            scenarios.append(scenario)
            if isinstance(scenario, (ScenarioOutline, ScenarioLoop)):
                scenarios.extend(scenario.scenarios)
        return scenarios

    def __str__(self):
        return "Feature: {} from {}:{}".format(self.sentence, self.path, self.line)

    def __repr__(self):
        return "<Feature: {} from {}:{}>".format(self.sentence, self.path, self.line)

    @property
    def state(self):
        """
            Returns the state of the scenario
        """
        for scenario in self.all_scenarios:
            if isinstance(scenario, (ScenarioOutline, ScenarioLoop)):  # skip scenario outlines
                continue

            if scenario.state in [Step.State.UNTESTED, Step.State.SKIPPED, Step.State.FAILED]:
                return scenario.state
        return Step.State.PASSED
