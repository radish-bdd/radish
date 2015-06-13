# -*- coding: utf-8 -*-

"""
    This module provides a class to represent one Scenario Outline Example
"""

from radish.scenario import Scenario


class ExampleScenario(Scenario):
    """
        Represents one example scenario from a ScenarioOutline
    """
    def __init__(self, id, keyword, sentence, path, line, parent, example):
        super(ExampleScenario, self).__init__(None, id, keyword, sentence, path, line, parent)
        self.example = example

    def has_to_run(self, scenario_choice):
        """
            Returns wheiter the scenario has to run or not

            :param list scenario_choice: the scenarios to run. If None all will run
        """
        if not scenario_choice:
            return True

        if self.parent.absolute_id in scenario_choice:
            return True

        return False
