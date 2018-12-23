# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.feature import Feature
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.stepmodel import Step


def test_creating_simple_feature():
    """
    Test creating a simple Feature
    """
    # given & when
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)

    # then
    assert feature.id == 1
    assert feature.keyword == "Feature"
    assert feature.sentence == "I am a feature"
    assert feature.path == "foo.feature"
    assert feature.line == 1
    assert feature.tags == []


def test_feature_representation():
    """
    Test Feature representation with str() and repr()
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)

    # when
    str_repr = str(feature)
    repr_repr = repr(feature)

    # then
    assert str_repr == "Feature: I am a feature from foo.feature:1"
    assert repr_repr == "<Feature: I am a feature from foo.feature:1>"


def test_feature_scenario_iterator(mocker):
    """
    Test iterating over Scenarios within a Feature
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    # add Scenarios to Feature
    feature.scenarios.extend(
        [mocker.MagicMock(id=1), mocker.MagicMock(id=2), mocker.MagicMock(id=3)]
    )

    # when
    scenario_iterator = iter(feature)

    # then
    assert next(scenario_iterator).id == 1
    assert next(scenario_iterator).id == 2
    assert next(scenario_iterator).id == 3

    with pytest.raises(StopIteration):
        next(scenario_iterator)


def test_feature_scenario_iterator_empty():
    """
    Test iterating over Scenarios within a Feature when no Scenarios
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)

    # when
    scenario_iterator = iter(feature)

    # then
    with pytest.raises(StopIteration):
        next(scenario_iterator)


@pytest.mark.parametrize(
    "scenario_sentences, expected_scenario, found",
    [(("foo", "bar"), "foo", True), (("bar"), "foo", False), ([], "foo", False)],
)
def test_feature_contains_scenario(
    scenario_sentences, expected_scenario, found, mocker
):
    """
    Test contains protocol for Feature to check if it contains a Scenario
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    # add Scenarios to Feature
    for sentence in scenario_sentences:
        feature.scenarios.append(mocker.MagicMock(sentence=sentence))

    # when
    contains = expected_scenario in feature

    # then
    assert contains is found


@pytest.mark.parametrize(
    "scenario_sentences, needle_scenario, expected_scenario",
    [(("foo", "bar"), "foo", "foo"), (("bar"), "foo", None), ([], "foo", None)],
)
def test_feature_get_scenario_as_item(
    scenario_sentences, needle_scenario, expected_scenario, mocker
):
    """
    Test getitem protocol for Feature to get specific Scenario
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    # add Scenarios to Feature
    for sentence in scenario_sentences:
        feature.scenarios.append(mocker.MagicMock(sentence=sentence))

    # when
    actual_scenario = feature[needle_scenario]

    # then
    if expected_scenario is None:
        assert actual_scenario is None
    else:
        assert actual_scenario.sentence == expected_scenario


def test_feature_all_scenarios(mocker):
    """
    Test getting expanded list of all Scenarios of a Feature
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    # add regular Scenarios to Feature
    feature.scenarios.extend([mocker.MagicMock(id=1), mocker.MagicMock(id=2)])
    # add Scenario Outline to Feature
    feature.scenarios.append(
        mocker.MagicMock(
            spec=ScenarioOutline,
            id=3,
            scenarios=[mocker.MagicMock(id=4), mocker.MagicMock(id=5)],
        )
    )
    # add Scenario Loop to Feature
    feature.scenarios.append(
        mocker.MagicMock(
            spec=ScenarioLoop,
            id=6,
            scenarios=[mocker.MagicMock(id=7), mocker.MagicMock(id=8)],
        )
    )

    # when
    all_scenarios = feature.all_scenarios

    # then
    assert len(all_scenarios) == 8
    assert all_scenarios[0].id == 1
    assert all_scenarios[1].id == 2
    assert all_scenarios[2].id == 3
    assert all_scenarios[3].id == 4
    assert all_scenarios[4].id == 5
    assert all_scenarios[5].id == 6
    assert all_scenarios[6].id == 7
    assert all_scenarios[7].id == 8


