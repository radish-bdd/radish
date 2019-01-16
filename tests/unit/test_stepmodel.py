# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.stepmodel import Step
from radish.exceptions import RadishError


def test_creating_simple_step():
    """
    Test creating a simple Step
    """
    # given & when
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )

    # then
    assert step.id == 1
    assert step.sentence == "I am a Step"
    assert step.path == "foo.feature"
    assert step.line == 1
    assert step.parent is None
    assert step.runable is True
    assert step.context_class is None
    assert step.embeddings == []


def test_getting_step_context_object(mocker):
    """
    Test getting a Step's context object
    """
    # given
    scenario = mocker.MagicMock(context=42)
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=scenario,
        runable=True,
        context_class=None,
    )

    # when
    context = step.context

    # then
    assert context == 42
    assert context == scenario.context


def test_getting_expanded_sentence(mocker):
    """
    Test getting the expanded Step sentence
    """
    # given
    scenario = mocker.MagicMock(constants=[("foo", "42"), ("bar", "21"), ("bla", "33")])
    step = Step(
        1,
        "I am ${foo} and ${bar} bla",
        "foo.feature",
        1,
        parent=scenario,
        runable=True,
        context_class=None,
    )

    # when
    sentence = step.expanded_sentence

    # then
    assert sentence == "I am 42 and 21 bla"
    assert step.sentence == "I am ${foo} and ${bar} bla"


def test_getting_context_sensitive_sentence(mocker):
    """
    Test getting the context sensitive Step sentence
    """
    # given
    scenario = mocker.MagicMock(constants=[("foo", "42"), ("bar", "21"), ("bla", "33")])
    step = Step(
        1,
        "And I am ${foo} and ${bar} bla",
        "foo.feature",
        1,
        parent=scenario,
        runable=True,
        context_class="Given",
    )
    step_no_context = Step(
        1,
        "And I am ${foo} and ${bar} bla",
        "foo.feature",
        1,
        parent=scenario,
        runable=True,
        context_class=None,
    )

    # when
    sentence = step.context_sensitive_sentence
    sentence_no_context = step_no_context.context_sensitive_sentence

    # then
    assert sentence == "Given I am 42 and 21 bla"
    assert step.sentence == "And I am ${foo} and ${bar} bla"

    assert sentence_no_context == "And I am 42 and 21 bla"
    assert step_no_context.sentence == "And I am ${foo} and ${bar} bla"


@pytest.mark.parametrize(
    "given_raw_text, expected_text",
    [
        ([], ""),
        (["Hello", "World"], "Hello\nWorld"),
        (["Hello", "Awesome", "World"], "Hello\nAwesome\nWorld"),
    ],
)
def test_getting_raw_text_from_step(given_raw_text, expected_text):
    """
    Test getting a Step's raw text data
    """
    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )
    step.raw_text = given_raw_text

    # when
    text = step.text

    # then
    assert text == expected_text


@pytest.mark.parametrize("debug_or_run", [("debug"), ("run")])
def test_run_not_runable_step(debug_or_run, mock_utils_debugger):
    """
    Test running a non-runable Step
    """
    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=False,
        context_class=None,
    )

    # when
    method = getattr(step, debug_or_run)
    state = method()

    # then
    assert state == Step.State.UNTESTED


def test_run_step_with_invalid_defintion_func():
    """
    Test running a Step with an invalid definition function
    """
    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )

    # when the Step doesn't have a definition function
    with pytest.raises(RadishError) as exc:
        step.run()
    # then the Step fails with an Exception
    assert str(exc.value) == "The step 'I am a Step' does not have a step definition"

    # when the Step has a non-callable definition function
    step.definition_func = "not-callable"
    with pytest.raises(RadishError) as exc:
        step.run()
    # then the step fails with an Exception
    assert str(exc.value) == "The step 'I am a Step' does not have a step definition"


