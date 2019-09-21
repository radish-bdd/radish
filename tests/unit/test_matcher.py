"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import re

import pytest

from radish.stepregistry import StepImpl
from radish.matcher import match_step, RegexStepImplMatcher, ParseTypeStepImplMatcher
from radish.models import Step
from radish.errors import (
    StepImplementationNotFoundError,
    StepImplementationPatternNotSupported,
)


def test_matcher_should_raise_error_when_no_step_impl_found(mocker):
    """The matcher should raise an error when no Step Implementation is found"""
    # given
    registry_mock = mocker.MagicMock()
    registry_mock.step_implementations.return_value = []
    step = Step(1, "Given", "Given", "pattern", None, None, None, None)
    step.set_scenario(mocker.MagicMock(name="Scenario"))

    # then
    with pytest.raises(StepImplementationNotFoundError) as excinfo:
        # when
        match_step(step, registry_mock)

    # then
    assert excinfo.value.step == step


def test_matcher_should_raise_error_when_no_matcher_for_pattern_type(mocker):
    """
    The matcher should raise an error when no Matcher supports a Step Implementation Pattern Type
    """
    # given
    class NotSupportedPatternType:
        pass

    step_impl = StepImpl("Given", NotSupportedPatternType(), None)
    registry_mock = mocker.MagicMock()
    registry_mock.step_implementations.return_value = [step_impl]
    step = Step(1, "Given", "Given", "pattern", None, None, None, None)
    step.set_scenario(mocker.MagicMock(name="Scenario"))

    # then
    with pytest.raises(StepImplementationPatternNotSupported) as excinfo:
        # when
        match_step(step, registry_mock)

    # then
    assert excinfo.value.step_impl == step_impl


def test_matcher_should_match_step_impl_with_parse_type_pattern(mocker):
    """The matcher should match a Step with a parse-type pattern"""
    # given
    step_impl = StepImpl("Given", "pattern", None)
    registry_mock = mocker.MagicMock()
    registry_mock.step_implementations.return_value = [step_impl]
    step = Step(1, "Given", "Given", "pattern", None, None, None, None)
    step.set_scenario(mocker.MagicMock(name="Scenario"))

    # when
    match_step(step, registry_mock)

    # then
    assert step.step_impl == step_impl
    assert isinstance(step.step_impl_match, ParseTypeStepImplMatcher.Match)


def test_matcher_should_match_step_impl_with_regex_pattern(mocker):
    """The matcher should match a Step with a parse-type pattern"""
    # given
    step_impl = StepImpl("Given", re.compile(r"pattern"), None)
    registry_mock = mocker.MagicMock()
    registry_mock.step_implementations.return_value = [step_impl]
    step = Step(1, "Given", "Given", "pattern", None, None, None, None)
    step.set_scenario(mocker.MagicMock(name="Scenario"))

    # when
    match_step(step, registry_mock)

    # then
    assert step.step_impl == step_impl
    assert isinstance(step.step_impl_match, RegexStepImplMatcher.Match)


def test_matcher_should_match_best_step_impl_candidate(mocker):
    """The matcher should match the best matching Step Implementation Candidate"""
    # given
    step_impl_candidate_1 = StepImpl("Given", re.compile(r"fooo"), None)
    step_impl_candidate_2 = StepImpl("Given", re.compile(r"foo"), None)
    step_impl_candidate_3 = StepImpl("Given", re.compile(r"foooo"), None)
    step_impl_no_candidate = StepImpl("Given", re.compile(r"meh"), None)

    registry_mock = mocker.MagicMock()
    registry_mock.step_implementations.return_value = [
        step_impl_candidate_1,
        step_impl_candidate_2,
        step_impl_candidate_3,
        step_impl_no_candidate,
    ]
    step = Step(1, "Given", "Given", "foo", None, None, None, None)
    step.set_scenario(mocker.MagicMock(name="Scenario"))

    # when
    match_step(step, registry_mock)

    # then
    assert step.step_impl == step_impl_candidate_2


def test_matcher_should_match_step_impl_with_step_with_constants(mocker):
    """The matcher should match a Step with Constants"""
    # given
    step_impl = StepImpl("Given", "pattern with A and B", None)
    registry_mock = mocker.MagicMock()
    registry_mock.step_implementations.return_value = [step_impl]
    step = Step(
        1, "Given", "Given", "pattern with ${x} and ${y}", None, None, None, None
    )
    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.constants = {"x": "A", "y": "B"}
    step.set_scenario(scenario_mock)

    # when
    match_step(step, registry_mock)

    # then
    assert step.step_impl == step_impl
    assert isinstance(step.step_impl_match, ParseTypeStepImplMatcher.Match)