def test_feature_constants(mocker):
    """
    Test getting all constants of this Feature
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    # add constants to Feature context -> this is directly done by the parser
    feature.context.constants = [mocker.MagicMock(value=1), mocker.MagicMock(value=2)]

    # when
    constants = feature.constants

    # then
    assert len(constants) == 2
    assert constants[0].value == 1
    assert constants[1].value == 2


def test_feature_state(mocker):
    """
    Test the state of a Feature according to the Scenario states
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    # add regular Scenarios to Feature
    regular_scenario = mocker.MagicMock(state=Step.State.PASSED)
    feature.scenarios.extend(
        [regular_scenario, mocker.MagicMock(state=Step.State.PASSED)]
    )
    # add Scenario Outline to Feature
    scenario_outline_example = mocker.MagicMock(state=Step.State.PASSED)
    scenario_outline = mocker.MagicMock(
        spec=ScenarioOutline,
        state=Step.State.PASSED,
        scenarios=[scenario_outline_example, mocker.MagicMock(state=Step.State.PASSED)],
    )
    feature.scenarios.append(scenario_outline)
    # add Scenario Loop to Feature
    scenario_loop_iteration = mocker.MagicMock(state=Step.State.PASSED)
    scenario_loop = mocker.MagicMock(
        spec=ScenarioLoop,
        state=Step.State.PASSED,
        scenarios=[scenario_loop_iteration, mocker.MagicMock(state=Step.State.PASSED)],
    )
    feature.scenarios.append(scenario_loop)

    # when all Scenarios pass then the Feature passes
    assert feature.state == Step.State.PASSED

    # when one Scenario is pending then the Feature is pending
    regular_scenario.state = Step.State.PENDING
    assert feature.state == Step.State.PENDING

    # when one Scenario is skipped then the Feature is skipped
    regular_scenario.state = Step.State.SKIPPED
    assert feature.state == Step.State.SKIPPED

    # when one Scenario is failed then the Feature is failed
    regular_scenario.state = Step.State.FAILED
    assert feature.state == Step.State.FAILED

    # when one Scenario is failed then the Feature is failed
    regular_scenario.state = Step.State.UNTESTED
    assert feature.state == Step.State.UNTESTED
    regular_scenario.state = Step.State.PASSED

    # Scenario Outline and Scenario Loop states are ignored
    scenario_outline.state = Step.State.FAILED
    assert feature.state == Step.State.PASSED
    scenario_loop.state = Step.State.FAILED
    assert feature.state == Step.State.PASSED

    # when a Scenario Outline Example is not passed the Feature is not passed
    scenario_outline_example.state = Step.State.FAILED
    assert feature.state == Step.State.FAILED
    scenario_outline_example.state = Step.State.PASSED

    # when a Scenario Loop Iteration is not passed the Feature is not passed
    scenario_loop_iteration.state = Step.State.FAILED
    assert feature.state == Step.State.FAILED
    scenario_loop_iteration.state = Step.State.PASSED

    # when a Scenario is untested which does not have to be run then the Feature is passed
    regular_scenario.state = Step.State.UNTESTED
    regular_scenario.has_to_run.return_value = False
    assert feature.state == Step.State.PASSED


@pytest.mark.parametrize(
    "scenario_ids, scenario_choice, expected_has_to_run",
    [
        ((1, 2, 3), [], True),
        ((1, 2, 3), [1], True),
        ((1, 2, 3), [1, 2, 5], True),
        ((1, 2, 3), [4], False),
        ((1, 2, 3), [4, 5], False),
    ],
)
def test_feature_scenario_has_to_run(
    scenario_ids, scenario_choice, expected_has_to_run, mocker
):
    """
    Test logic to check whether a Scenario within a Feature has to run or not
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    # add Scenarios to Feature
    for scenario_id in scenario_ids:
        feature.scenarios.append(mocker.MagicMock(absolute_id=scenario_id))

    # when
    actual_has_to_run = feature.has_to_run(scenario_choice)

    # then
    assert actual_has_to_run is expected_has_to_run
