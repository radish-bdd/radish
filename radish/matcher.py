# -*- coding: utf-8 -*-

"""
    This module provides a class to match the feature file steps with the registered steps from the registry
"""

import re
import parse
from collections import namedtuple

from .argexpregistry import ArgExpRegistry
from .exceptions import StepDefinitionNotFoundError, StepPatternError

StepMatch = namedtuple("StepMatch", ["args", "kwargs", "func"])


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
        match = cls.match(step.expanded_sentence, steps)
        if not match or not match.func:
            raise StepDefinitionNotFoundError(step)

        step.definition_func = match.func
        step.arguments = match.args
        step.keyword_arguments = match.kwargs

    @staticmethod
    def match(sentence, steps):
        """
            Tries to find a match from the given sentence with the given steps

            :param string sentence: the step sentence to match
            :param dict steps: the available registered steps

            :returns: the arguments and the func which were matched
            :rtype: tuple
        """
        for pattern, func in steps.items():
            if isinstance(pattern, re._pattern_type):  # pylint: disable=protected-access
                match = pattern.search(sentence)
                if match:
                    return StepMatch(args=match.groups(), kwargs=match.groupdict(), func=func)
            else:
                try:
                    compiled = parse.compile(pattern, ArgExpRegistry().expressions)
                except ValueError as e:
                    raise StepPatternError(pattern, func.__name__, e)

                match = compiled.search(sentence)
                if match:
                    return StepMatch(args=match.fixed, kwargs=match.named, func=func)

        return None
