"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import textwrap

import colorful as cf

from radish.extensionregistry import extension
from radish.hookregistry import after, before
from radish.models.state import State
from radish.terrain import world

#: Holds the amount of spaces to indent per block
INDENT_STEP = " " * 4


@extension
class DotsFormatter:
    @classmethod
    def load(cls, config):
        if config.formatter == "Dots":
            return cls()
        else:
            return None

    STATE_SYMBOLS = {
        State.PASSED: ".",
        State.PENDING: "P",
        State.UNTESTED: "U",
        State.SKIPPED: "S",
        State.FAILED: "F",
    }

    def __init__(self):
        self.failed_steps = []

        before.each_feature(is_formatter=True)(self.write_feature_header)
        after.each_feature(is_formatter=True)(
            lambda *args, **kwargs: print("", flush=True)
        )

        after.each_scenario(is_formatter=True)(self.write_dot_for_scenario)
        after.each_step(is_formatter=True)(self.remember_failed_steps)

        after.all(is_formatter=True)(self.write_endreport)

    def write_feature_header(self, feature):
        print(cf.bold_white(str(feature.path)) + ":", end=" ", flush=True)

    def write_dot_for_scenario(self, scenario):
        print(self.STATE_SYMBOLS[scenario.state], end="", flush=True)

    def remember_failed_steps(self, step):
        if step.state == State.FAILED:
            self.failed_steps.append(step)

    def write_endreport(self, features):
        if not self.failed_steps:
            return

        print()
        print(cf.bold_firebrick("Failures:"), flush=True)

        for step in self.failed_steps:
            print(
                "{}: {}".format(str(step.path), step.scenario.short_description),
                flush=True,
            )
            print(INDENT_STEP + "{} {}".format(step.keyword, step.text), flush=True)

            report = step.failure_report
            failure_report_indentation = INDENT_STEP + INDENT_STEP

            if world.config.with_traceback:
                failure_information = report.traceback
            else:
                failure_information = "{}: {}\n".format(report.name, report.reason)

            print(
                cf.firebrick(
                    textwrap.indent(failure_information, failure_report_indentation)
                ),
                flush=True,
            )
