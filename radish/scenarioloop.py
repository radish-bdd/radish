# -*- coding: utf-8 -*-

"""
This module provides a Scenario type which represents a Scenario loop
"""

import copy

from .scenario import Scenario
from .iterationscenario import IterationScenario
from .stepmodel import Step


class ScenarioLoop(Scenario):
    """
        Represents a scenario loop
    """

    def __init__(
        self,
        id,
        keyword,
        iterations_keyword,
        sentence,
        path,
        line,
        parent,
        tags=None,
        preconditions=None,
        background=None,
    ):
        super(ScenarioLoop, self).__init__(
            id,
            keyword,
            sentence,
            path,
            line,
            parent,
            tags,
            preconditions,
            background=background,
        )
        self.iterations_keyword = iterations_keyword
        self.iterations = 0
        self.scenarios = []

    def build_scenarios(self):
        """
            Builds the scenarios for every iteration

            Note: This must be done before merging the steps
                  from the feature file with the step definitions
        """
        for i in range(self.iterations):
            scenario_id = self.id + i + 1
            background = None
            scenario = IterationScenario(
                scenario_id,
                self.keyword,
                "{0} - iteration {1}".format(self.sentence, i),
                self.path,
                self.line,
                self,
                i,
            )
            if self.background:
                background = self.background.create_instance(
                    parent=scenario, steps_runable=True
                )
                scenario.background = background

            for step_id, iteration_step in enumerate(self.steps):
                step = Step(
                    step_id + 1,
                    iteration_step.sentence,
                    iteration_step.path,
                    iteration_step.line,
                    scenario,
                    True,
                    context_class=iteration_step.context_class,
                )
                step.table_header = copy.copy(iteration_step.table_header)
                step.table_data = copy.copy(iteration_step.table_data)
                step.table = copy.copy(iteration_step.table)
                step.raw_text = copy.copy(iteration_step.raw_text)
                scenario.steps.append(step)
            self.scenarios.append(scenario)

    def after_parse(self):
        """
            Build looped scenarios
        """
        Scenario.after_parse(self)
        self.build_scenarios()
        self.complete = True
