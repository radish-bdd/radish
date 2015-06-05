# -*- coding: utf-8 -*-

"""
    Providing radish core functionality like the feature file Runner.
"""

from radish.exceptions import RunnerEarlyExit


class Runner(object):
    """
        Represents a class which is able to run features.
    """
    def __init__(self, features, hooks, early_exit=False):
        self._features = features
        self._hooks = hooks
        self._early_exit = early_exit

    def start(self):
        """
            Start running features
        """
        self._hooks.call("before", "all", self._features)
        try:
            for feature in self._features:
                self.run_feature(feature)
        except RunnerEarlyExit:
            return
        finally:
            self._hooks.call("after", "all", self._features)

    def run_feature(self, feature):
        """
            Runs the given feature

            :param Feature feature: the feature to run
        """
        self._hooks.call("before", "each_feature", feature)
        try:
            for scenario in feature.all_scenarios:
                self.run_scenario(scenario)
        except RunnerEarlyExit:
            raise
        finally:
            self._hooks.call("after", "each_feature", feature)

    def run_scenario(self, scenario):
        """
            Runs the given scenario

            :param Scenario scenario: the scnenario to run
        """
        # inidicates wheiter the steps should be skipped instead of running it
        skip_next = False

        self._hooks.call("before", "each_scenario", scenario)
        try:
            for step in scenario.steps:
                if skip_next:
                    self.skip_step(step)
                    continue

                self.run_step(step)

                if step.state == step.State.FAILED:
                    if self._early_exit:
                        raise RunnerEarlyExit()

                    skip_next = True
        except RunnerEarlyExit:
            raise
        finally:
            self._hooks.call("after", "each_scenario", scenario)

    def run_step(self, step):
        """
            Runs the given step

            :param Step step: the step to run
        """
        self._hooks.call("before", "each_step", step)
        step.run()
        self._hooks.call("after", "each_step", step)

    def skip_step(self, step):
        """
            Skips the given step

            :param Step step: the step to skip
        """
        self._hooks.call("before", "each_step", step)
        step.skip()
        self._hooks.call("after", "each_step", step)
