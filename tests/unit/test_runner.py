"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from unittest.mock import call, ANY

import pytest

from radish.errors import RadishError
from radish.hookregistry import HookRegistry
from radish.models import ScenarioLoop, ScenarioOutline
from radish.models.state import State
from radish.runner import Runner


@pytest.fixture(name="hook_registry", scope="function")
def setup_fake_hookregistry(mocker):
    """Setup a fake HookRegistry

    This fake HookRegistry can be used to assert called hooks.
    """
    fake_hookregistry = mocker.MagicMock(spec=HookRegistry)

    return fake_hookregistry


def test_start_run_without_features(hook_registry, default_config):
    """When starting the Runner without any Features it should pass and call the ``all`` hooks"""
    # given
    runner = Runner(default_config, None, hook_registry)

    # when
    status = runner.start([])

    # then
    assert status
    hook_registry.call.assert_has_calls(
        [call("all", "before", False, []), call("all", "after", False, [])]
    )


def test_start_run_should_iterate_all_given_features(
    hook_registry, default_config, mocker
):
    """All Features given to run should be iterated"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()

    first_feature = mocker.MagicMock(name="First Feature")
    second_feature = mocker.MagicMock(name="Second Feature")

    # when
    runner.start([first_feature, second_feature])

    # given
    runner.run_feature.assert_has_calls([call(first_feature), call(second_feature)])


def test_should_only_run_feature_which_have_to_run(
    hook_registry, default_config, mocker
):
    """The Runner should only run features which need to be run"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()

    first_feature = mocker.MagicMock(name="First Feature")
    first_feature.has_to_run.return_value = True
    second_feature = mocker.MagicMock(name="Second Feature")
    second_feature.has_to_run.return_value = False
    third_feature = mocker.MagicMock(name="Third Feature")
    third_feature.has_to_run.return_value = True

    # when
    runner.start([first_feature, second_feature, third_feature])

    # given
    runner.run_feature.assert_has_calls([call(first_feature), call(third_feature)])


def test_should_not_exit_for_failed_feature_if_early_exit_not_set(
    hook_registry, default_config, mocker
):
    """The Runner should not exit early if a Feature failes if the early exit flag is not set"""
    # given
    default_config.early_exit = False

    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()
    runner.run_feature.side_effects = [State.PASSED, State.FAILED, State.PASSED]

    first_feature = mocker.MagicMock(name="First Feature")
    second_feature = mocker.MagicMock(name="Second Feature")
    third_feature = mocker.MagicMock(name="Third Feature")

    # when
    runner.start([first_feature, second_feature, third_feature])

    # given
    runner.run_feature.assert_has_calls(
        [call(first_feature), call(second_feature), call(third_feature)]
    )


def test_should_exit_for_failed_feature_if_early_exit_set(
    hook_registry, default_config, mocker
):
    """The Runner should exit early if a Feature failes if the early exit flag is set"""
    # given
    default_config.early_exit = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()
    runner.run_feature.side_effect = [State.PASSED, State.FAILED, State.PASSED]

    first_feature = mocker.MagicMock(name="First Feature")
    second_feature = mocker.MagicMock(name="Second Feature")
    third_feature = mocker.MagicMock(name="Third Feature")

    # when
    runner.start([first_feature, second_feature, third_feature])

    # given
    runner.run_feature.assert_has_calls([call(first_feature), call(second_feature)])


def test_should_return_good_status_if_all_features_passed(
    hook_registry, default_config, mocker
):
    """
    The Runner should return a good status when finished if all features passed in normal mode
    """
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()
    runner.run_feature.side_effect = [State.PASSED, State.PASSED]

    first_feature = mocker.MagicMock(name="First Feature", state=State.PASSED)
    second_feature = mocker.MagicMock(name="Second Feature", state=State.PASSED)

    # when
    status = runner.start([first_feature, second_feature])

    # given
    assert status


def test_should_return_failed_status_if_not_all_features_passed(
    hook_registry, default_config, mocker
):
    """
    The Runner should return a failure status when finished
    if not all features passed in normal mode
    """
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()
    runner.run_feature.side_effect = [State.PASSED, State.FAILED]

    first_feature = mocker.MagicMock(name="First Feature", state=State.PASSED)
    second_feature = mocker.MagicMock(name="Second Feature", state=State.FAILED)

    # when
    status = runner.start([first_feature, second_feature])

    # given
    assert not status


