"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import pytest

from radish.errors import RadishError
from radish.models.state import State
from radish.models.step import Step
from radish.models.stepfailurereport import StepFailureReport


def test_step_is_initialized_without_a_step_impl():
    """A Step is initialized without a Step Implementation assigned to it"""
    # when
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # then
    assert step.step_impl is None
    assert step.step_impl_match is None


def test_step_is_intialized_in_untested_state():
    """A Step is initialized in the UNTESTED State"""
    # when
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # then
    assert step.state is State.UNTESTED


def test_step_is_intialized_without_a_failure_report():
    """A Step is initialized without a Failure report"""
    # when
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # then
    assert step.failure_report is None


def test_step_is_intialized_without_any_embeddings():
    """A Step is initialized without any embeddings"""
    # when
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # then
    assert step.embeddings == []


def test_step_context_returns_the_same_as_scenario_context(mocker):
    """A Steps context returns the Scenarios context it belongs to"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.context = mocker.MagicMock(name="Scenario Context")
    step.set_scenario(scenario_mock)

    # then
    assert step.context is scenario_mock.context


def test_step_can_assign_a_step_impl(mocker):
    """A Step can be assigned a Step Implementation"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")

    # when
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # then
    assert step.step_impl is step_impl_mock
    assert step.step_impl_match is step_impl_match_mock


def test_step_fail_to_run_if_no_step_impl():
    """A Step should fail to run if it has no Step Implementation assigned to it"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # then
    with pytest.raises(RadishError):
        # when
        step.run(None)


def test_step_fail_to_run_if_already_run(mocker):
    """A Step should fail to run if it was already run / has another state then UNTESTED"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step.assign_implementation(step_impl_mock, step_impl_match_mock)
    step.state = State.PASSED

    # then
    with pytest.raises(RadishError):
        # when
        step.run(None)


def test_step_should_evaluate_its_matched_step_impl_arguments(mocker):
    """A Step should evlauate the arguments of its matched Step Implementation"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step_impl_match_mock.evaluate.return_value = ([], {})
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # when
    step.run(None)

    # then
    step_impl_match_mock.evaluate.assert_called_once_with()


def test_step_should_set_state_to_running_before_running_step_impl(mocker):
    """A Step should set its State to RUNNING before it runs the Step Implementation function"""
    # given
    class WrapperForMockerSpy:
        def step_func(self, step):
            assert step.state is State.RUNNING

    w = WrapperForMockerSpy()
    mocker.spy(w, "step_func")

    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_mock.func = w.step_func
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step_impl_match_mock.evaluate.return_value = ([], {})
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # when
    step.run(None)

    # then
    w.step_func.assert_called_once_with(step)


def test_step_should_pass_evaluated_kwargs_to_step_impl_func(mocker):
    """
    A Step should pass the evaluated kwargs from the Step Implementation match function
    to the Step Implementation function.
    """
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step_impl_match_mock.evaluate.return_value = ([], {"foo": "bar", "bla": "meh"})
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # when
    step.run(None)

    # then
    step_impl_mock.func.assert_called_once_with(step, foo="bar", bla="meh")


def test_step_should_pass_evaluated_args_to_step_impl_func(mocker):
    """
    A Step should pass the evaluated args from the Step Implementation match function
    to the Step Implementation function.
    """
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step_impl_match_mock.evaluate.return_value = (["foo", "bar"], {})
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # when
    step.run(None)

    # then
    step_impl_mock.func.assert_called_once_with(step, "foo", "bar")


def test_step_fail_if_step_impl_func_raises(mocker):
    """A Step should fail if the Step Implementation function raised an Exception"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step.fail = mocker.MagicMock(name="Step fail function")
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    exception = Exception("buuh!")
    step_impl_mock.func.side_effect = exception
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step_impl_match_mock.evaluate.return_value = ([], {})
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # when
    step.run(None)

    # then
    step.fail.assert_called_once_with(exception)


def test_step_should_change_state_to_passed_if_step_impl_func_not_raised(mocker):
    """
    A Step should change its State to PASSED if the ran
    Step Implementation function did not raise any Exception
    """
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step_impl_match_mock.evaluate.return_value = ([], {})
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # when
    step.run(None)

    # then
    assert step.state is State.PASSED


def test_step_should_fail_with_failed_state_and_report():
    """When a Step is failed it should change its State to FAILED and create a report"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # when
    try:
        raise Exception("buuh!")
    except Exception as exc:
        step.fail(exc)

    # then
    assert step.state is State.FAILED
    assert isinstance(step.failure_report, StepFailureReport)


def test_step_should_be_able_to_skip_while_running():
    """A Step should be able to be skipped while it's running"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step.state = State.RUNNING

    # when
    step.skip()

    # then
    assert step.state is State.SKIPPED


def test_step_should_not_be_able_to_skip_when_not_running():
    """A Step should not be able to be skipped when it's not running"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # then
    with pytest.raises(RadishError):
        # when
        step.skip()

    assert step.state is not State.SKIPPED


def test_step_should_be_able_to_mark_pending_while_running():
    """A Step should be able to be marked pending while it's running"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step.state = State.RUNNING

    # when
    step.pending()

    # then
    assert step.state is State.PENDING


def test_step_should_not_be_able_to_mark_pending_when_not_running():
    """A Step should not be able to be marked pending when it's not running"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # then
    with pytest.raises(RadishError):
        # when
        step.pending()

    assert step.state is not State.PENDING


def test_step_should_embed_data_without_encoding():
    """A Step should be able to embed data without an encoding"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)

    # when
    step.embed("data", encode_data_to_base64=False)

    # then
    assert step.embeddings == [{"data": "data", "mime_type": "text/plain"}]


def test_step_should_embed_data_with_base64_encoding():
    """A Step should be able to embed data base64 encoded"""
    # given
    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    data_b64_encoded = "ZGF0YQ=="  # == "data"

    # when
    step.embed("data", encode_data_to_base64=True)

    # then
    assert step.embeddings == [{"data": data_b64_encoded, "mime_type": "text/plain"}]


def test_step_should_not_set_passed_state_if_state_changed_during_run(mocker):
    """A Step should not set its State to PASSED if the state was changed during the run"""
    # given
    def step_change_state(step):
        step.skip()

    step = Step(1, "keyword", "used_keyword", "text", None, None, None, None)
    step_impl_mock = mocker.MagicMock(name="Step Impl")
    step_impl_mock.func = step_change_state
    step_impl_match_mock = mocker.MagicMock(name="Step Impl Match")
    step_impl_match_mock.evaluate.return_value = ([], {})
    step.assign_implementation(step_impl_mock, step_impl_match_mock)

    # when
    step.run(None)

    # then
    assert step.state is State.SKIPPED
