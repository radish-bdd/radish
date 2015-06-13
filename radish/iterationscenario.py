# -*- coding: utf-8 -*-

"""
    This module provides a Scenario which represents one iteration in a ScenarioLoop
"""

from radish.scenario import Scenario


class IterationScenario(Scenario):
    """
        Represents one iteration from a ScenarioLoop
    """
    def __init__(self, id, keyword, sentence, path, line, parent, iteration):
        super(IterationScenario, self).__init__(None, id, keyword, sentence, path, line, parent)
        self.iteration = iteration

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
