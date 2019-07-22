"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import radish.matcher as matcher
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
                self.hook_registry.call(what, "before", model, *args, **kwargs)
                try:
                    return func(self, model, *args, **kwargs)
                finally:
                    self.hook_registry.call(what, "after", model, *args, **kwargs)

            return __wrapper

        return __decorator

    def __init__(self, config, step_registry, hook_registry):
        self.config = config
        self.step_registry = step_registry
        self.hook_registry = hook_registry

    @with_hooks("all")
    def start(self, features):
        """Start the Runner"""
        for feature in features:
            if not feature.has_to_run(self.config.tag_expression, self.config.scenario_ids):
                continue

            state = self.run_feature(feature)
            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    @with_hooks("each_feature")
    def run_feature(self, feature: Feature):
        """Run the given Feature"""
        for rule in feature.rules:
            # check if this Rule has to be run
            if not rule.has_to_run(self.config.tag_expression, self.config.scenario_ids):
                continue

            state = self.run_rule(rule)
            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    @with_hooks("each_rule")
    def run_rule(self, rule: Rule):
        for scenario in rule.scenarios:
            # check if this Scenario has to be run
            if not scenario.has_to_run(self.config.tag_expression, self.config.scenario_ids):
                continue

            if isinstance(scenario, ScenarioOutline):
                state = self.run_scenario_outline(scenario)
            elif isinstance(scenario, ScenarioLoop):
                state = self.run_scenario_loop(scenario)
            else:
                state = self.run_scenario(scenario)

            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    def run_scenario_outline(self, scenario_outline: ScenarioOutline):
        for scenario in scenario_outline.examples:
            # check if this Scenario has to be run
            if not scenario.has_to_run(self.config.tag_expression, self.config.scenario_ids):
                continue

            state = self.run_scenario(scenario)
            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    def run_scenario_loop(self, scenario_loop: ScenarioLoop):
        for scenario in scenario_loop.examples:
            # check if this Scenario has to be run
            if not scenario.has_to_run(self.config.tag_expression, self.config.scenario_ids):
                continue

            state = self.run_scenario(scenario)
            if state is not State.PASSED and self.config.early_exit:
                return state

        return State.PASSED

    @with_hooks("each_scenario")
    def run_scenario(self, scenario: Scenario):
        # run background steps
        if scenario.background:
            for step in scenario.background.steps:
                state = self.run_step(step)
                if state is not State.PASSED:
                    break

        if not scenario.background or scenario.background.state is State.PASSED:
            for step in scenario.steps:
                state = self.run_step(step)
                if state is not State.PASSED:
                    break

        return scenario.state

    @with_hooks("each_step")
    def run_step(self, step: Step):
        try:
            # match the Step with a Step Implementation
            matcher.match_step(step, self.step_registry)
        except Exception as exc:
            step.fail(exc)
        else:
            step.run()

        return step.state
