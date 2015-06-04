# -*- coding: utf-8 -*-

"""
    This module provides a class to represent a Scenario Outline
"""

from radish.scenario import Scenario
from radish.step import Step


class ScenarioOutline(Scenario):
    """
        Represents a Scenario
    """

    class Example(object):
        """
            Represents the ScenarioOutline examples
        """

        def __init__(self, data, path, line):
            self.data = data
            self.path = path
            self.line = line

    def __init__(self, sentence, path, line):
        super(ScenarioOutline, self).__init__(sentence, path, line)
        self.scenarios = []
        self.examples_header = []
        self.examples = []

    def build_scenarios(self):
        """
            Builds the scenarios with the parsed Examples

            Note: This must be done before mering the steps from the feature file with the step definitions
        """
        for row_id, example in enumerate(self.examples):
            examples = dict(zip(self.examples_header, example.data))
            scenario = Scenario("{} - row {}".format(self.sentence, row_id), self.path, self.line)
            for outlined_step in self.steps:
                sentence = self._replace_examples_in_sentence(outlined_step.sentence, examples)
                step = Step(sentence, outlined_step.path, example.line)
                scenario.steps.append(step)
            self.scenarios.append(scenario)

    @classmethod
    def _replace_examples_in_sentence(cls, sentence, examples):
        """
            Replaces the given examples in the given sentece

            :param string sentence: the step sentence in which to replace the examples
            :param dict examples: the examples

            :returns: the new step sentence
            :rtype: string
        """
        for key, value in examples.items():
            sentence = sentence.replace("<{}>".format(key), value)
        return sentence
