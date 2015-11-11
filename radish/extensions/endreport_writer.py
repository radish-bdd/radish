# -*- coding: utf-8 -*-

"""
    This radish extension module provide the functionality to write the end report
"""

# disable no-member lint error because of dynamic method from colorful
# pylint: disable=no-member

from datetime import timedelta
from colorful import colorful
from radish.hookregistry import after
from radish.step import Step
from radish.utils import console_write as write
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop


@after.all  # pylint: disable=no-member
def console_write_after_all(features, marker):
    """
        Writes the endreport for all features

        :param list features: all features
    """
    stats = {
        "features": {"amount": 0, "passed": 0, "failed": 0, "skipped": 0, "untested": 0},
        "scenarios": {"amount": 0, "passed": 0, "failed": 0, "skipped": 0, "untested": 0},
        "steps": {"amount": 0, "passed": 0, "failed": 0, "skipped": 0, "untested": 0},
    }
    duration = timedelta()
    for feature in features:
        stats["features"]["amount"] += 1
        stats["features"][feature.state] += 1

        if feature.state in [Step.State.PASSED, Step.State.FAILED]:
            duration += feature.duration

        for scenario in feature.all_scenarios:
            if isinstance(scenario, ScenarioOutline):  # skip ScenarioOutlines
                continue
            if isinstance(scenario, ScenarioLoop):  # skip ScenarioLoop
                continue

            stats["scenarios"]["amount"] += 1
            stats["scenarios"][scenario.state] += 1
            for step in scenario.steps:
                stats["steps"]["amount"] += 1
                stats["steps"][step.state] += 1

    colored_closing_paren = colorful.bold_white(")")
    colored_comma = colorful.bold_white(", ")
    passed_word = colorful.bold_green("{0} passed")
    failed_word = colorful.bold_red("{0} failed")
    skipped_word = colorful.cyan("{0} skipped")

    output = colorful.bold_white("{0} features (".format(stats["features"]["amount"]))
    output += passed_word.format(stats["features"]["passed"])
    if stats["features"]["failed"]:
        output += colored_comma + failed_word.format(stats["features"]["failed"])
    if stats["features"]["skipped"]:
        output += colored_comma + skipped_word.format(stats["features"]["skipped"])
    output += colored_closing_paren

    output += "\n"
    output += colorful.bold_white("{} scenarios (".format(stats["scenarios"]["amount"]))
    output += passed_word.format(stats["scenarios"]["passed"])
    if stats["scenarios"]["failed"]:
        output += colored_comma + failed_word.format(stats["scenarios"]["failed"])
    if stats["scenarios"]["skipped"]:
        output += colored_comma + skipped_word.format(stats["scenarios"]["skipped"])
    output += colored_closing_paren

    output += "\n"
    output += colorful.bold_white("{} steps (".format(stats["steps"]["amount"]))
    output += passed_word.format(stats["steps"]["passed"])
    if stats["steps"]["failed"]:
        output += colored_comma + failed_word.format(stats["steps"]["failed"])
    if stats["steps"]["skipped"]:
        output += colored_comma + skipped_word.format(stats["steps"]["skipped"])
    output += colored_closing_paren

    output += "\n"
    output += colorful.cyan("Run {0} finished within {1}:{2} minutes".format(marker, int(duration.total_seconds()) / 60, duration.total_seconds() % 60.0))

    write(output)
