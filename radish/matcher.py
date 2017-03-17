# -*- coding: utf-8 -*-

"""
    This module provides a class to match the feature file steps with the registered steps from the registry
"""

import re
from collections import namedtuple

import parse

from .argexpregistry import ArgExpRegistry
from .exceptions import StepDefinitionNotFoundError, StepPatternError

StepMatch = namedtuple("StepMatch", ["argument_match", "func"])


class RegexStepArguments(object):  # pylint: disable=too-few-public-methods
    """Class to represent the argument groups matched by a regex step pattern"""
    def __init__(self, match):
        self.match = match

    def evaluate(self):
        """Lazy and return evaluate the step group matches"""
        return self.match.groups(), self.match.groupdict()


class ParseStepArguments(object):  # pylint: disable=too-few-public-methods
    """Class to represent the argument groups matched by a parse step pattern"""
    def __init__(self, match):
        self.match = match

    def evaluate(self):
        """Lazy and return evaluate the step group matches"""
        result = self.match.evaluate_result()
        return result.fixed, result.named


def merge_steps(features, steps):
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
                merge_step(step, steps)


def merge_step(step, steps):
    """
        Merges a single step with the registered steps

        :param Step step: the step from a feature file to merge
        :param list steps: the registered steps
    """
    match = match_step(step.expanded_sentence, steps)
    if not match or not match.func:
        raise StepDefinitionNotFoundError(step)

    step.definition_func = match.func
    step.argument_match = match.argument_match


def match_step(sentence, steps):
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
            argument_match = RegexStepArguments(match)
        else:
            try:
                compiled = parse.compile(pattern, ArgExpRegistry().expressions)
            except ValueError as e:
                raise StepPatternError(pattern, func.__name__, e)

            match = compiled.search(sentence, evaluate_result=False)
            argument_match = ParseStepArguments(match)

        if match:
            return StepMatch(argument_match=argument_match, func=func)

    return None