def test_should_return_good_status_if_all_features_failed_in_wip_mode(
    hook_registry, default_config, mocker
):
    """
    The Runner should return a good status when finished if all features failed in WIP mode
    """
    # given
    default_config.wip_mode = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()
    runner.run_feature.side_effect = [State.FAILED, State.FAILED]

    first_feature = mocker.MagicMock(name="First Feature", state=State.FAILED)
    second_feature = mocker.MagicMock(name="Second Feature", state=State.FAILED)

    # when
    status = runner.start([first_feature, second_feature])

    # given
    assert status


def test_should_return_failed_status_if_any_feature_passed_in_wip_mode(
    hook_registry, default_config, mocker
):
    """
    The Runner should return a failure status when finished
    if any feature passed in WIP mode
    """
    # given
    default_config.wip_mode = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_feature = mocker.MagicMock()
    runner.run_feature.side_effect = [State.PASSED, State.FAILED]

    first_feature = mocker.MagicMock(name="First Feature", state=State.PASSED)
    second_feature = mocker.MagicMock(name="Second Feature", state=State.FAILED)

    # when
    status = runner.start([first_feature, second_feature])

    # given
    assert not status


def test_runner_should_call_hooks_when_running_a_feature(
    hook_registry, default_config, mocker
):
    """The Runner should call the ``each_feature`` hooks when running a Feature"""
    # given
    runner = Runner(default_config, None, hook_registry)
    feature_mock = mocker.MagicMock(name="Feature")

    # when
    runner.run_feature(feature_mock)

    # then
    hook_registry.call.assert_has_calls(
        [
            call("each_feature", "before", False, feature_mock),
            call("each_feature", "after", False, feature_mock),
        ]
    )


def test_runner_should_run_each_rule_in_a_feature(
    hook_registry, default_config, mocker
):
    """The Runner should run each Rule from a Feature"""
    # given
    runner = Runner(default_config, None, hook_registry)
    feature_mock = mocker.MagicMock(name="Feature")
    first_rule = mocker.MagicMock(name="First Rule")
    second_rule = mocker.MagicMock(name="Second Rule")
    feature_mock.rules = [first_rule, second_rule]
    runner.run_rule = mocker.MagicMock()

    # when
    runner.run_feature(feature_mock)

    # then
    runner.run_rule.assert_has_calls([call(first_rule), call(second_rule)])


def test_runner_should_only_run_rule_which_need_to_be_run(
    hook_registry, default_config, mocker
):
    """The Runner should run only the Rules which need to be run"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_rule = mocker.MagicMock()

    feature_mock = mocker.MagicMock(name="Feature")
    first_rule = mocker.MagicMock(name="First Rule")
    first_rule.has_to_run.return_value = True
    second_rule = mocker.MagicMock(name="Second Rule")
    second_rule.has_to_run.return_value = False
    third_rule = mocker.MagicMock(name="Third Rule")
    third_rule.has_to_run.return_value = True
    feature_mock.rules = [first_rule, second_rule, third_rule]

    # when
    runner.run_feature(feature_mock)

    # then
    runner.run_rule.assert_has_calls([call(first_rule), call(third_rule)])


def test_runner_should_not_exit_for_failed_rule_if_early_exit_flag_is_not_set(
    hook_registry, default_config, mocker
):
    """The Runner should not exit for a failed Rule if the early exit flag is not set"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_rule = mocker.MagicMock()
    runner.run_rule.side_effect = [State.PASSED, State.FAILED, State.PASSED]

    feature_mock = mocker.MagicMock(name="Feature")
    first_rule = mocker.MagicMock(name="First Rule")
    second_rule = mocker.MagicMock(name="Second Rule")
    third_rule = mocker.MagicMock(name="Third Rule")
    feature_mock.rules = [first_rule, second_rule, third_rule]

    # when
    runner.run_feature(feature_mock)

    # then
    runner.run_rule.assert_has_calls(
        [call(first_rule), call(second_rule), call(third_rule)]
    )


