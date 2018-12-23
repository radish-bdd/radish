# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.scenariooutline import ScenarioOutline
from radish.examplescenario import ExampleScenario
from radish.background import Background
from radish.stepmodel import Step
from radish.exceptions import RadishError


def test_creating_simple_scenariooutline():
    """
    Test creating a simple ScenarioOutline
    """
    # given & when
    scenario = ScenarioOutline(
        1,
        "Scenario Outline",
        "Examples",
        "I am a Scenario Outline",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )

    # then
    assert scenario.id == 1
    assert scenario.keyword == "Scenario Outline"
    assert scenario.example_keyword == "Examples"
    assert scenario.sentence == "I am a Scenario Outline"
    assert scenario.path == "foo.feature"
    assert scenario.line == 1
    assert scenario.parent is None
    assert scenario.tags == []
    assert scenario.preconditions == []
    assert scenario.background is None


def test_building_scenariooutline_scenarios(mocker):
    """
    Test building Scenarios from a Scenario Outline Example
    """
    # given
    scenario_outline = ScenarioOutline(
        1,
        "Scenario Outline",
        "Examples",
        "I am a Scenario Outline",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add steps
    scenario_outline.steps.extend(
        [
            mocker.MagicMock(sentence="Given I have <foo>", path="foo.feature"),
            mocker.MagicMock(sentence="And I have <bar>", path="foo.feature"),
            mocker.MagicMock(sentence="When I add those", path="foo.feature"),
        ]
    )
    # add examples
    scenario_outline.examples_header = ["foo", "bar"]
    scenario_outline.examples = [
        # row 0
        ScenarioOutline.Example(["1", "2"], "foo.feature", 1),
        # row 3
        ScenarioOutline.Example(["3", "4"], "foo.feature", 2),
    ]

    # when - build the scenarios
    scenario_outline.build_scenarios()

    # then - expect 2 built Scenarios
    assert len(scenario_outline.scenarios) == 2
    # then - expect that Scenarios are of type ExampleScenario
    assert all(isinstance(x, ExampleScenario) for x in scenario_outline.scenarios)
    # then - expect correct Example Scenario sentences
    assert scenario_outline.scenarios[0].sentence == "I am a Scenario Outline - row 0"
    assert scenario_outline.scenarios[1].sentence == "I am a Scenario Outline - row 1"
    # then - expect correctly replaced Step sentences
    assert scenario_outline.scenarios[0].steps[0].sentence == "Given I have 1"
    assert scenario_outline.scenarios[0].steps[1].sentence == "And I have 2"
    assert scenario_outline.scenarios[0].steps[2].sentence == "When I add those"
    assert scenario_outline.scenarios[1].steps[0].sentence == "Given I have 3"
    assert scenario_outline.scenarios[1].steps[1].sentence == "And I have 4"
    assert scenario_outline.scenarios[1].steps[2].sentence == "When I add those"


def test_building_scenariooutline_scenarios_with_background(mocker):
    """
    Test building Scenarios from a Scenario Outline Example including a Background
    """
    # given
    background = Background(
        "Background", "I am a Background", "foo.feature", 1, parent=None
    )
    # add some Steps
    background.steps.extend(
        [
            Step(1, "Foo", "foo.feature", 2, background, False),
            Step(2, "Foo", "foo.feature", 3, background, False),
        ]
    )
    scenario_outline = ScenarioOutline(
        1,
        "Scenario Outline",
        "Examples",
        "I am a Scenario Outline",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=background,
    )
    # add steps
    scenario_outline.steps.extend(
        [
            mocker.MagicMock(sentence="Given I have <foo>", path="foo.feature"),
            mocker.MagicMock(sentence="And I have <bar>", path="foo.feature"),
            mocker.MagicMock(sentence="When I add those", path="foo.feature"),
        ]
    )
    # add examples
    scenario_outline.examples_header = ["foo", "bar"]
    scenario_outline.examples = [
        # row 0
        ScenarioOutline.Example(["1", "2"], "foo.feature", 1),
        # row 3
        ScenarioOutline.Example(["3", "4"], "foo.feature", 2),
    ]

    # when - build the scenarios
    scenario_outline.build_scenarios()

    # then - expect ExampleScenarios to have background copy assigned
    assert scenario_outline.scenarios[0].background.sentence == "I am a Background"
    assert scenario_outline.scenarios[1].background.sentence == "I am a Background"


def test_scenariooutline_example_colum_width():
    """
    Test calculation for maximum width of Example columns
    """
    # given
    scenario_outline = ScenarioOutline(
        1,
        "Scenario Outline",
        "Examples",
        "I am a Scenario Outline",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add examples
    scenario_outline.examples_header = ["foo", "bar"]
    scenario_outline.examples = [
        # row 0
        ScenarioOutline.Example(["Spiderman", "Batman"], "foo.feature", 1),
        # row 3
        ScenarioOutline.Example(["Peter", "Bruce Wayne"], "foo.feature", 2),
    ]

    # when
    index_0_width = scenario_outline.get_column_width(0)
    # then
    assert index_0_width == len("Spiderman")

    # when
    index_1_width = scenario_outline.get_column_width(1)
    # then
    assert index_1_width == len("Bruce Wayne")


def test_scenariooutline_example_invalid_colum_width():
    """
    Test invalid column id exception when calculating column width for Scenario Outline Examples
    """
    # given
    scenario_outline = ScenarioOutline(
        1,
        "Scenario Outline",
        "Examples",
        "I am a Scenario Outline",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add examples
    scenario_outline.examples_header = ["foo", "bar"]
    scenario_outline.examples = [
        # row 0
        ScenarioOutline.Example(["Spiderman", "Batman"], "foo.feature", 1),
        # row 3
        ScenarioOutline.Example(["Peter", "Bruce Wayne"], "foo.feature", 2),
    ]

    # when
    with pytest.raises(RadishError) as exc:
        scenario_outline.get_column_width(42)

    # then
    assert (
        str(exc.value)
        == "Invalid colum_index to get column width for ScenarioOutline 'I am a Scenario Outline'"
    )


def test_scenariooutline_afterparse_logic(mocker):
    """
    Test Scenario Outline after parse logic
    """
    # given
    scenario_outline = ScenarioOutline(
        1,
        "Scenario Outline",
        "Examples",
        "I am a Scenario Outline",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add steps
    scenario_outline.steps.extend(
        [
            mocker.MagicMock(sentence="Given I have <foo>", path="foo.feature"),
            mocker.MagicMock(sentence="And I have <bar>", path="foo.feature"),
            mocker.MagicMock(sentence="When I add those", path="foo.feature"),
        ]
    )
    # add examples
    scenario_outline.examples_header = ["foo", "bar"]
    scenario_outline.examples = [
        # row 0
        ScenarioOutline.Example(["1", "2"], "foo.feature", 1),
        # row 3
        ScenarioOutline.Example(["3", "4"], "foo.feature", 2),
    ]

    # when
    scenario_outline.after_parse()

    # then - expect 2 built Scenarios
    assert len(scenario_outline.scenarios) == 2
    assert scenario_outline.complete is True
