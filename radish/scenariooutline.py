# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Scenario Outline
"""

from radish.scenario import Scenario


class ScenarioOutline(Scenario):
    """
        Represents a Scenario
    """

    class Examples(object):
        """
            Represents the ScenarioOutline examples
        """

        def __init__(self):
            self.header = []
            self.rows = []

    def __init__(self, sentence, path, line):
        super(ScenarioOutline, self).__init__(sentence, path, line)
        self.examples = ScenarioOutline.Examples()
