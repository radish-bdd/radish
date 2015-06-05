# -*- coding: utf-8 -*-

"""
    Providing radish core functionality like the feature file Runner.
"""


class Runner(object):
    """
        Represents a class which is able to run features.
    """
    def __init__(self, features, hooks):
        self._features = features
        self._hooks = hooks

    def start(self):
        """
            Start running features
        """
        self._hooks.call("before", "all", self._features)
        for feature in self._features:
            self.run_feature(feature)
        self._hooks.call("after", "all", self._features)

    def run_feature(self, feature):
        """
            Runs the given feature

            :param Feature feature: the feature to run
        """
        self._hooks.call("before", "each_feature", feature)
        for scenario in feature.all_scenarios:
            self.run_scenario(scenario)
        self._hooks.call("after", "each_feature", feature)

    def run_scenario(self, scenario):
        """
            Runs the given scenario

            :param Scenario scenario: the scnenario to run
        """
        self._hooks.call("before", "each_scenario", scenario)
        for step in scenario.steps:
            self.run_step(step)
        self._hooks.call("after", "each_scenario", scenario)

    def run_step(self, step):
        """
            Runs the given step

            :param Step step: the step to run
        """
        self._hooks.call("before", "each_step", step)
        step.run()
        self._hooks.call("after", "each_step", step)
