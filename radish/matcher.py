# -*- coding: utf-8 -*-

"""
    This module provides a class to match the feature file steps with the registered steps from the registry
"""

import re
import parse

from .argexpregistry import ArgExpRegistry
from .exceptions import StepDefinitionNotFoundError, StepPatternError


class Matcher(object):
    """
        Matches steps from the feature files with the registered steps
    """
    @classmethod
    def merge_steps(cls, features, steps):
        """
            Merges steps from the given features with the given steps

            :param list features: the features
            :param dict steps: the steps
        """
        # FIXME: fix cycle-import ... Matcher -> ScenarioOutline -> Step -> Matcher
        from .scenariooutline import ScenarioOutline
        for feature in features:
            for scenario in feature.all_scenarios:
                if isinstance(scenario, ScenarioOutline):
                    continue  # ScenarioOutline steps do not have to be merged

                for step in scenario.steps:
                    cls.merge_step(step, steps)

    @classmethod
    def merge_step(cls, step, steps):
        """
            Merges a single step with the registered steps

            :param Step step: the step from a feature file to merge
            :param list steps: the registered steps
        """
        arguments, keyword_arguments, func = cls.match(step.expanded_sentence, steps)
        if not func:
            raise StepDefinitionNotFoundError(step)

        step.definition_func = func
        step.arguments = arguments
        step.keyword_arguments = keyword_arguments

    @staticmethod
    def match(sentence, steps):
        """
            Tries to find a match from the given sentence with the given steps

            :param string sentence: the step sentence to match
            :param dict steps: the available registered steps

            :returns: the arguments and the func which were matched
            :rtype: tuple
        """
        # FIXME: return namedtuple instead of tuple
        for pattern, func in steps.items():
            if isinstance(pattern, re._pattern_type):  # pylint: disable=protected-access
                match = pattern.search(sentence)
                if match:
                    return match.groups(), match.groupdict(), func
            else:
                try:
                    compiled = parse.compile(pattern, ArgExpRegistry().expressions)
                except ValueError as e:
                    raise StepPatternError(pattern, func.__name__, e)

                match = compiled.search(sentence)
                if match:
                    return match.fixed, match.named, func

        return None, None, None
