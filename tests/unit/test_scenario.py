# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.feature import Feature
from radish.scenario import Scenario
from radish.background import Background
from radish.stepmodel import Step


def test_creating_simple_scenario():
    """
    Test creating a simple Scenario
    """
    # given & when
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )

    # then
    assert scenario.id == 1
    assert scenario.keyword == "Scenario"
    assert scenario.sentence == "I am a Scenario"
    assert scenario.path == "foo.feature"
    assert scenario.line == 1
    assert scenario.parent is None
    assert scenario.tags == []
    assert scenario.preconditions == []
    assert scenario.background is None


def test_scenario_state(mocker):
    """
    Test getting the Scenario state according to it's Steps states
    """
    # given
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add Steps to this Scenario
    scenario.steps.extend(
        [
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
        ]
    )
    # get the step to modify
    step = scenario.steps[1]

    # when all Steps are passed the Scenario is passed
    assert scenario.state == Step.State.PASSED

    # when one Step is failed the Scenario is failed
    step.state = Step.State.FAILED
    assert scenario.state == Step.State.FAILED

    # when one Step is pending the Scenario is pending
    step.state = Step.State.PENDING
    assert scenario.state == Step.State.PENDING

    # when one Step is skipped the Scenario is skipped
    step.state = Step.State.SKIPPED
    assert scenario.state == Step.State.SKIPPED

    # when one Step is untested the Scenario is untested
    step.state = Step.State.UNTESTED
    assert scenario.state == Step.State.UNTESTED


def test_scenario_state_with_background(mocker):
    """
    Test getting the Scenario state according to it's Steps states including a Background
    """
    # given
    background = mocker.MagicMock(steps=[])
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=background,
    )
    # add Steps to this Scenario
    scenario.steps.extend([mocker.MagicMock(state=Step.State.PASSED)])
    # add Steps to the background
    background.steps.extend(
        [
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
        ]
    )
    # get the step to modify
    step = background.steps[1]

    # when all Steps are passed the Scenario is passed
    assert scenario.state == Step.State.PASSED

    # when a Background Step is failed the Scenario is failed
    step.state = Step.State.FAILED
    assert scenario.state == Step.State.FAILED


def test_scenario_all_steps(mocker):
    """
    Test getting all Steps which are part of a Scenario
    """
    # given
    background = mocker.MagicMock(all_steps=[])
    precondition_scenario = mocker.MagicMock(all_steps=[])
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=[precondition_scenario],
        background=background,
    )

    # when
    # add Steps to this Scenario
    scenario.steps.extend([mocker.MagicMock(state=Step.State.PASSED)])
    # add Steps to the Background
    background.all_steps.extend(
        [
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
        ]
    )
    # add Steps to the precondition Scenario
    precondition_scenario.all_steps.extend(
        [
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
        ]
    )

    # then
    assert len(scenario.all_steps) == 6


def test_get_scenario_constants():
    """
    Test getting all constants from a Scenario
    """
    # given
    feature = Feature(1, "Feature", "I am a feature", "foo.feature", 1, tags=None)
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        2,
        parent=feature,
        tags=None,
        preconditions=None,
        background=None,
    )
    # add Feature constants
    feature.context.constants = [("foo", "1"), ("bar", "42")]
    # add Scenario constants
    scenario.context.constants = [("some_foo", "${foo}3"), ("answer", "${bar}")]

    # when
    constants = scenario.constants

    assert len(constants) == 4
    assert constants[0] == ("some_foo", "13")
    assert constants[1] == ("answer", "42")
    assert constants[2] == ("foo", "1")
    assert constants[3] == ("bar", "42")


def test_scenario_failed_step(mocker):
    """
    Test getting the first failed Step from a Scenario
    """
    # given
    background = mocker.MagicMock(steps=[])
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=background,
    )

    # when
    # add Steps to this Scenario
    scenario.steps.extend([mocker.MagicMock(state=Step.State.PASSED)])
    # add Steps to the Background
    background.steps.extend(
        [
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
            mocker.MagicMock(state=Step.State.PASSED),
        ]
    )

    # when no Step failed
    assert scenario.failed_step is None

    # when a Scenario Step fails it should be returned
    scenario.steps[0].state = Step.State.FAILED
    assert scenario.failed_step == scenario.steps[0]
    scenario.steps[0].state = Step.State.PASSED

    # when a Background Step fails it should be returned
    background.steps[0].state = Step.State.FAILED
    assert scenario.failed_step == background.steps[0]
    background.steps[0].state = Step.State.PASSED

    # when a Background and a Scenario Step fails the
    # Background Step should be returned
    background.steps[0].state = Step.State.FAILED
    scenario.steps[0].state = Step.State.FAILED
    assert scenario.failed_step == background.steps[0]


@pytest.mark.parametrize(
    "scenario_id, scenario_choice, expected_has_to_run",
    [
        (1, [], True),
        (1, [1], True),
        (2, [1, 2, 5], True),
        (1, [4], False),
        (1, [4, 5], False),
    ],
)
def test_scenario_has_to_run(scenario_id, scenario_choice, expected_has_to_run):
    """
    Test logic to check whether a Scenario has to run or not
    """
    # given
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=None,
        background=None,
    )
    scenario.absolute_id = scenario_id

    # when
    actual_has_to_run = scenario.has_to_run(scenario_choice)

    # then
    assert actual_has_to_run is expected_has_to_run


def test_scenario_after_parse_logic(mocker):
    """
    Test logic which is used to complete the parsing of Scenario
    """
    # given
    background = Background(1, "Background", "I am a Background", "foo.feature", 1)
    precondition_scenario = Scenario(
        2, "Scenario", "I am a Scenario", "foo.feature", 1, parent=None
    )
    scenario = Scenario(
        1,
        "Scenario",
        "I am a Scenario",
        "foo.feature",
        1,
        parent=None,
        tags=None,
        preconditions=[precondition_scenario],
        background=background,
    )
    # add Steps to this Scenario
    scenario.steps.extend(
        [mocker.MagicMock(id=99, as_background=False, as_precondition=False)]
    )
    # set Scenario Step parents
    for step in scenario.steps:
        step.parent = scenario
    # add Steps to the Background
    background.steps.extend(
        [
            mocker.MagicMock(id=5, as_background=False, as_precondition=False),
            mocker.MagicMock(id=6, as_background=False, as_precondition=False),
            mocker.MagicMock(id=66, as_background=False, as_precondition=False),
        ]
    )
    # set Background Step parents
    for background_step in background.steps:
        background_step.parent = background
    # add Steps to the precondition Scenario
    precondition_scenario.steps.extend(
        [
            mocker.MagicMock(id=5, as_background=False, as_precondition=False),
            mocker.MagicMock(id=77, as_background=False, as_precondition=False),
        ]
    )
    # set Precondition Scenario Step parents
    for step in precondition_scenario.steps:
        step.parent = precondition_scenario

    # when after_parse() was not called it's not completed
    assert scenario.complete is False

    # when
    scenario.after_parse()
    steps = scenario.all_steps

    # then - the Scenario is completed
    assert scenario.complete is True

    # then - the step id's are in valid order
    assert steps[0].id == 1
    assert steps[1].id == 2
    assert steps[2].id == 3
    assert steps[3].id == 4
    assert steps[4].id == 5
    assert steps[5].id == 6

    # then - check as_background flags
    assert all(step.as_background for step in background.steps)
    # then - check as_precondition flags
    assert all(step.as_precondition for step in precondition_scenario.steps)
