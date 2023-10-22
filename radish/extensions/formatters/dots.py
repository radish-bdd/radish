# -*- coding: utf-8 -*-

"""
This radish extension provides the functionality to write the feature file run to the console.
"""

import sys

from radish.terrain import world
from radish.hookregistry import before, after
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.stepmodel import Step
from radish.extensionregistry import extension

from radish.printer import printer, styled_text


@extension
class DotOutputFormatter(object):
    """
    Output formatter in the dot style.
    """

    LOAD_IF = staticmethod(lambda config: config.formatter == "dots")
    LOAD_PRIORITY = 30

    STATE_SYMBOLS = {
        Step.State.PASSED: ".",
        Step.State.PENDING: "P",
        Step.State.UNTESTED: "U",
        Step.State.SKIPPED: "S",
        Step.State.FAILED: "F",
    }

    def __init__(self):
        before.each_feature(self.dot_formatter_before_each_feature)
        after.each_feature(lambda *args, **kwargs: sys.stdout.printer.write("\n"))
        after.each_scenario(self.dot_formatter_after_each_scenario)
        after.each_step(self.dot_formatter_after_each_step)
        after.all(self.dot_formatter_failure_summary)

        self._failed_steps = []

    def dot_formatter_before_each_feature(self, feature):
        """
        Writes feature header to the console

        :param Feature feature: the feature to write to the console
        """
        output = styled_text(feature.path, "bold black") + ": "
        printer.write(output)

    def dot_formatter_after_each_scenario(self, scenario):
        """
        If the scenario is a ExampleScenario it will write the Examples header

        :param Scenario scenario: the scenario which was ran.
        """
        if isinstance(scenario, (ScenarioOutline, ScenarioLoop)):
            return

        sys.stdout.write(str(self.STATE_SYMBOLS[scenario.state]))

    def dot_formatter_after_each_step(self, step):
        if step.state == Step.State.FAILED:
            self._failed_steps.append(step)

    def dot_formatter_failure_summary(self, features, marker):
        """Output summary for failed Scenarios."""
        if not self._failed_steps:
            return

        output = "\n" + styled_text("Failures:", "bold red") + "\n"

        for step in self._failed_steps:
            output += "{}: {}\n    {}\n".format(step.path, step.parent.sentence, styled_text(step.sentence, "red"))
            if world.config.with_traceback:
                output += "      {}\n".format(
                    "\n      ".join([str(styled_text(l, "red")) for l in step.failure.traceback.split("\n")[:-2]])
                )
            output += "      {}: {}\n\n".format(
                styled_text(step.failure.name, "bold red"), styled_text(step.failure.reason, "red")
            )

        printer.write(output + "\n")
