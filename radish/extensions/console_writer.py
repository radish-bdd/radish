# -*- coding: utf-8 -*-

"""
    This radish extension provides the functionality to write the feature file run to the console.
"""

from colorful import colorful

from radish.terrain import before, after
from radish.scenariooutline import ScenarioOutline
from radish.step import Step


def write(text):
    """
        Writes the given text to console
    """
    print(text)


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
    output = "\r\033[A\033[K        {}".format(color_func(step.sentence))

    if step.state == step.State.FAILED:
        output += "\n        {}: {}\n".format(step.failure.name, step.failure.reason)

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
        output += "\r\033[A\033[K        {0} {1} {0}".format(colored_pipe, (" {} ").format(colored_pipe).join(color_func("{1: <{0}}".format(scenario.parent.get_column_width(i), x)) for i, x in enumerate(scenario.example.data)))

    if output:
        write(output)


@after.each_feature  # pylint: disable=no-member
def console_writer_after_each_feature(feature):  # pylint: disable=unused-argument
    """
        Writes a newline after each feature

        :param Feature feature: the feature which was ran.
    """
    write("")