def test_runner_should_exit_for_failed_rule_if_early_exit_flag_is_set(
    hook_registry, default_config, mocker
):
    """The Runner should exit for a failed Rule if the early exit flag is set"""
    # given
    default_config.early_exit = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_rule = mocker.MagicMock()
    runner.run_rule.side_effect = [State.PASSED, State.FAILED, State.PASSED]

    feature_mock = mocker.MagicMock(name="Feature")
    first_rule = mocker.MagicMock(name="First Rule")
    second_rule = mocker.MagicMock(name="Second Rule")
    third_rule = mocker.MagicMock(name="Third Rule")
    feature_mock.rules = [first_rule, second_rule, third_rule]

    # when
    runner.run_feature(feature_mock)

    # then
    runner.run_rule.assert_has_calls([call(first_rule), call(second_rule)])


def test_runner_should_call_hooks_when_running_a_rule(
    hook_registry, default_config, mocker
):
    """The Runner should call the ``each_rule`` hooks when running a Rule"""
    # given
    runner = Runner(default_config, None, hook_registry)
    rule_mock = mocker.MagicMock(name="Rule")

    # when
    runner.run_rule(rule_mock)

    # then
    hook_registry.call.assert_has_calls(
        [
            call("each_rule", "before", False, rule_mock),
            call("each_rule", "after", False, rule_mock),
        ]
    )


def test_runner_should_iterate_all_scenarios_when_running_a_rule(
    hook_registry, default_config, mocker
):
    """The Runner should iterate all Scenarios when running a Rule"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()

    rule_mock = mocker.MagicMock(name="Rule")
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    rule_mock.scenarios = [first_scenario, second_scenario]

    # when
    runner.run_rule(rule_mock)

    # then
    runner.run_scenario.assert_has_calls([call(first_scenario), call(second_scenario)])


def test_runner_should_only_run_scenario_which_need_to_be_run(
    hook_registry, default_config, mocker
):
    """The Runner should only run Scenarios which need to be run"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()

    rule_mock = mocker.MagicMock(name="Rule")
    first_scenario = mocker.MagicMock(name="First Scenario")
    first_scenario.has_to_run.return_value = True
    second_scenario = mocker.MagicMock(name="Second Scenario")
    second_scenario.has_to_run.return_value = False
    third_scenario = mocker.MagicMock(name="Third Scenario")
    third_scenario.has_to_run.return_value = True
    rule_mock.scenarios = [first_scenario, second_scenario, third_scenario]

    # when
    runner.run_rule(rule_mock)

    # then
    runner.run_scenario.assert_has_calls([call(first_scenario), call(third_scenario)])


def test_runner_should_not_exit_for_failed_scenario_if_early_exit_flag_is_not_set(
    hook_registry, default_config, mocker
):
    """The Runner should not exit for a failed Scenario if the early exit flag is not set"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()
    runner.run_scenario.side_effect = [State.PASSED, State.FAILED, State.PASSED]

    rule_mock = mocker.MagicMock(name="Rule")
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    third_scenario = mocker.MagicMock(name="Third Scenario")
    rule_mock.scenarios = [first_scenario, second_scenario, third_scenario]

    # when
    runner.run_rule(rule_mock)

    # then
    runner.run_scenario.assert_has_calls(
        [call(first_scenario), call(second_scenario), call(third_scenario)]
    )


def test_runner_should_exit_for_failed_scenario_if_early_exit_flag_is_set(
    hook_registry, default_config, mocker
):
    """The Runner should exit for a failed Scenario if the early exit flag is set"""
    # given
    default_config.early_exit = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()
    runner.run_scenario.side_effect = [State.PASSED, State.FAILED, State.PASSED]

    rule_mock = mocker.MagicMock(name="Rule")
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    third_scenario = mocker.MagicMock(name="Third Scenario")
    rule_mock.scenarios = [first_scenario, second_scenario, third_scenario]

    # when
    runner.run_rule(rule_mock)

    # then
    runner.run_scenario.assert_has_calls([call(first_scenario), call(second_scenario)])


@pytest.mark.parametrize("scenario_container_type", [ScenarioLoop, ScenarioOutline])
def test_runner_should_run_scenario_loop_and_outline_as_scenario_container(
    scenario_container_type, hook_registry, default_config, mocker
):
    """The Runner should run a ScenarioLoop and ScenarioOutline as a Scenario Container"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario_container = mocker.MagicMock()

    rule_mock = mocker.MagicMock(name="Rule")
    scenario = mocker.MagicMock(
        name=scenario_container_type.__name__, spec=scenario_container_type
    )
    rule_mock.scenarios = [scenario]

    # when
    runner.run_rule(rule_mock)

    # then
    runner.run_scenario_container.assert_has_calls([call(scenario)])


