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
        super(ExampleScenario, self).__init__(id, keyword, sentence, path, line, parent)
        self.example = example
