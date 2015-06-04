# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Feature from a parsed feature file.
"""

from radish.scenariooutline import ScenarioOutline


class Feature(object):
    """
        Represent a Feature
    """

    def __init__(self, sentence, path, line):
        self.sentence = sentence
        self.path = path
        self.line = line
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
            if isinstance(scenario, ScenarioOutline):
                scenarios.extend(scenario.scenarios)
        return scenarios

    def __str__(self):
        return "Feature: {} from {}:{}".format(self.sentence, self.path, self.line)

    def __repr__(self):
        return "<Feature: {} from {}:{}>".format(self.sentence, self.path, self.line)
