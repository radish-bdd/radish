# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

from radish.scenarioloop import ScenarioLoop
from radish.iterationscenario import IterationScenario
from radish.background import Background
from radish.stepmodel import Step


def test_creating_simple_scenarioloop():
    """
    Test creating a simple ScenarioLoop
    """
    # given & when
    scenario = ScenarioLoop(
        1,
        "Scenario Loop",
        "Iterations",
        "I am a Scenario Loop",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )

    # then
    assert scenario.id == 1
    assert scenario.keyword == "Scenario Loop"
    assert scenario.iterations_keyword == "Iterations"
    assert scenario.sentence == "I am a Scenario Loop"
    assert scenario.path == "foo.feature"
    assert scenario.line == 1
    assert scenario.parent is None
    assert scenario.tags == []
    assert scenario.preconditions == []
    assert scenario.background is None


def test_building_scenarioloop_scenarios(mocker):
    """
    Test building Scenarios from a Scenario Loop
    """
    # given
    scenario_loop = ScenarioLoop(
        1,
        "Scenario Loop",
        "Iterations",
        "I am a Scenario Loop",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add steps
    scenario_loop.steps.extend(
        [
            mocker.MagicMock(sentence="Given I have 1", path="foo.feature"),
            mocker.MagicMock(sentence="And I have 2", path="foo.feature"),
            mocker.MagicMock(sentence="When I add those", path="foo.feature"),
        ]
    )
    # set iterations
    scenario_loop.iterations = 2

    # when - build the scenarios
    scenario_loop.build_scenarios()

    # then - expect 2 built Scenarios
    assert len(scenario_loop.scenarios) == 2
    # then - expect that Scenarios are of type ExampleScenario
    assert all(isinstance(x, IterationScenario) for x in scenario_loop.scenarios)
    # then - expect correct Example Scenario sentences
    assert scenario_loop.scenarios[0].sentence == "I am a Scenario Loop - iteration 0"
    assert scenario_loop.scenarios[1].sentence == "I am a Scenario Loop - iteration 1"
    # then - expect correctly replaced Step sentences
    assert scenario_loop.scenarios[0].steps[0].sentence == "Given I have 1"
    assert scenario_loop.scenarios[0].steps[1].sentence == "And I have 2"
    assert scenario_loop.scenarios[0].steps[2].sentence == "When I add those"
    assert scenario_loop.scenarios[1].steps[0].sentence == "Given I have 1"
    assert scenario_loop.scenarios[1].steps[1].sentence == "And I have 2"
    assert scenario_loop.scenarios[1].steps[2].sentence == "When I add those"


def test_building_scenarioloop_scenarios_with_background(mocker):
    """
    Test building Scenarios from a Scenario Loop including a Background
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
    scenario_loop = ScenarioLoop(
        1,
        "Scenario Loop",
        "Iterations",
        "I am a Scenario Loop",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=background,
    )
    # add steps
    scenario_loop.steps.extend(
        [
            mocker.MagicMock(sentence="Given I have 1", path="foo.feature"),
            mocker.MagicMock(sentence="And I have 2", path="foo.feature"),
            mocker.MagicMock(sentence="When I add those", path="foo.feature"),
        ]
    )
    # set iterations
    scenario_loop.iterations = 2

    # when - build the scenarios
    scenario_loop.build_scenarios()

    # then - expect ExampleScenarios to have background copy assigned
    assert scenario_loop.scenarios[0].background.sentence == "I am a Background"
    assert scenario_loop.scenarios[1].background.sentence == "I am a Background"


def test_scenarioloop_afterparse_logic(mocker):
    """
    Test Scenario Loop after parse logic
    """
    # given
    scenario_loop = ScenarioLoop(
        1,
        "Scenario Loop",
        "Iterations",
        "I am a Scenario Loop",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add steps
    scenario_loop.steps.extend(
        [
            mocker.MagicMock(sentence="Given I have 1", path="foo.feature"),
            mocker.MagicMock(sentence="And I have 2", path="foo.feature"),
            mocker.MagicMock(sentence="When I add those", path="foo.feature"),
        ]
    )
    # set iterations
    scenario_loop.iterations = 2

    # when
    scenario_loop.after_parse()

    # then - expect 2 built Scenarios
    assert len(scenario_loop.scenarios) == 2
    assert scenario_loop.complete is True
