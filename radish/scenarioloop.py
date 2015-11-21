# -*- coding: utf-8 -*-

"""
    This module provides a Scenario type which represents a Scenario loop
"""

from .scenario import Scenario
from .iterationscenario import IterationScenario
from .stepmodel import Step


class ScenarioLoop(Scenario):
    """
        Represents a scenario loop
    """
    def __init__(self, id, keyword, iterations_keyword, sentence, path, line, parent, tags=None, preconditions=None):
        super(ScenarioLoop, self).__init__(id, keyword, sentence, path, line, parent, tags, preconditions)
        self.iterations_keyword = iterations_keyword
        self.iterations = 0
        self.scenarios = []

    def build_scenarios(self):
        """
            Builds the scenarios for every iteration

            Note: This must be done before mering the steps from the feature file with the step definitions
        """
        for i in range(self.iterations):
            scenario_id = self.id + i + 1
            scenario = IterationScenario(scenario_id, self.keyword, "{0} - iteration {1}".format(self.sentence, i), self.path, self.line, self, i)
            for step_id, iteration_step in enumerate(self.steps):
                step = Step(step_id + 1, iteration_step.sentence, iteration_step.path, iteration_step.line, scenario, True)
                scenario.steps.append(step)
            self.scenarios.append(scenario)

    def after_parse(self):
        """
            Build looped scenarios
        """
        Scenario.after_parse(self)
        self.build_scenarios()