def test_runner_should_shuffle_scenarios_in_a_rule_if_shuffle_scenarios_flag_set(
    hook_registry, default_config, mocker
):
    """
    The Runner should shuffle the Scenarios within a Rule before
    running them if the shuffle Scenarios flag is set
    """
    # given
    default_config.shuffle_scenarios = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()

    rule_mock = mocker.MagicMock(name="Rule")
    scenario = mocker.MagicMock(name="Scenario")
    rule_mock.scenarios = [scenario]

    mocker.patch("random.sample")

    # when
    runner.run_rule(rule_mock)

    # then
    import random

    random.sample.assert_called_once_with(rule_mock.scenarios, len(rule_mock.scenarios))


def test_runner_should_iterate_all_scenarios_when_running_a_scenario_container(
    hook_registry, default_config, mocker
):
    """The Runner should iterate all Scenarios when running a Scenario Container"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()

    scenario_container_mock = mocker.MagicMock(name="Scenario Container")
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    scenario_container_mock.examples = [first_scenario, second_scenario]

    # when
    runner.run_scenario_container(scenario_container_mock)

    # then
    runner.run_scenario.assert_has_calls([call(first_scenario), call(second_scenario)])


def test_runner_should_only_run_scenario_in_a_scenario_container_which_need_to_be_run(
    hook_registry, default_config, mocker
):
    """The Runner should only run Scenarios in a Scenario Container which need to be run"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()

    scenario_container_mock = mocker.MagicMock(name="Scenario Container")
    first_scenario = mocker.MagicMock(name="First Scenario")
    first_scenario.has_to_run.return_value = True
    second_scenario = mocker.MagicMock(name="Second Scenario")
    second_scenario.has_to_run.return_value = False
    third_scenario = mocker.MagicMock(name="Third Scenario")
    third_scenario.has_to_run.return_value = True
    scenario_container_mock.examples = [first_scenario, second_scenario, third_scenario]

    # when
    runner.run_scenario_container(scenario_container_mock)

    # then
    runner.run_scenario.assert_has_calls([call(first_scenario), call(third_scenario)])


def test_runner_should_not_exit_for_failed_scenario_in_scenario_container_if_early_exit_flag_is_not_set(  # noqa
    hook_registry, default_config, mocker
):
    """
    The Runner should not exit for a failed Scenario
    in Scenario Container if the early exit flag is not set
    """
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()
    runner.run_scenario.side_effect = [State.PASSED, State.FAILED, State.PASSED]

    scenario_container_mock = mocker.MagicMock(name="Scenario Container")
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    third_scenario = mocker.MagicMock(name="Third Scenario")
    scenario_container_mock.examples = [first_scenario, second_scenario, third_scenario]

    # when
    runner.run_scenario_container(scenario_container_mock)

    # then
    runner.run_scenario.assert_has_calls(
        [call(first_scenario), call(second_scenario), call(third_scenario)]
    )


def test_runner_should_exit_for_failed_scenario_in_scenario_container_if_early_exit_flag_is_set(
    hook_registry, default_config, mocker
):
    """
    The Runner should exit for a failed Scenario in
    Scenario Container if the early exit flag is set
    """
    # given
    default_config.early_exit = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()
    runner.run_scenario.side_effect = [State.PASSED, State.FAILED, State.PASSED]

    scenario_container_mock = mocker.MagicMock(name="Scenario Container")
    first_scenario = mocker.MagicMock(name="First Scenario")
    second_scenario = mocker.MagicMock(name="Second Scenario")
    third_scenario = mocker.MagicMock(name="Third Scenario")
    scenario_container_mock.examples = [first_scenario, second_scenario, third_scenario]

    # when
    runner.run_scenario_container(scenario_container_mock)

    # then
    runner.run_scenario.assert_has_calls([call(first_scenario), call(second_scenario)])


