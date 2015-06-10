# -*- coding: utf-8 -*-

"""
    This radish extension provides the functionality to write the feature file run to the console.
"""

from datetime import timedelta
from colorful import colorful

from radish.terrain import world, before, after
from radish.scenariooutline import ScenarioOutline
from radish.step import Step
from radish.utils import console_write as write


def get_color_func(state):
    """
        Returns the color func to use
    """
    if state == Step.State.PASSED:
        return colorful.bold_green
    elif state == Step.State.FAILED:
        return colorful.bold_red
    elif state:
        return colorful.cyan


def get_line_jump_seq():
    """
        Returns the line jump ANSI sequence
    """
    line_jump_seq = ""
    if not world.config.no_ansi and not world.config.no_line_jump:
        line_jump_seq = "\r\033[A\033[K"
    return line_jump_seq


@before.each_feature  # pylint: disable=no-member
def console_writer_before_each_feature(feature):
    """
        Writes feature header to the console

        :param Feature feature: the feature to write to the console
    """
    leading = "\n    " if feature.description else ""
    output = """{}: {}{}{}""".format(colorful.bold_white(feature.keyword), colorful.bold_white(feature.sentence), leading, colorful.white("\n    ".join(feature.description)))
    write(output)


@before.each_scenario  # pylint: disable=no-member
def console_writer_before_each_scenario(scenario):
    """
        Writes the scenario header to the console

        :param Scenario scenario: the scenario to write to the console
    """
    output = "\n"
    if isinstance(scenario.parent, ScenarioOutline):
        if world.config.write_steps_once:
            return

        colored_pipe = colorful.bold_white("|")
        output = "        {0} {1} {0}".format(colored_pipe, (" {} ").format(colored_pipe).join(colorful.bold_brown("{1: <{0}}".format(scenario.parent.get_column_width(i), x)) for i, x in enumerate(scenario.example.data)))
    else:
        output += """    {}: {}""".format(colorful.bold_white(scenario.keyword), colorful.bold_white(scenario.sentence))
    write(output)


@before.each_step  # pylint: disable=no-member
def console_writer_before_each_step(step):
    """
        Writes the step to the console before it is run

        :param Step step: the step to write to the console
    """
    if isinstance(step.parent.parent, ScenarioOutline):
        return

    if world.config.write_steps_once:
        return

    output = "\r        {}".format(colorful.bold_brown(step.sentence))
    write(output)


@after.each_step  # pylint: disable=no-member
def console_writer_after_each_step(step):
    """
        Writes the step to the console after it was run

        :param Step step: the step to write to the console
    """
    if isinstance(step.parent.parent, ScenarioOutline):
        return

    color_func = get_color_func(step.state)
    output = "{}        {}".format(get_line_jump_seq(), color_func(step.sentence))

    if step.state == step.State.FAILED:
        if world.config.with_traceback:
            output += "\n          {}".format("\n          ".join([colorful.red(l) for l in step.failure.traceback.split("\n")[:-2]]))
        output += "\n          {}: {}".format(colorful.bold_red(step.failure.name), colorful.red(step.failure.reason))

    write(output)


@after.each_scenario  # pylint: disable=no-member
def console_writer_after_each_scenario(scenario):
    """
        If the scenario is a ExampleScenario it will write the Examples header

        :param Scenario scenario: the scenario which was ran.
    """
    output = ""
    if isinstance(scenario, ScenarioOutline):
        output += "\n    {}:\n".format(colorful.bold_white(scenario.example_keyword))
        output += colorful.bold_white("        | {} |".format(" | ".join("{1: <{0}}".format(scenario.get_column_width(i), x) for i, x in enumerate(scenario.examples_header))))
    elif isinstance(scenario.parent, ScenarioOutline):
        colored_pipe = colorful.bold_white("|")
        color_func = get_color_func(scenario.state)
        output += "{0}        {1} {2} {1}".format(get_line_jump_seq(), colored_pipe, (" {} ").format(colored_pipe).join(color_func("{1: <{0}}".format(scenario.parent.get_column_width(i), x)) for i, x in enumerate(scenario.example.data)))

        if scenario.state == Step.State.FAILED:
            failed_step = scenario.failed_step
            if world.config.with_traceback:
                output += "\n          {}".format("\n          ".join([colorful.red(l) for l in failed_step.failure.traceback.split("\n")[:-2]]))
            output += "\n          {}: {}".format(colorful.bold_red(failed_step.failure.name), colorful.red(failed_step.failure.reason))

    if output:
        write(output)


@after.each_feature  # pylint: disable=no-member
def console_writer_after_each_feature(feature):  # pylint: disable=unused-argument
    """
        Writes a newline after each feature

        :param Feature feature: the feature which was ran.
    """
    write("")


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

            stats["scenarios"]["amount"] += 1
            stats["scenarios"][scenario.state] += 1
            for step in scenario.steps:
                stats["steps"]["amount"] += 1
                stats["steps"][step.state] += 1

    colored_closing_paren = colorful.bold_white(")")
    colored_comma = colorful.bold_white(", ")
    passed_word = colorful.bold_green("{} passed")
    failed_word = colorful.bold_red("{} failed")
    skipped_word = colorful.cyan("{} skipped")
    untested_word = colorful.cyan("{} untested")

    output = colorful.bold_white("{} features (".format(stats["features"]["amount"]))
    output += passed_word.format(stats["features"]["passed"])
    if stats["features"]["failed"]:
        output += colored_comma + failed_word.format(stats["features"]["failed"])
    if stats["features"]["skipped"]:
        output += colored_comma + skipped_word.format(stats["features"]["skipped"])
    if stats["features"]["untested"]:
        output += colored_comma + untested_word.format(stats["features"]["untested"])
    output += colored_closing_paren

    output += "\n"
    output += colorful.bold_white("{} scenarios (".format(stats["scenarios"]["amount"]))
    output += passed_word.format(stats["scenarios"]["passed"])
    if stats["scenarios"]["failed"]:
        output += colored_comma + failed_word.format(stats["scenarios"]["failed"])
    if stats["scenarios"]["skipped"]:
        output += colored_comma + skipped_word.format(stats["scenarios"]["skipped"])
    if stats["scenarios"]["untested"]:
        output += colored_comma + untested_word.format(stats["scenarios"]["untested"])
    output += colored_closing_paren

    output += "\n"
    output += colorful.bold_white("{} steps (".format(stats["steps"]["amount"]))
    output += passed_word.format(stats["steps"]["passed"])
    if stats["steps"]["failed"]:
        output += colored_comma + failed_word.format(stats["steps"]["failed"])
    if stats["steps"]["skipped"]:
        output += colored_comma + skipped_word.format(stats["steps"]["skipped"])
    if stats["steps"]["untested"]:
        output += colored_comma + untested_word.format(stats["steps"]["untested"])
    output += colored_closing_paren

    output += "\n"
    output += colorful.cyan("Run {} finished within {}:{} minutes".format(marker, int(duration.total_seconds()) / 60, duration.total_seconds() % 60.0))

    write(output)
