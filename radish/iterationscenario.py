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
        super(IterationScenario, self).__init__(id, keyword, sentence, path, line, parent)
        self.iteration = iteration