def test_runner_should_shuffle_scenarios_in_a_scenario_container_if_shuffle_scenarios_flag_set(
    hook_registry, default_config, mocker
):
    """
    The Runner should shuffle the Scenarios within a Scenario Container before
    running them if the shuffle Scenarios flag is set
    """
    # given
    default_config.shuffle_scenarios = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_scenario = mocker.MagicMock()

    scenario_container_mock = mocker.MagicMock(name="Rule")
    scenario = mocker.MagicMock(name="Scenario")
    scenario_container_mock.examples = [scenario]

    mocker.patch("random.sample")

    # when
    runner.run_scenario_container(scenario_container_mock)

    # then
    import random

    random.sample.assert_called_once_with(
        scenario_container_mock.examples, len(scenario_container_mock.examples)
    )


def test_runner_should_call_hooks_when_runner_a_scenario(
    hook_registry, default_config, mocker
):
    """The Runner should call the ``each_scenario`` hooks when running a Scenario"""
    # given
    runner = Runner(default_config, None, hook_registry)
    scenario_mock = mocker.MagicMock(name="Scenario")

    # when
    runner.run_scenario(scenario_mock)

    # then
    hook_registry.call.assert_has_calls(
        [
            call("each_scenario", "before", False, scenario_mock),
            call("each_scenario", "after", False, scenario_mock),
        ]
    )


def test_runner_should_iterate_all_steps_in_a_scenario(
    hook_registry, default_config, mocker
):
    """The Runner should iterate all Steps in a Scenario"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.return_value = State.PASSED

    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.background = None
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    scenario_mock.steps = [first_step, second_step]

    # when
    runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_has_calls([call(first_step), call(second_step)])


def test_runner_should_only_not_run_steps_in_a_scenario_if_background_not_passed(
    hook_registry, default_config, mocker
):
    """
    The Runner should not run Steps in a Scenario
    if the Background is available and did not pass.
    """
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.return_value = State.PASSED

    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.background.state = State.FAILED
    first_step = mocker.MagicMock(name="First Step")
    scenario_mock.steps = [first_step]

    # when
    runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_not_called()


def test_runner_should_only_run_steps_in_scenario_if_background_passed(
    hook_registry, default_config, mocker
):
    """
    The Runner should only run Steps in a Scenario
    if the Background is available and did pass.
    """
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.return_value = State.PASSED

    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.background.state = State.PASSED
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    scenario_mock.steps = [first_step, second_step]

    # when
    runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_has_calls([call(first_step), call(second_step)])


def test_runner_should_stop_running_steps_after_first_failed(
    hook_registry, default_config, mocker
):
    """The Runner should stop running Steps after the first Step failed in normal mode"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.side_effect = [State.PASSED, State.FAILED]

    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.background = None
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    scenario_mock.steps = [first_step, second_step]

    # when
    runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_has_calls([call(first_step)])


