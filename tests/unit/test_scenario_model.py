"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from unittest.mock import MagicMock

import pytest
from tagexpressions import parse

from radish.models import ConstantTag, Scenario, Tag
from radish.models.state import State


def test_scenario_should_set_feature_to_steps_when_feature_set(mocker):
    """A Scenario should forward the Feature to each Step"""
    # given
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    scenario = Scenario(
        1, "Scenario", "My Scenario", [], None, None, [first_step, second_step]
    )
    feature_mock = mocker.MagicMock(name="Feature")

    # when
    scenario.set_feature(feature_mock)

    # then
    assert scenario.feature is feature_mock
    first_step.set_feature.assert_called_once_with(feature_mock)
    second_step.set_feature.assert_called_once_with(feature_mock)


def test_scenario_should_set_rule_to_steps_when_rule_set(mocker):
    """A Scenario should forward the Rule to each Step"""
    # given
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    scenario = Scenario(
        1, "Scenario", "My Scenario", [], None, None, [first_step, second_step]
    )
    rule_mock = mocker.MagicMock(name="Rule")

    # when
    scenario.set_rule(rule_mock)

    # then
    assert scenario.rule is rule_mock
    first_step.set_rule.assert_called_once_with(rule_mock)
    second_step.set_rule.assert_called_once_with(rule_mock)


def test_scenario_should_copy_background_when_set(mocker):
    """A Scenario should make a deepcopy when a Background is set"""
    # given
    scenario = Scenario(1, "Scenario", "My Scenario", [], None, None, [])
    background_mock = mocker.MagicMock(name="Background")
    background_mock.short_description = "My Background"

    # when
    scenario.set_background(background_mock)

    # then
    assert scenario.background.short_description == background_mock.short_description
    assert scenario.background is not background_mock


def test_scenario_should_set_itself_as_scenario_for_a_set_background(mocker):
    """A Scenario should set itself as Scenario for a set Background"""
    # given
    scenario = Scenario(1, "Scenario", "My Scenario", [], None, None, [])
    background_mock = mocker.MagicMock(name="Background")

    # when
    scenario.set_background(background_mock)

    # then
    scenario.background.set_scenario.assert_called_once_with(scenario)


def test_scenario_should_set_its_rule_as_rule_for_a_set_background(mocker):
    """A Scenario should set its Rule as Rule for a set Background"""
    # given
    scenario = Scenario(1, "Scenario", "My Scenario", [], None, None, [])
    scenario.rule = mocker.MagicMock(name="Rule")
    background_mock = mocker.MagicMock(name="Background")

    # when
    scenario.set_background(background_mock)

    # then
    scenario.background.set_rule.assert_called_once_with(scenario.rule)


def test_scenario_should_ignore_to_set_none_for_a_background(mocker):
    """A Scenario should ignore to set None for a Background"""
    # given
    scenario = Scenario(1, "Scenario", "My Scenario", [], None, None, [])
    background_mock = mocker.MagicMock(name="Background")
    scenario.set_background(background_mock)

    # when
    scenario.set_background(None)

    # then
    assert scenario.background is not None


@pytest.mark.parametrize(
    "given_background_state, given_steps, expected_state",
    [
        (State.PASSED, [], State.PASSED),
        (
            State.PASSED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
            ],
            State.PASSED,
        ),
        (
            State.PASSED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.FAILED),
                MagicMock(state=State.UNTESTED),
            ],
            State.FAILED,
        ),
        (
            State.PASSED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.UNTESTED),
                MagicMock(state=State.UNTESTED),
            ],
            State.UNTESTED,
        ),
        (
            State.PASSED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.SKIPPED),
                MagicMock(state=State.UNTESTED),
            ],
            State.SKIPPED,
        ),
        (
            State.PASSED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.SKIPPED),
                MagicMock(state=State.PENDING),
            ],
            State.PENDING,
        ),
        (
            State.PASSED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.SKIPPED),
                MagicMock(state=State.FAILED),
            ],
            State.FAILED,
        ),
        (
            State.PASSED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.UNTESTED),
                MagicMock(state=State.FAILED),
            ],
            State.FAILED,
        ),
        (
            State.UNTESTED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
            ],
            State.UNTESTED,
        ),
        (
            State.SKIPPED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
            ],
            State.SKIPPED,
        ),
        (
            State.PENDING,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
            ],
            State.PENDING,
        ),
        (
            State.FAILED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
                MagicMock(state=State.PASSED),
            ],
            State.FAILED,
        ),
        (
            State.SKIPPED,
            [
                MagicMock(state=State.PASSED),
                MagicMock(state=State.FAILED),
                MagicMock(state=State.PASSED),
            ],
            State.FAILED,
        ),
    ],
    ids=[
        "Background PASSED, No Steps -> Scenario PASSED",
        "Background PASSED, Steps all PASSED -> Scenario PASSED",
        "Background PASSED, Steps [PASSED, FAILED, UNTESTED] -> Scenario FAILED",
        "Background PASSED, Steps [PASSED, UNTESTED, UNTESTED] -> Scenario UNTESTED",
        "Background PASSED, Steps [PASSED, SKIPPED, UNTESTED] -> Scenario SKIPPED",
        "Background PASSED, Steps [PASSED, SKIPPED, PENDING] -> Scenario PENDING",
        "Background PASSED, Steps [PASSED, SKIPPED, FAILED] -> Scenario FAILED",
        "Background PASSED, Steps [PASSED, UNTESTED, FAILED] -> Scenario FAILED",
        "Background UNTESTED, Steps [PASSED, PASSED, PASSED] -> Scenario UNTESTED",
        "Background SKIPPED, Steps [PASSED, PASSED, PASSED] -> Scenario SKIPPED",
        "Background PENDING, Steps [PASSED, PASSED, PASSED] -> Scenario PENDING",
        "Background FAILED, Steps [PASSED, PASSED, PASSED] -> Scenario FAILED",
        "Background SKIPPED, Steps [PASSED, FAILED, PASSED] -> Scenario FAILED",
    ],
)
def test_scenario_should_return_correct_state(
    given_background_state, given_steps, expected_state, mocker
):
    """
    A Scneario should return the correct State depending on its
    Background State and its own Steps State.
    """
    # given
    scenario = Scenario(1, "Scenario", "My Scenario", [], None, None, given_steps)
    background_mock = mocker.MagicMock(name="Background")
    background_mock.state = given_background_state
    background_mock.steps = [mocker.MagicMock(state=given_background_state)]
    scenario.set_background(background_mock)

    # when
    actual_state = scenario.state

    # then
    assert actual_state == expected_state


