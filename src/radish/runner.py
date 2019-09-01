"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import functools
import random

import radish.matcher as matcher
from radish.errors import RadishError
from radish.models import Feature, Rule, Scenario, ScenarioLoop, ScenarioOutline, Step
from radish.models.state import State


class Runner:
    """Radish Feature Runner

    The Runner takes a list of Feature File ASTs to run.
    The Steps in the AST will be matched just before
    they are run.
    """

    def with_hooks(what):
        """Call hooks for a specific model"""

        def __decorator(func):
            def __wrapper(self, model, *args, **kwargs):
                only_formatters = self.config.dry_run_mode

                self.hook_registry.call(
                    what, "before", only_formatters, model, *args, **kwargs
                )
                try:
                    return func(self, model, *args, **kwargs)
                finally:
                    self.hook_registry.call(
                        what, "after", only_formatters, model, *args, **kwargs
                    )

            return __wrapper

        return __decorator

    def __init__(self, config, step_registry, hook_registry):
        self.config = config
        self.step_registry = step_registry
        self.hook_registry = hook_registry

    @with_hooks("all")
    def start(self, features):
        """Start the Runner"""
        success_state = State.PASSED if not self.config.wip_mode else State.FAILED
        feature_states = []
        for feature in features:
            if not feature.has_to_run(
                self.config.tag_expression, self.config.scenario_ids
            ):
                continue

            state = self.run_feature(feature)
            if state is not success_state and self.config.early_exit:
                return state

            feature_states.append(feature.state)

        return not any(state is not success_state for state in feature_states)

    @with_hooks("each_feature")
    def run_feature(self, feature: Feature):
        """Run the given Feature"""
        for rule in feature.rules:
            # check if this Rule has to be run
            if not rule.has_to_run(
                self.config.tag_expression, self.config.scenario_ids
            ):
                continue

            state = self.run_rule(rule)
            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    @with_hooks("each_rule")
    def run_rule(self, rule: Rule):
        if self.config.shuffle_scenarios:
            scenarios = random.sample(rule.scenarios, len(rule.scenarios))
        else:
            scenarios = rule.scenarios

        for scenario in scenarios:
            # check if this Scenario has to be run
            if not scenario.has_to_run(
                self.config.tag_expression, self.config.scenario_ids
            ):
                continue

            if isinstance(scenario, (ScenarioOutline, ScenarioLoop)):
                state = self.run_scenario_container(scenario)
            else:
                state = self.run_scenario(scenario)

            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    def run_scenario_container(self, scenario_container):
        if self.config.shuffle_scenarios:
            scenarios = random.sample(
                scenario_container.examples, len(scenario_container.examples)
            )
        else:
            scenarios = scenario_container.examples

        for scenario in scenarios:
            # check if this Scenario has to be run
            if not scenario.has_to_run(
                self.config.tag_expression, self.config.scenario_ids
            ):
                continue

            state = self.run_scenario(scenario)
            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    @with_hooks("each_scenario")
    def run_scenario(self, scenario: Scenario):
        def __run_steps(steps):
            for step in steps:
                state = self.run_step(step)
                if self.config.dry_run_mode:
                    continue  # ignore Step states in dry run mode

                if state is State.RUNNING:
                    raise RadishError(
                        "The Step {} was still in RUNNING state after it has run".format(
                            step
                        )
                    )

                if state is State.FAILED:
                    break

        # run background steps
        if scenario.background:
            __run_steps(scenario.background.steps)

        # run precondition steps
        if scenario.preconditions:
            for precondition in scenario.preconditions:
                __run_steps(precondition.steps)

        if not scenario.background or scenario.background.state is State.PASSED:
            __run_steps(scenario.steps)

        return scenario.state

    @with_hooks("each_step")
    def run_step(self, step: Step):
        return self._run_step(step)

    def _run_step(self, step: Step):
        try:
            # match the Step with a Step Implementation
            matcher.match_step(step, self.step_registry)
        except Exception as exc:
            step.fail(exc)
        else:
            if not self.config.dry_run_mode:
                if self.config.debug_steps_mode:
                    step.debug(functools.partial(self._behave_like_runner, step))
                else:
                    step.run(functools.partial(self._behave_like_runner, step))

        return step.state

    def _behave_like_runner(self, step, step_line):
        """Wrapper function for a Step to run ``step.behave_like``"""
        behave_like_step_keyword, behave_like_step_text = step_line.split(maxsplit=1)
        behave_like_step = Step(
            step.id,
            behave_like_step_keyword,
            behave_like_step_keyword,
            behave_like_step_text,
            None,
            None,
            step.path,
            step.line,
        )
        behave_like_step.feature = step.feature
        behave_like_step.rule = step.rule
        behave_like_step.scenario = step.scenario

        return self._run_step(behave_like_step), behave_like_step
