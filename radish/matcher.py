# -*- coding: utf-8 -*-

"""
    This module provides a class to match the feature file steps with the registered steps from the registry
"""

import re

from radish.exceptions import StepDefinitionNotFoundError


class Matcher(object):
    """
        Matches steps from the feature files with the registered steps
    """
    def merge_steps(self, features, steps):
        """
            Merges steps from the given features with the given steps

            :param list features: the features
            :param dict steps: the steps
        """
        for feature in features:
            for scenario in feature.scenarios:
                for step in scenario.steps:
                    arguments, func = self.match(step.sentence, steps)
                    if not arguments or not func:
                        raise StepDefinitionNotFoundError(step)

                    step.definition_func = func
                    step.arguments = arguments

    def match(self, sentence, steps):
        """
            Tries to find a match from the given sentence with the given steps

            :param string sentence: the step sentence to match
            :param dict steps: the available registered steps

            :returns: the arguments and the func which were matched
            :rtype: tuple
        """
        for regex, func in steps.items():
            match = re.search(regex, sentence)
            if match:
                return match, func

        return None, None
