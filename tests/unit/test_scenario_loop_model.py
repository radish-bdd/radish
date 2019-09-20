"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest
from tagexpressions import parse

from radish.models import ScenarioLoop, Tag


def test_scenarioloop_set_feature_on_all_examples(mocker):
    """A ScenarioLoop should forward a set Feature to all its Examples"""
    # given
    feature_mock = mocker.MagicMock(name="Feature")
    scenario = ScenarioLoop(
        1, "Scenario Loop", "My ScenarioLoop", [], None, None, [], 0
    )
    first_example = mocker.MagicMock(name="First Example")
    second_example = mocker.MagicMock(name="Second Example")
    scenario.examples = [first_example, second_example]

    # when
    scenario.set_feature(feature_mock)

    # then
    assert scenario.feature is feature_mock
    first_example.set_feature.assert_called_once_with(feature_mock)
    second_example.set_feature.assert_called_once_with(feature_mock)


def test_scenarioloop_set_background_on_all_examples(mocker):
    """A ScenarioLoop should forward a set Background to all its Examples"""
    # given
    background_mock = mocker.MagicMock(name="Background")
    scenario = ScenarioLoop(
        1, "Scenario Loop", "My ScenarioLoop", [], None, None, [], 0
    )
    first_example = mocker.MagicMock(name="First Example")
    second_example = mocker.MagicMock(name="Second Example")
    scenario.examples = [first_example, second_example]

    # when
    scenario.set_background(background_mock)

    # then
    assert scenario.background is not None
    first_example.set_background.assert_called_once_with(background_mock)
    second_example.set_background.assert_called_once_with(background_mock)


def test_scenarioloop_set_rule_on_all_examples(mocker):
    """A ScenarioLoop should forward a set Rule to all its Examples"""
    # given
    rule_mock = mocker.MagicMock(name="Rule")
    scenario = ScenarioLoop(
        1, "Scenario Loop", "My ScenarioLoop", [], None, None, [], 0
    )
    first_example = mocker.MagicMock(name="First Example")
    second_example = mocker.MagicMock(name="Second Example")
    scenario.examples = [first_example, second_example]

    # when
    scenario.set_rule(rule_mock)

    # then
    assert scenario.rule is rule_mock
    first_example.set_rule.assert_called_once_with(rule_mock)
    second_example.set_rule.assert_called_once_with(rule_mock)


def test_scenarioloop_build_examples_from_iterations():
    """A ScenarioLoop should build its Examples from the given amount of Iterations"""
    # given & when
    scenario = ScenarioLoop(
        1, "Scenario Loop", "My ScenarioLoop", [], None, None, [], 2
    )  # two examples

    # then
    assert len(scenario.examples) == 2


def test_scenarioloop_should_build_examples_with_info_in_short_description():
    """A ScenarioLoop should build its Examples with the Iteration id in the short description"""
    # given & when
    scenario = ScenarioLoop(
        1, "Scenario Loop", "My ScenarioLoop", [], None, None, [], 2
    )

    # then
    assert scenario.examples[0].short_description == "My ScenarioLoop [Iteration: 1]"
    assert scenario.examples[1].short_description == "My ScenarioLoop [Iteration: 2]"


def test_scenarioloop_should_build_examples_with_copied_steps(mocker):
    """A ScenarioLoop should build its Example with a copy of its own Steps"""
    # given & when
    scenario = ScenarioLoop(
        1,
        "Scenario Loop",
        "My ScenarioLoop",
        [],
        None,
        None,
        [mocker.MagicMock(name="First Step"), mocker.MagicMock(name="Second Step")],
        2,
    )

    # then
    assert len(scenario.examples[0].steps) == 2
    assert len(scenario.examples[1].steps) == 2
    assert scenario.steps is not scenario.examples[0].steps
    assert scenario.steps is not scenario.examples[1].steps


@pytest.mark.parametrize(
    "tagexpression, scenario_ids, expected_has_to_run",
    [
        (None, [], True),
        (parse("tag-a"), [], True),
        (parse("tag-c"), [], True),
        (parse("tag-X"), [], False),
        (None, [1], True),
        (None, [3], True),
        (None, [-1], False),
        (parse("tag-a"), [-1], False),
        (parse("tag-X"), [1], False),
        (parse("tag-X"), [3], False),
        (parse("tag-a"), [3], True),
    ],
    ids=[
        "no tagexpression, no scenario_ids => RUN",
        "tagexpression match in Scenario Tags, no scenario_ids => RUN",
        "tagexpression match in Feature Tags, no scenario_ids => RUN",
        "tagexpression no match, no scenario_ids => NO RUN",
        "no tagexpression, scenario_ids match => RUN",
        "no tagexpression, scenario_ids match Example => RUN",
        "no tagexpression, scenario_ids no match => NO RUN",
        "tagexpression match, scenario_ids no match => NO RUN",
        "tagexpression no match, scenario_ids match => NO RUN",
        "tagexpression no match, scenario_ids match Example => NO RUN",
        "tag expression match, scenario_ids match Example => RUN",
    ],
)
def test_scenario_should_correctly_evaluate_if_it_has_to_be_run(
    mocker, tagexpression, scenario_ids, expected_has_to_run
):
    """Test that a Scenario should correctly evaluate if it has to be run or not"""
    # given
    feature_mock = mocker.MagicMock(tags=[Tag("tag-c", None, None)])
    scenario = ScenarioLoop(
        1,
        "Scenario Loop",
        "My ScenarioLoop",
        [Tag("tag-a", None, None), Tag("tag-b", None, None)],
        None,
        None,
        [],
        2,
    )
    scenario.set_feature(feature_mock)

    # when
    has_to_run = scenario.has_to_run(tagexpression, scenario_ids)

    # then
    assert has_to_run == expected_has_to_run
