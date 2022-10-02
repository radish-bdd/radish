# -*- coding: utf-8 -*-

"""
This module provides a class to represent one Scenario Outline Example
"""

from .scenario import Scenario


class ExampleScenario(Scenario):
    """
    Represents one example scenario from a ScenarioOutline
    """

    def __init__(
        self, id, keyword, sentence, path, line, parent, example, background=None
    ):
        super(ExampleScenario, self).__init__(
            id, keyword, sentence, path, line, parent, background=background
        )
        self.example = example

    def has_to_run(self, scenario_choice):
        """
        Returns wheiter the scenario has to run or not

        :param list scenario_choice: the scenarios to run. If None all will run
        """
        return self.parent.has_to_run(scenario_choice)
