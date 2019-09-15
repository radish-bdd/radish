"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.models import Rule, State


def test_rule_should_forward_set_feature_to_its_scenarios(mocker):
    """A Rule should forward a set Feature to its Scenarios"""
    # given
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    rule = Rule("Rule", "My Rule", None, None, [first_scenario, second_scenario])
    feature_mock = mocker.MagicMock(name="Feature")

    # when
    rule.set_feature(feature_mock)

    # then
    assert rule.feature is feature_mock
    first_scenario.set_feature.assert_called_once_with(feature_mock)
    second_scenario.set_feature.assert_called_once_with(feature_mock)


def test_rule_should_forward_set_background_to_its_scenarios(mocker):
    """A Rule should forward a set Background to its Scenarios"""
    # given
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    rule = Rule("Rule", "My Rule", None, None, [first_scenario, second_scenario])
    background_mock = mocker.MagicMock(name="Background")

    # when
    rule.set_background(background_mock)

    # then
    first_scenario.set_background.assert_called_once_with(background_mock)
    second_scenario.set_background.assert_called_once_with(background_mock)


@pytest.mark.parametrize(
    "given_scenario_states, expected_state",
    [
        ([State.PASSED, State.PASSED, State.PASSED], State.PASSED),
        ([State.PASSED, State.UNTESTED, State.PASSED], State.UNTESTED),
        ([State.PASSED, State.SKIPPED, State.UNTESTED], State.SKIPPED),
        ([State.PASSED, State.PENDING, State.SKIPPED], State.PENDING),
        ([State.PASSED, State.PENDING, State.FAILED], State.FAILED),
        ([State.PASSED, State.RUNNING, State.FAILED], State.RUNNING),
    ],
    ids=[
        "[State.PASSED, State.PASSED, State.PASSED] -> State.PASSED",
        "[State.PASSED, State.UNTESTED, State.PASSED] -> State.UNTESTED",
        "[State.PASSED, State.SKIPPED, State.UNTESTED] -> State.SKIPPED",
        "[State.PASSED, State.PENDING, State.SKIPPED] -> State.PENDING",
        "[State.PASSED, State.PENDING, State.FAILED] -> State.FAILED",
        "[State.PASSED, State.RUNNING, State.FAILED] -> State.RUNNING",
    ],
)
def test_rule_should_return_correct_state_according_to_its_scenario_states(
    given_scenario_states, expected_state, mocker
):
    """A Rule should return the correct State according to its Scenario States"""
    # given
    rule = Rule(
        "Rule",
        "My Rule",
        None,
        None,
        [mocker.MagicMock(state=s) for s in given_scenario_states],
    )

    # when
    actual_state = rule.state

    # then
    assert actual_state == expected_state


@pytest.mark.parametrize(
    "scenarios_need_to_run, expected_has_to_run",
    [
        ([False, False, False], False),
        ([False, True, False], True),
        ([False, True, True], True),
    ],
    ids=[
        "no Scenario needs to run",
        " a Scenario needs to run",
        "multiple Scenarios need to run",
    ],
)
def test_rule_should_run_if_one_of_its_scenario_has_to_run(
    scenarios_need_to_run, expected_has_to_run, mocker
):
    """A Rule should run if one of its Scenarios has to run"""
    scenarios = []
    for has_to_run in scenarios_need_to_run:
        scenario_mock = mocker.MagicMock()
        scenario_mock.has_to_run.return_value = has_to_run
        scenarios.append(scenario_mock)

    # given
    rule = Rule("Rule", "My Rule", None, None, scenarios)

    # when
    actual_has_to_run = rule.has_to_run(None, None)

    # then
    assert actual_has_to_run == expected_has_to_run
