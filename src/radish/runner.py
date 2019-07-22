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

    def __init__(self, step_registry, hook_registry):
        self.step_registry = step_registry
        self.hook_registry = hook_registry

    @with_hooks("all")
    def start(self, features):
        """Start the Runner"""
        for feature in features:
            self.run_feature(feature)

    @with_hooks("each_feature")
    def run_feature(self, feature: Feature):
        """Run the given Feature"""
        for rule in feature.rules:
            self.run_rule(rule)

    @with_hooks("each_rule")
    def run_rule(self, rule: Rule):
        for scenario in rule.scenarios:
            if isinstance(scenario, ScenarioOutline):
                self.run_scenario_outline(scenario)
            elif isinstance(scenario, ScenarioLoop):
                self.run_scenario_loop(scenario)
            else:
                self.run_scenario(scenario)

    def run_scenario_outline(self, scenario_outline: ScenarioOutline):
        for scenario in scenario_outline.examples:
            self.run_scenario(scenario)

    def run_scenario_loop(self, scenario_loop: ScenarioLoop):
        for scenario in scenario_loop.examples:
            self.run_scenario(scenario)

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
