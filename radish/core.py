# -*- coding: utf-8 -*-

"""
    Providing radish core functionality like the feature file Runner.
"""


class Runner(object):
    """
        Represents a class which is able to run features.
    """
    def __init__(self, features):
        self._features = features

    def start(self):
        """
            Start running features
        """
        # TODO: call before all hook
        for feature in self._features:
            self.run_feature(feature)
        # TODO: call after all hook

    def run_feature(self, feature):
        """
            Runs the given feature

            :param Feature feature: the feature to run
        """
        # TODO: call before each feature hook
        for scenario in feature.all_scenarios:
            self.run_scenario(scenario)
        # TODO: call after each feature hook

    def run_scenario(self, scenario):
        """
            Runs the given scenario

            :param Scenario scenario: the scnenario to run
        """
        # TODO: call before each scenario hook
        for step in scenario.steps:
            self.run_step(step)
        # TODO: call after each scenario hook

    def run_step(self, step):
        """
            Runs the given step

            :param Step step: the step to run
        """
        # TODO: call before each step hook
        step.run()
        # TODO: call after each step hook
