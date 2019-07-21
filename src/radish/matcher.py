"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import re

from parse_type.cfparse import Parser

from radish.models.step import Step
from radish.errors import (
    StepImplementationNotFoundError,
    StepImplementationPatternNotSupported,
)

try:
    re_pattern_type = re.Pattern  # >= Python 3.7
except AttributeError:
    re_pattern_type = re._pattern_type


class RegexStepImplMatcher:
    """Matcher for Regular Expression based Step Implementations"""

    class Match:
        def __init__(self, match):
            self.match = match

        def evaluate(self):
            """Lazy and return evaluate the step group matches"""
            return self.match.groups(), self.match.groupdict()

    def __call__(self, step_text, step_impl):
        match = step_impl.pattern.search(step_text)
        if match:
            return self.Match(match), len(match.group())

        return None, 0


class ParseTypeStepImplMatcher:
    """Matcher for parse-type based Step Implementations"""

    class Match:
        def __init__(self, match):
            self.match = match

        def evaluate(self):
            """Lazy and return evaluate the step group matches"""
            result = self.match.evaluate_result()
            return result.fixed, result.named

    def __call__(self, step_text, step_impl):
        try:
            # parser = Parser(pattern, CustomTypeRegistry().custom_types)
            parser = Parser(step_impl.pattern)
        except ValueError:
            raise Exception("Cannot create parser")
            # raise StepPatternError(step_impl.pattern, func.__name__, e)

        match = parser.search(step_text, evaluate_result=False)
        if match:
            return self.Match(match), len(match.match.group())

        return None, 0


#: Holds a mapping of available Matchers
matchers = {re_pattern_type: RegexStepImplMatcher(), str: ParseTypeStepImplMatcher()}


def match_step(step: Step, registry):
    """Match the given ``Step`` with a registered Step Implementation from the ``StepRegistry``.

    If no match can be made an error is raised.
    If a match can be made the found ``StepImpl`` is assigned to the ``Step``.
    """
    # get all possible Step Implementation from the registry
    # depending on the Step Keyword.
    step_impls = registry.step_implementations(step.keyword)

    potentional_matches = []
    for step_impl in step_impls:
        try:
            matcher = matchers[type(step_impl.pattern)]
        except KeyError:
            raise StepImplementationPatternNotSupported(step_impl)

        match, match_length = matcher(step.text, step_impl)
        if match:
            if len(step.text) == match_length:
                # if perfect match can be made we return it no
                # matter of the other potentional matches
                step.assign_implementation(step_impl, match)
                return

            distance_to_perfect = abs(len(step.text) - match_length)
            potentional_matches.append(((step_impl, match), distance_to_perfect))

    if potentional_matches:
        # get best match
        best_step_impl, best_match = min(potentional_matches, key=lambda x: x[1])[0]
        step.assign_implementation(best_step_impl, best_match)

    raise StepImplementationNotFoundError(step)
