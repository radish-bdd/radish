# -*- coding: utf-8 -*-

"""
    This radish extension provides the functionality to write the feature file run to the console.
"""

# disable no-member lint error because of dynamic method from colorful
# pylint: disable=no-member

from datetime import timedelta
from colorful import colorful

from radish.terrain import world
from radish.hookregistry import before, after
from radish.feature import Feature
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
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


def get_id_sentence_prefix(model, color_func, max_rows=None):
    """
        Returns the id from a model as sentence prefix

        :param Model model: a model with an id property
        :param function color_func: a function which gives coloring
        :param int max_rows: the maximum rows. Used for padding
    """
    padding = len("{}. ".format(max_rows)) if max_rows else 0
    return color_func("{1: >{0}}. ".format(padding, model.id)) if world.config.write_ids else ""


def get_id_padding(max_rows):
    """
        Returns the id padding
    """
    if not world.config.write_ids:
        return ""

    return " " * (max_rows + 2)


@before.each_feature  # pylint: disable=no-member
def console_writer_before_each_feature(feature):
    """
        Writes feature header to the console

        :param Feature feature: the feature to write to the console
    """
    output = ""
    for tag in feature.tags:
        output += colorful.cyan("@{}\n".format(tag.name))

    leading = "\n    " if feature.description else ""

    output += "{}{}: {}{}{}".format(
        get_id_sentence_prefix(feature, colorful.bold_cyan),
        colorful.bold_white(feature.keyword),
        colorful.bold_white(feature.sentence),
        leading,
        colorful.white("\n    ".join(feature.description))
    )
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

        id_prefix = get_id_sentence_prefix(scenario, colorful.bold_brown, len(scenario.parent.scenarios))
        colored_pipe = colorful.bold_white("|")
        output = "        {0}{1} {2} {1}".format(
            id_prefix,
            colored_pipe,
            (" {} ").format(colored_pipe).join(
                colorful.bold_brown("{1: <{0}}".format(scenario.parent.get_column_width(i), x)) for i, x in enumerate(scenario.example.data)
            )
        )
    elif isinstance(scenario.parent, ScenarioLoop):
        if world.config.write_steps_once:
            return

        id_prefix = get_id_sentence_prefix(scenario, colorful.bold_brown, len(scenario.parent.scenarios))
        colored_pipe = colorful.bold_white("|")
        output = "        {0}{1} {2: <18} {1}".format(id_prefix, colored_pipe, colorful.bold_brown(scenario.iteration))
    else:
        id_prefix = get_id_sentence_prefix(scenario, colorful.bold_cyan)
        for tag in scenario.tags:
            output += colorful.cyan("    @{}\n".format(tag.name))
        output += """    {}{}: {}""".format(id_prefix, colorful.bold_white(scenario.keyword), colorful.bold_white(scenario.sentence))
    write(output)


@before.each_step  # pylint: disable=no-member
def console_writer_before_each_step(step):
    """
        Writes the step to the console before it is run

        :param Step step: the step to write to the console
    """
    if not isinstance(step.parent.parent, Feature):
        return

    if world.config.write_steps_once:
        return

    output = "\r        {}{}".format(get_id_sentence_prefix(step, colorful.bold_brown), colorful.bold_brown(step.sentence))
    write(output)


@after.each_step  # pylint: disable=no-member
def console_writer_after_each_step(step):
    """
        Writes the step to the console after it was run

        :param Step step: the step to write to the console
    """
    if not isinstance(step.parent.parent, Feature):
        return

    color_func = get_color_func(step.state)
    output = "{}        {}{}".format(get_line_jump_seq(), get_id_sentence_prefix(step, colorful.bold_cyan), color_func(step.sentence))

    if step.state == step.State.FAILED:
        if world.config.with_traceback:
            output += "\n          {}{}".format(get_id_padding(len(step.parent.steps) - 2), "\n          ".join([colorful.red(l) for l in step.failure.traceback.split("\n")[:-2]]))
        output += "\n          {}{}: {}".format(get_id_padding(len(step.parent.steps) - 2), colorful.bold_red(step.failure.name), colorful.red(step.failure.reason))

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
        output += colorful.bold_white("        {}| {} |".format(
            get_id_padding(len(scenario.scenarios)),
            " | ".join("{1: <{0}}".format(scenario.get_column_width(i), x) for i, x in enumerate(scenario.examples_header))
        ))
    elif isinstance(scenario, ScenarioLoop):
        output += "\n    {}: {}".format(colorful.bold_white(scenario.iterations_keyword), colorful.cyan(scenario.iterations))
    elif isinstance(scenario.parent, ScenarioOutline):
        colored_pipe = colorful.bold_white("|")
        color_func = get_color_func(scenario.state)
        output += "{0}        {1}{2} {3} {2}".format(
            get_line_jump_seq(),
            get_id_sentence_prefix(scenario, colorful.bold_cyan, len(scenario.parent.scenarios)),
            colored_pipe,
            (" {} ").format(colored_pipe).join(
                color_func("{1: <{0}}".format(scenario.parent.get_column_width(i), x)) for i, x in enumerate(scenario.example.data)
            )
        )

        if scenario.state == Step.State.FAILED:
            failed_step = scenario.failed_step
            if world.config.with_traceback:
                output += "\n          {}{}".format(get_id_padding(len(scenario.parent.scenarios)), "\n          ".join([colorful.red(l) for l in failed_step.failure.traceback.split("\n")[:-2]]))
            output += "\n          {}{}: {}".format(get_id_padding(len(scenario.parent.scenarios)), colorful.bold_red(failed_step.failure.name), colorful.red(failed_step.failure.reason))
    elif isinstance(scenario.parent, ScenarioLoop):
        colored_pipe = colorful.bold_white("|")
        color_func = get_color_func(scenario.state)
        output += "{0}        {1}{2} {3: <18} {2}".format(get_line_jump_seq(), get_id_sentence_prefix(scenario, colorful.bold_cyan, len(scenario.parent.scenarios)), colored_pipe, color_func(scenario.iteration))

        if scenario.state == Step.State.FAILED:
            failed_step = scenario.failed_step
            if world.config.with_traceback:
                output += "\n          {}{}".format(get_id_padding(len(scenario.parent.scenarios)), "\n          ".join([colorful.red(l) for l in failed_step.failure.traceback.split("\n")[:-2]]))
            output += "\n          {}{}: {}".format(get_id_padding(len(scenario.parent.scenarios)), colorful.bold_red(failed_step.failure.name), colorful.red(failed_step.failure.reason))

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

    output = colorful.bold_white("{} features (".format(stats["features"]["amount"]))
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
    output += colorful.cyan("Run {} finished within {}:{} minutes".format(marker, int(duration.total_seconds()) / 60, duration.total_seconds() % 60.0))

    write(output)
