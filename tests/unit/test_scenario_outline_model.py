"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest
from tagexpressions import parse

from radish.models import ScenarioOutline, Tag


def test_scenariooutline_set_feature_on_all_examples(mocker):
    """A ScenarioOutline should forward a set Feature to all its Examples"""
    # given
    feature_mock = mocker.MagicMock(name="Feature")
    scenario = ScenarioOutline(
        1, "Scenario Outline", "My ScenarioOutline", [], None, None, [], []
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


def test_scenariooutline_set_background_on_all_examples(mocker):
    """A ScenarioOutline should forward a set Background to all its Examples"""
    # given
    background_mock = mocker.MagicMock(name="Background")
    scenario = ScenarioOutline(
        1, "Scenario Outline", "My ScenarioOutline", [], None, None, [], []
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


def test_scenariooutline_set_rule_on_all_examples(mocker):
    """A ScenarioOutline should forward a set Rule to all its Examples"""
    # given
    rule_mock = mocker.MagicMock(name="Rule")
    scenario = ScenarioOutline(
        1, "Scenario Outline", "My ScenarioOutline", [], None, None, [], []
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


def test_scenariooutline_build_examples_from_example_table():
    """A ScenarioOutline should build its Examples from the given Example Table"""
    # given & when
    scenario = ScenarioOutline(
        1,
        "Scenario Outline",
        "My ScenarioOutline",
        [],
        None,
        None,
        [],
        [{}, {}],  # two empty examples
    )

    # then
    assert len(scenario.examples) == 2


def test_scenariooutline_should_build_examples_with_info_in_short_description():
    """A ScenarioOutline should build its Examples with the Example Info in the short description"""
    # given & when
    scenario = ScenarioOutline(
        1,
        "Scenario Outline",
        "My ScenarioOutline",
        [],
        None,
        None,
        [],
        [{"foo": "bar", "bla": "meh"}, {"bar": "foo", "meh": "bla"}],
    )

    # then
    assert (
        scenario.examples[0].short_description
        == "My ScenarioOutline [foo: bar, bla: meh]"  # noqa
        # Python 3.5 has no dict ordering
        or scenario.examples[0].short_description  # noqa
        == "My ScenarioOutline [bla: meh, foo: bar]"  # noqa
    )
    assert (
        scenario.examples[1].short_description
        == "My ScenarioOutline [bar: foo, meh: bla]"  # noqa
        # Python 3.5 has no dict ordering
        or scenario.examples[1].short_description  # noqa
        == "My ScenarioOutline [meh: bla, bar: foo]"  # noqa
    )


def test_scenariooutline_should_build_examples_with_copied_steps(mocker):
    """A ScenarioOutline should build its Example with a copy of its own Steps"""
    # given & when
    scenario = ScenarioOutline(
        1,
        "Scenario Outline",
        "My ScenarioOutline",
        [],
        None,
        None,
        [mocker.MagicMock(name="First Step"), mocker.MagicMock(name="Second Step")],
        [{}, {}],
    )

    # then
    assert len(scenario.examples[0].steps) == 2
    assert len(scenario.examples[1].steps) == 2
    assert scenario.steps is not scenario.examples[0].steps
    assert scenario.steps is not scenario.examples[1].steps


def test_scenariooutline_should_build_examples_with_replaced_step_texts(mocker):
    """
    A ScenarioOutline should build its Example with Step Texts that have the Example Info replaced
    """
    # given & when
    scenario = ScenarioOutline(
        1,
        "Scenario Outline",
        "My ScenarioOutline",
        [],
        None,
        None,
        [
            mocker.MagicMock(name="First Step", text="One <foo> Three"),
            mocker.MagicMock(name="Second Step", text="Four <bar> Six"),
        ],
        [{"foo": "Two", "bar": "Five"}, {"foo": "Zwei", "bar": "Fuenf"}],
    )

    # then
    assert scenario.examples[0].steps[0].text == "One Two Three"
    assert scenario.examples[0].steps[1].text == "Four Five Six"

    assert scenario.examples[1].steps[0].text == "One Zwei Three"
    assert scenario.examples[1].steps[1].text == "Four Fuenf Six"


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
    scenario = ScenarioOutline(
        1,
        "Scenario Outline",
        "My ScenarioOutline",
        [Tag("tag-a", None, None), Tag("tag-b", None, None)],
        None,
        None,
        [],
        [{"foo": "bar"}, {"foo": "meh"}],
    )
    scenario.set_feature(feature_mock)

    # when
    has_to_run = scenario.has_to_run(tagexpression, scenario_ids)

    # then
    assert has_to_run == expected_has_to_run
