# -*- coding: utf-8 -*-

"""
Providing radish core functionality like the feature file Runner.
"""

from random import shuffle

from .terrain import world
from .scenariooutline import ScenarioOutline
from .scenarioloop import ScenarioLoop
from .stepmodel import Step


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
                return 1

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
                self._hooks.call(
                    "before", model, True, model_instance, *args, **kwargs
                )  # pylint: disable=protected-access
                try:
                    return func(self, model_instance, *args, **kwargs)
                finally:
                    self._hooks.call(
                        "after", model, False, model_instance, *args, **kwargs
                    )  # pylint: disable=protected-access

            return _wrapper

        return _decorator

    def __init__(self, hooks, early_exit=False, show_only=False):
        self._hooks = hooks
        self._early_exit = early_exit
        self._required_exit = False
        self._show_only = show_only

    @handle_exit
    @call_hooks("all")
    def start(self, features, marker):
        """
        Start running features

        :param list features: the features to run
        :param string marker: the marker for this run
        """
        if world.config.shuffle:
            shuffle(features)

        returncode = 0  # return code is set to 1 if any feature fails
        for feature in features:
            if not feature.has_to_run(world.config.scenarios):
                continue

            returncode |= self.run_feature(feature)

        if world.config.wip:
            # swap the state from 0 to 1
            # and the other way around
            returncode ^= 1

        return returncode

    @handle_exit
    @call_hooks("each_feature")
    def run_feature(self, feature):
        """
        Runs the given feature

        :param Feature feature: the feature to run
        """
        if world.config.shuffle:
            shuffle(feature.scenarios)

        returncode = 0
        for scenario in feature:
            if not scenario.has_to_run(world.config.scenarios):
                continue
            returncode |= self.run_scenario(scenario)

            if not isinstance(scenario, (ScenarioOutline, ScenarioLoop)):
                continue

            for sub_scenario in scenario.scenarios:
                returncode |= self.run_scenario(sub_scenario)
        return returncode

    @handle_exit
    @call_hooks("each_scenario")
    def run_scenario(self, scenario):
        """
        Runs the given scenario

        :param Scenario scenario: the scnenario to run
        """
        returncode = 0
        steps = scenario.all_steps if world.config.expand else scenario.steps
        for step in steps:
            if scenario.state == Step.State.FAILED:
                self.skip_step(step)
                continue

            returncode |= self.run_step(step)

            if step.state == step.State.FAILED and self._early_exit:
                self.exit()
                return 1
        return returncode

    @handle_exit
    @call_hooks("each_step")
    def run_step(self, step):
        """
            Runs the given step

            :param Step step: the step to run
        """
        if self._show_only:
            return 0

        if world.config.debug_steps:
            state = step.debug()
        else:
            state = step.run()

        return 1 if state == Step.State.FAILED else 0

    def skip_step(self, step):
        """
            Skips the given step

            :param Step step: the step to skip
        """
        self._hooks.call("before", "each_step", True, step)
        step.skip()
        self._hooks.call("after", "each_step", False, step)

    def exit(self):
        """
            Exits the runner
        """
        self._required_exit = True
