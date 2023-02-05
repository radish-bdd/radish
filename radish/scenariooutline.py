# -*- coding: utf-8 -*-

"""
This module provides a class to represent a Scenario Outline
"""

import copy

from .scenario import Scenario
from .examplescenario import ExampleScenario
from .stepmodel import Step
from .exceptions import RadishError


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

    def __init__(
        self,
        id,
        keyword,
        example_keyword,
        sentence,
        path,
        line,
        parent,
        tags=None,
        preconditions=None,
        background=None,
    ):
        super(ScenarioOutline, self).__init__(
            id, keyword, sentence, path, line, parent, tags, preconditions, background
        )
        self.example_keyword = example_keyword
        self.scenarios = []
        self.examples_header = []
        self.examples = []

    def build_scenarios(self):
        """
        Builds the scenarios with the parsed Examples

        Note: This must be done before merging the steps
              from the feature file with the step definitions
        """
        for row_id, example in enumerate(self.examples):
            examples = dict(zip(self.examples_header, example.data))
            scenario_id = self.id + row_id + 1
            background = None
            scenario = ExampleScenario(
                scenario_id,
                self.keyword,
                "{0} - row {1}".format(self.sentence, row_id),
                self.path,
                self.line,
                self,
                example,
            )
            if self.background:
                background = self.background.create_instance(parent=scenario, steps_runable=True)
                scenario.background = background

            for step_id, outlined_step in enumerate(self.steps):
                sentence = self._replace_examples_in_sentence(outlined_step.sentence, examples)
                raw_text = self._replace_examples_in_raw_text(outlined_step.raw_text, examples)
                step = Step(
                    step_id + 1,
                    sentence,
                    outlined_step.path,
                    example.line,
                    scenario,
                    True,
                    context_class=outlined_step.context_class,
                )
                # copy extended attributes
                step.table_header = copy.copy(outlined_step.table_header)
                step.table_data = copy.copy(outlined_step.table_data)
                step.table = copy.copy(outlined_step.table)
                step.raw_text = raw_text

                # add step to scenario
                scenario.steps.append(step)
            self.scenarios.append(scenario)

    @staticmethod
    def _replace_examples_in_sentence(sentence, examples):
        """
        Replaces the given examples in the given sentence

        :param string sentence: the step sentence in which to replace the examples
        :param dict examples: the examples

        :returns: the new step sentence
        :rtype: string
        """
        for key, value in examples.items():
            sentence = sentence.replace("<{0}>".format(key), value)
        return sentence

    @staticmethod
    def _replace_examples_in_raw_text(raw_text, examples):
        """
        Replaces the given examples in the given raw_text, which is
        a list of strings

        :param list raw_text: list of strings in which to replace the examples
        :param dict examples: the examples

        :returns: the new list raw_text
        :rtype: list
        """
        raw_text_list = []
        for raw_text_item in raw_text:
            raw_text_item = ScenarioOutline._replace_examples_in_sentence(raw_text_item, examples)
            raw_text_list.append(raw_text_item)
        return raw_text_list

    def get_column_width(self, column_index):
        """
        Gets the column width from the given column

        :param int column_index: the column index to get the width from
        """
        try:
            return max(
                max([len(x.data[column_index]) for x in self.examples]),
                len(self.examples_header[column_index]),
            )
        except IndexError:
            raise RadishError("Invalid colum_index to get column width for ScenarioOutline '{0}'".format(self.sentence))

    def after_parse(self):
        """
        Build outlined scenarios
        """
        Scenario.after_parse(self)
        self.build_scenarios()
        self.complete = True