def test_runner_should_continue_running_steps_when_step_is_skipped_or_pending(
    hook_registry, default_config, mocker
):
    """The Runner should continue running Steps after a Step is skipped"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.side_effect = [
        State.PASSED,
        State.SKIPPED,
        State.PENDING,
        State.PASSED,
    ]

    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.background = None
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    third_step = mocker.MagicMock(name="Third Step")
    fourth_step = mocker.MagicMock(name="Fourth Step")
    scenario_mock.steps = [first_step, second_step, third_step, fourth_step]

    # when
    runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_has_calls(
        [call(first_step), call(second_step), call(third_step), call(fourth_step)]
    )


def test_runner_should_abort_if_step_is_still_running_after_running_it(
    hook_registry, default_config, mocker
):
    """The Runner should abort if a Steps State is still running after its ran"""
    # given
    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.side_effect = [State.PASSED, State.RUNNING, State.PASSED]

    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.background = None
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    third_step = mocker.MagicMock(name="Third Step")
    scenario_mock.steps = [first_step, second_step, third_step]

    # then
    with pytest.raises(RadishError):
        # when
        runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_has_calls([call(first_step), call(second_step)])


def test_runner_should_run_all_steps_even_when_failed_in_dry_run_mode(
    hook_registry, default_config, mocker
):
    """The Runner should runn all Steps even when one failed in the dry run mode"""
    # given
    default_config.dry_run_mode = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.side_effect = [State.FAILED, State.UNTESTED]

    scenario_mock = mocker.MagicMock(name="Scenario")
    scenario_mock.background = None
    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    scenario_mock.steps = [first_step, second_step]

    # when
    runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_has_calls([call(first_step), call(second_step)])


def test_runner_should_run_steps_from_a_background(
    hook_registry, default_config, mocker
):
    """The Runner should run all Steps from a Background before running the Scenario steps"""
    # given
    default_config.dry_run_mode = True

    runner = Runner(default_config, None, hook_registry)
    runner.run_step = mocker.MagicMock()
    runner.run_step.side_effect = [
        State.PASSED,
        State.PASSED,
        State.PASSED,
        State.PASSED,
    ]

    scenario_mock = mocker.MagicMock(name="Scenario")

    first_background_step = mocker.MagicMock(name="First Background Step")
    second_background_step = mocker.MagicMock(name="Second Background Step")
    scenario_mock.background.steps = [first_background_step, second_background_step]
    scenario_mock.background.state = State.PASSED

    first_step = mocker.MagicMock(name="First Step")
    second_step = mocker.MagicMock(name="Second Step")
    scenario_mock.steps = [first_step, second_step]

    # when
    runner.run_scenario(scenario_mock)

    # then
    runner.run_step.assert_has_calls(
        [
            call(first_background_step),
            call(second_background_step),
            call(first_step),
            call(second_step),
        ]
    )


def test_runner_should_call_hooks_when_running_a_step(
    hook_registry, default_config, mocker
):
    """The Runner should call the ``each_step`` hooks when running a Step"""
    # given
    runner = Runner(default_config, None, hook_registry)
    step_mock = mocker.MagicMock(name="Step")

    # when
    runner.run_step(step_mock)

    # then
    hook_registry.call.assert_has_calls(
        [
            call("each_step", "before", False, step_mock),
            call("each_step", "after", False, step_mock),
        ]
    )


def test_runner_should_run_step_after_being_matched_in_normal_mode(
    hook_registry, default_config, mocker
):
    """
    The Runner should run a Step after it's being
    successfully matched with a Step Implementation
    in the normal mode.
    """
    # given
    runner = Runner(default_config, None, hook_registry)
    step_mock = mocker.MagicMock(name="Step")

    mocker.patch("radish.runner.matcher")

    # when
    runner.run_step(step_mock)

    # then
    step_mock.run.assert_called_once_with(ANY)


def test_runner_should_debug_step_after_being_matched_in_debug_steps_mode(
    hook_registry, default_config, mocker
):
    """
    The Runner should debug a Step after it's being
    successfully matched with a Step Implementation
    in the debug steps mode.
    """
    # given
    default_config.debug_steps_mode = True

    runner = Runner(default_config, None, hook_registry)
    step_mock = mocker.MagicMock(name="Step")

    mocker.patch("radish.runner.matcher")

    # when
    runner.run_step(step_mock)

    # then
    step_mock.debug.assert_called_once_with(ANY)


def test_runner_should_not_run_nor_debug_step_after_being_matched_in_dry_run_mode(
    hook_registry, default_config, mocker
):
    """
    The Runner should not run nor debug a Step after it's being
    successfully matched with a Step Implementation in the dry run mode.
    """
    # given
    default_config.dry_run_mode = True

    runner = Runner(default_config, None, hook_registry)
    step_mock = mocker.MagicMock(name="Step")

    mocker.patch("radish.runner.matcher")

    # when
    runner.run_step(step_mock)

    # then
    step_mock.run.assert_not_called()
    step_mock.debug.assert_not_called()


def test_runner_should_fail_step_when_it_cannot_be_matched(
    hook_registry, default_config, mocker
):
    """The Runner should fail a Step when it cannot be matched with any Step Implementation"""
    runner = Runner(default_config, None, hook_registry)
    step_mock = mocker.MagicMock(name="Step")

    matcher_mock = mocker.patch("radish.runner.matcher")
    match_exc = RadishError("buuh!")
    matcher_mock.match_step.side_effect = match_exc

    # when
    runner.run_step(step_mock)

    # then
    step_mock.fail.assert_called_once_with(match_exc)