def test_scenario_without_steps_should_return_untested_state(mocker):
    """
    A Scneario without any Steps should return the State UNTESTED
    """
    # given
    scenario = Scenario(1, "Scenario", "My Scenario", [], None, None, [])
    scenario.background = None

    # when
    actual_state = scenario.state

    # then
    assert actual_state == State.UNTESTED


def test_scenario_should_ignore_background_state_if_no_background(mocker):
    """A Scenario should ignore the Background for the State if no is assigned"""
    # given
    scenario = Scenario(
        1,
        "Scenario",
        "My Scenario",
        [],
        None,
        None,
        [mocker.MagicMock(state=State.SKIPPED)],
    )

    # when
    actual_state = scenario.state

    # then
    assert actual_state == State.SKIPPED


@pytest.mark.parametrize(
    "tagexpression, scenario_ids, expected_has_to_run",
    [
        (None, [], True),
        (parse("tag-a"), [], True),
        (parse("tag-c"), [], True),
        (parse("tag-X"), [], False),
        (None, [1], True),
        (None, [2], False),
        (parse("tag-a"), [2], False),
        (parse("tag-X"), [1], False),
        (parse("tag-a"), [1], True),
    ],
    ids=[
        "no tagexpression, no scenario_ids => RUN",
        "tagexpression match in Scenario Tags, no scenario_ids => RUN",
        "tagexpression match in Feature Tags, no scenario_ids => RUN",
        "tagexpression no match, no scenario_ids => NO RUN",
        "no tagexpression, scenario_ids match => RUN",
        "no tagexpression, scenario_ids no match => NO RUN",
        "tagexpression match, scenario_ids no match => NO RUN",
        "tagexpression no match, scenario_ids match => NO RUN",
        "tag expression match, scenario_ids match => RUN",
    ],
)
def test_scenario_should_correctly_evaluate_if_it_has_to_be_run(
    mocker, tagexpression, scenario_ids, expected_has_to_run
):
    """Test that a Scenario should correctly evaluate if it has to be run or not"""
    # given
    feature_mock = mocker.MagicMock(tags=[Tag("tag-c", None, None)])
    scenario = Scenario(
        1,
        "Scenario",
        "My Scenario",
        [Tag("tag-a", None, None), Tag("tag-b", None, None)],
        None,
        None,
        [],
    )
    scenario.set_feature(feature_mock)

    # when
    has_to_run = scenario.has_to_run(tagexpression, scenario_ids)

    # then
    assert has_to_run == expected_has_to_run


def test_scenario_should_return_all_constants(mocker):
    """A Scenario should return all Constants from the Tags"""
    # given
    tags = [
        Tag("x", None, None),
        ConstantTag("k1", "v1", None, None),
        Tag("y", None, None),
        ConstantTag("k2", "v2", None, None),
    ]
    scenario = Scenario(1, "Scenario", "My Scenario", tags, None, None, [])
    feature_mock = mocker.MagicMock(name="Feature")
    feature_mock.constants = {}
    scenario.set_feature(feature_mock)

    # when
    actual_constants = scenario.constants

    # then
    assert actual_constants == {"k1": "v1", "k2": "v2"}


def test_scenario_should_inherit_feature_constants(mocker):
    """A Scenario should inherit all Constants from the Feature"""
    # given
    tags = [
        Tag("x", None, None),
        ConstantTag("k1", "v1", None, None),
        Tag("y", None, None),
        ConstantTag("k2", "v2", None, None),
    ]
    feature_mock = mocker.MagicMock(name="Feature")
    feature_mock.constants = {"kf1": "vf1", "kf2": "vf2"}
    scenario = Scenario(1, "Scenario", "My Scenario", tags, None, None, [])
    scenario.set_feature(feature_mock)

    # when
    actual_constants = scenario.constants

    # then
    assert actual_constants == {"k1": "v1", "k2": "v2", "kf1": "vf1", "kf2": "vf2"}
