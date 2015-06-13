# -*- coding: utf-8 -*-

"""
    Providing radish core functionality like the feature file Runner.
"""

from radish.terrain import world
from radish.step import Step


class Runner(object):
    """
        Represents a class which is able to run features.
    """

    def handle_exit(func):  # pylint: disable=no-self-argument
        """
            Handles an runner exit
        """
        def _decorator(self, *args, **kwargs):
            """
                Actual decorator
            """
            if self._required_exit:  # pylint: disable=protected-access
                return None

            return func(self, *args, **kwargs)  # pylint: disable=not-callable
        return _decorator

    def call_hooks(model):  # pylint: disable=no-self-argument
        """
            Call hooks for a specific model
        """
        def _decorator(func):
            """
                The actual decorator
            """
            def _wrapper(self, model_instance, *args, **kwargs):
                """
                    Decorator wrapper
                """
                self._hooks.call("before", model, model_instance, *args, **kwargs)  # pylint: disable=protected-access
                try:
                    return func(self, model_instance, *args, **kwargs)
                finally:
                    self._hooks.call("after", model, model_instance, *args, **kwargs)  # pylint: disable=protected-access
            return _wrapper
        return _decorator

    def __init__(self, hooks, early_exit=False):
        self._hooks = hooks
        self._early_exit = early_exit
        self._required_exit = False

    @handle_exit
    @call_hooks("all")
    def start(self, features, marker):
        """
            Start running features

            :param list features: the features to run
            :param string marker: the marker for this run
        """
        for feature in features:
            if not feature.has_to_run(world.config.scenarios):
                continue

            self.run_feature(feature)

    @handle_exit
    @call_hooks("each_feature")
    def run_feature(self, feature):
        """
            Runs the given feature

            :param Feature feature: the feature to run
        """
        for scenario in feature.all_scenarios:
            if not scenario.has_to_run(world.config.scenarios):
                continue
            self.run_scenario(scenario)

    @handle_exit
    @call_hooks("each_scenario")
    def run_scenario(self, scenario):
        """
            Runs the given scenario

            :param Scenario scenario: the scnenario to run
        """
        for step in scenario.steps:
            if scenario.state == Step.State.FAILED:
                self.skip_step(step)
                continue

            self.run_step(step)

            if step.state == step.State.FAILED and self._early_exit:
                self.exit()
                return

    @handle_exit
    @call_hooks("each_step")
    def run_step(self, step):
        """
            Runs the given step

            :param Step step: the step to run
        """
        if world.config.debug_steps:
            step.debug()
        else:
            step.run()

    def skip_step(self, step):
        """
            Skips the given step

            :param Step step: the step to skip
        """
        self._hooks.call("before", "each_step", step)
        step.skip()
        self._hooks.call("after", "each_step", step)

    def exit(self):
        """
            Exits the runner
        """
        self._required_exit = True
