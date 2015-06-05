# -*- coding: utf-8 -*-

"""
    This radish extension provides the functionality to write the feature file run to the console.
"""

from colorful import colorful

from radish.terrain import before, after


def write(text):
    """
        Writes the given text to console
    """
    print(text)


@before.each_feature  # pylint: disable=no-member
def console_writer_before_each_feature(feature):
    """
        Writes feature header to the console

        :param Feature feature: the feature to write to the console
    """
    leading = "    " if feature.description else ""
    trailing = "\n" if feature.description else ""
    output = """{}: {}
{}{}{}""".format(colorful.bold_white(feature.keyword), colorful.bold_white(feature.sentence), leading, colorful.white("\n    ".join(feature.description)), trailing)
    write(output)


@before.each_scenario  # pylint: disable=no-member
def console_writer_before_each_scenario(scenario):
    """
        Writes the scenario header to the console

        :param Scenario scenario: the scenario to write to the console
    """
    output = """    {}: {}""".format(colorful.bold_white(scenario.keyword), colorful.bold_white(scenario.sentence))
    write(output)


@before.each_step  # pylint: disable=no-member
def console_writer_before_each_step(step):
    """
        Writes the step to the console before it is run

        :param Step step: the step to write to the console
    """
    output = "\r        {}".format(colorful.bold_brown(step.sentence))
    write(output)


@after.each_step  # pylint: disable=no-member
def console_writer_after_each_step(step):
    """
        Writes the step to the console after it was run

        :param Step step: the step to write to the console
    """
    color_func = None
    if step.state == step.State.PASSED:
        color_func = colorful.bold_green
    elif step.state == step.State.FAILED:
        color_func = colorful.bold_red
    elif step.state:
        color_func = colorful.cyan

    output = "\r\033[A\033[K        {}".format(color_func(step.sentence))

    if step.state == step.State.FAILED:
        output += "\n        {}: {}\n".format(step.failure.name, step.failure.reason)

    write(output)


@after.each_scenario  # pylint: disable=no-member
def console_writer_after_each_scenario(scenario):  # pylint: disable=unused-argument
    """
        Writes a newline after each scenario

        :param Scenario scenario: the scenario which was ran.
    """
    write("")  # new line is written by the write function
