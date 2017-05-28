# -*- coding: utf-8 -*-

"""
    This module provides a class to match the feature file steps with the registered steps from the registry
"""

import re
from collections import namedtuple

try:
    from parse_type.cfparse import Parser
except ImportError:
    from parse import Parser

from .customtyperegistry import CustomTypeRegistry
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
            if scenario.background:
                for step in scenario.background.steps:
                    merge_step(step, steps)

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
    match = match_step(step.context_sensitive_sentence, steps)
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
            if match:
                longest_group = get_longest_group(match.regs)
            else:
                longest_group = 0
        else:
            try:
                parser = Parser(pattern, CustomTypeRegistry().custom_types)
            except ValueError as e:
                raise StepPatternError(pattern, func.__name__, e)

            match = parser.search(sentence, evaluate_result=False)
            argument_match = ParseStepArguments(match)
            if match:
                longest_group = get_longest_group(match.match.regs)
            else:
                longest_group = 0

        if match:
            if len(sentence) == longest_group:
                return StepMatch(argument_match=argument_match, func=func)

    return None


def get_longest_group(regs):
    if len(regs) < 1:
        return 0

    longest_group = regs[0][1]

    for reg in regs[1:]:
        candidate = reg[1]
        if candidate > longest_group:
            longest_group = candidate
    return longest_group