class StepHelper(object):
    """Helper class only used for mocking"""

    @staticmethod
    def step_func(step, foo=None, bar=None):
        """
        Helper Step Definition Function.
        """
        pass

    @staticmethod
    def step_pending_func(step):
        """
        Helper Step Definition Function which
        sets the Step to PENDING
        """
        step.pending()

    @staticmethod
    def step_fail_func(step):
        """
        Helper Step Definition Function which fails the Step
        """
        raise AssertionError("failing step")

    @staticmethod
    def step_skip_func(step):
        """
        Helper Step Definition Function which skips the step
        """
        step.skip()

@pytest.mark.parametrize("debug_or_run", [("run"), ("debug")])
def test_run_debug_step_function_with_kwargs(debug_or_run, mocker, mock_utils_debugger):
    """
    Test running/debugging a Step with a function and keyword arguments
    """
    # mock step function which is to use
    mocker.spy(StepHelper, "step_func")

    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )
    step.definition_func = StepHelper.step_func
    step.argument_match = mocker.MagicMock()
    step.argument_match.evaluate.return_value = (tuple(), {"foo": "1", "bar": "2"})

    # when
    method = getattr(step, debug_or_run)
    state = method()

    # then
    assert state == Step.State.PASSED
    StepHelper.step_func.assert_called_once_with(step, foo="1", bar="2")


@pytest.mark.parametrize("debug_or_run", [("run"), ("debug")])
def test_run_debug_step_function_with_posargs(
    debug_or_run, mocker, mock_utils_debugger
):
    """
    Test running/debugging a Step with a function and positional arguments
    """
    # mock step function which is to use
    mocker.spy(StepHelper, "step_func")

    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )
    step.definition_func = StepHelper.step_func
    step.argument_match = mocker.MagicMock()
    step.argument_match.evaluate.return_value = ((1, 2), {})

    # when
    method = getattr(step, debug_or_run)
    state = method()

    # then
    assert state == Step.State.PASSED
    StepHelper.step_func.assert_called_once_with(step, 1, 2)


@pytest.mark.parametrize("debug_or_run", [("run"), ("debug")])
def test_run_debug_step_function_mark_pending(
    debug_or_run, mocker, mock_utils_debugger
):
    """
    Test running/debugging a Step which marks itself as pending
    """
    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )
    step.definition_func = StepHelper.step_pending_func
    step.argument_match = mocker.MagicMock()
    step.argument_match.evaluate.return_value = (tuple(), {})

    # when
    method = getattr(step, debug_or_run)
    state = method()

    # then
    assert state == Step.State.PENDING == step.state


@pytest.mark.parametrize("debug_or_run", [("run"), ("debug")])
def test_run_debug_step_function_mark_skipped(
    debug_or_run, mocker, mock_utils_debugger
):
    """
    Test running/debugging a Step which marks itself as skipped
    """
    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )
    step.definition_func = StepHelper.step_skip_func
    step.argument_match = mocker.MagicMock()
    step.argument_match.evaluate.return_value = (tuple(), {})

    # when
    method = getattr(step, debug_or_run)
    state = method()

    # then
    assert state == Step.State.SKIPPED == step.state


@pytest.mark.parametrize("debug_or_run", [("run"), ("debug")])
def test_run_debug_step_function_with_exception(
    debug_or_run, mocker, mock_utils_debugger
):
    """
    Test running/debugging a Step which raises an Exception
    """
    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )
    step.definition_func = StepHelper.step_fail_func
    step.argument_match = mocker.MagicMock()
    step.argument_match.evaluate.return_value = (tuple(), {})

    # when
    method = getattr(step, debug_or_run)
    state = method()

    # then
    assert state == step.state == Step.State.FAILED
    assert step.failure is not None
    assert step.failure.reason == "failing step"
    assert step.failure.name == "AssertionError"


def test_skip_a_step():
    """
    Test skipping a Step
    """
    # given
    step = Step(
        1,
        "I am a Step",
        "foo.feature",
        1,
        parent=None,
        runable=True,
        context_class=None,
    )

    # when
    step.skip()

    # then
    assert step.state == Step.State.SKIPPED
