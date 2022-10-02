# -*- coding: utf-8 -*-

"""
This module provides a Scenario which represents one iteration in a ScenarioLoop
"""

from .scenario import Scenario


class IterationScenario(Scenario):
    """
    Represents one iteration from a ScenarioLoop
    """

    def __init__(
        self, id, keyword, sentence, path, line, parent, iteration, background=None
    ):
        super(IterationScenario, self).__init__(
            id, keyword, sentence, path, line, parent, background=background
        )
        self.iteration = iteration

    def has_to_run(self, scenario_choice):
        """
        Returns wheiter the scenario has to run or not

        :param list scenario_choice: the scenarios to run. If None all will run
        """
        return self.parent.has_to_run(scenario_choice)
