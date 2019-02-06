# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.runner import Runner
from radish.stepmodel import Step


@pytest.mark.parametrize(
    "run_state, expected_returncode",
    [
        (Step.State.PASSED, 0),
        (Step.State.UNTESTED, 0),
        (Step.State.SKIPPED, 0),
        (Step.State.PENDING, 0),
        (Step.State.FAILED, 1),
    ],
    ids=[
        "Running Step returing PASSED",
        "Running Step returing UNTESTED",
        "Running Step returing SKIPPED",
        "Running Step returing PENDING",
        "Running Step returing FAILED",
    ],
)
def test_run_single_step(run_state, expected_returncode, hookregistry, mocker):
    """
    Test running a single Step
    """
    # given
    runner = Runner(hookregistry)
    step = mocker.MagicMock()
    step.run.return_value = run_state

    # when
    returncode = runner.run_step(step)

    # then
    assert returncode == expected_returncode
    assert step.run.call_count == 1


@pytest.mark.parametrize(
    "debug_state, expected_returncode",
    [
        (Step.State.PASSED, 0),
        (Step.State.UNTESTED, 0),
        (Step.State.SKIPPED, 0),
        (Step.State.PENDING, 0),
        (Step.State.FAILED, 1),
    ],
    ids=[
        "Debugging Step returing PASSED",
        "Debugging Step returing UNTESTED",
        "Debugging Step returing SKIPPED",
        "Debugging Step returing PENDING",
        "Debugging Step returing FAILED",
    ],
)
def test_debug_single_step(
    debug_state, expected_returncode, world_config, hookregistry, mocker
):
    """
    Test debugging a single Step
    """
    # given
    runner = Runner(hookregistry)
    step = mocker.MagicMock()
    step.debug.return_value = debug_state

    # set debug mode
    world_config.debug_steps = True

    # when
    returncode = runner.run_step(step)

    # then
    assert returncode == expected_returncode
    assert step.debug.call_count == 1


def test_run_single_step_show_only(hookregistry, mocker):
    """
    Test running single step when show only mode is on
    """
    # given
    runner = Runner(hookregistry, show_only=True)
    step = mocker.MagicMock()
    step.run.return_value = Step.State.FAILED

    # when
    returncode = runner.run_step(step)

    # then
    assert returncode == 0
    assert step.run.call_count == 0


def test_skip_single_step(hookregistry, mocker):
    """
    Test skipping a single Step
    """
    # given
    runner = Runner(hookregistry)
    step = mocker.MagicMock()
    step.skip.return_value = None

    # when
    runner.skip_step(step)

    # then
    assert step.skip.call_count == 1


@pytest.mark.parametrize("run_or_skip", ["run_step", "skip_step"])
def test_run_skip_step_hooks(run_or_skip, hookregistry, mocker):
    """
    Test that Hooks are executed when running or skipping a Step
    """
    # given
    # register hooks in registry
    before_step_stub = mocker.stub()
    after_step_stub = mocker.stub()
    hookregistry.register("before", "each_step", before_step_stub)
    hookregistry.register("after", "each_step", after_step_stub)
    # create runner
    runner = Runner(hookregistry, show_only=True)

    step = mocker.MagicMock(all_tags=[])

    # when
    method = getattr(runner, run_or_skip)
    method(step)

    # then
    assert before_step_stub.call_count == 1
    assert after_step_stub.call_count == 1


def test_should_call_hooks_in_correct_order(hookregistry, mocker):
    """
    Test that hooks are called in correct order.

    Correct order meaning:
        * before hooks: ascending order
        * after hooks: descending order
    """
    # given
    runner = Runner(hookregistry)

    # register hooks
    data = []

    def first_before_stub(*args):
        data.append(1)

    def first_after_stub(*args):
        data.append(1)

    def second_before_stub(*args):
        data.append(2)

    def second_after_stub(*args):
        data.append(2)

    hookregistry.register("before", "each_step", second_before_stub, order=2)
    hookregistry.register("after", "each_step", second_after_stub, order=2)
    hookregistry.register("before", "each_step", first_before_stub, order=1)
    hookregistry.register("after", "each_step", first_after_stub, order=1)

    # setup dummy step
    step = mocker.MagicMock()

    # when
    runner.run_step(step)

    # then
    assert data == [1, 2, 2, 1]
