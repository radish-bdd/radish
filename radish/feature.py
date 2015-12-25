# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Feature from a parsed feature file.
"""

from .model import Model
from .scenariooutline import ScenarioOutline
from .scenarioloop import ScenarioLoop
from .stepmodel import Step
from .terrain import world


class Feature(Model):
    """
        Represent a Feature
    """

    def __init__(self, id, keyword, sentence, path, line, tags=None):
        super(Feature, self).__init__(id, keyword, sentence, path, line, None, tags)
        self.description = []
        self.scenarios = []
        self.context = self.Context()

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

    @property
    def constants(self):
        """
            Returns all constants
        """
        return self.context.constants

    def __str__(self):
        return "Feature: {0} from {1}:{2}".format(self.sentence, self.path, self.line)

    def __repr__(self):
        return "<Feature: {0} from {1}:{2}>".format(self.sentence, self.path, self.line)

    def __iter__(self):
        """
            Returns an iterator for the scenario of this feature
        """
        return iter(self.scenarios)

    def __contains__(self, sentence):
        """
            Checks if the given scenario sentence is from a scenario of this feature

            :param str sentence: the scenario sentence to search
        """
        return any(s for s in self.scenarios if s.sentence == sentence)

    def __getitem__(self, sentence):
        """
            Returns the scenario with the given sentence

            :param str sentence: the scenario sentence to search
        """
        return next((s for s in self.scenarios if s.sentence == sentence), None)

    @property
    def state(self):
        """
            Returns the state of the scenario
        """
        for scenario in self.all_scenarios:
            if isinstance(scenario, (ScenarioOutline, ScenarioLoop)):  # skip scenario outlines
                continue

            if not scenario.has_to_run(world.config.scenarios, world.config.feature_tags, world.config.scenario_tags):
                continue

            if scenario.state is not Step.State.PASSED:
                return scenario.state
        return Step.State.PASSED

    def has_to_run(self, scenario_choice, feature_tags, scenario_tags):
        """
            Returns wheiter the feature has to run or not
        """
        if not scenario_choice and not feature_tags and not scenario_tags:
            return True

        in_choice = False
        if scenario_choice:
            in_choice = any(s for s in self.scenarios if s.absolute_id in scenario_choice)

        in_tags = False
        if feature_tags:
            in_tags = any(t for t in self.tags if t.name in feature_tags)

        scenario_to_run = any(s for s in self.scenarios if s.has_to_run(scenario_choice, feature_tags, scenario_tags))

        return in_choice or in_tags or scenario_to_run
