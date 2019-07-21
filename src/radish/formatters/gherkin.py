"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from datetime import timedelta

import colorful as cf

from radish.hookregistry import before, after
from radish.models import DefaultRule

#: Holds the amount of spaces to indent per block
INDENT_STEP = " " * 4

#: Holds the ANSI escape sequence for a line up jump
LINE_UP_JUMP = "\r\033[A\033[K"


def write_tagline(tag, indentation=""):
    tagline = cf.deepSkyBlue3("@{name}".format(name=tag.name))
    print(indentation + tagline, flush=True)


@before.each_feature()
def write_feature_header(feature):
    """Write the Feature Header to stdout

    The Feature Header will be printed in the form of:

    @tag-a
    @tag-b
    Feature: short description
        description line 1
        description line 2
    """
    # write Tags
    for tag in feature.tags:
        write_tagline(tag)

    # write Feature heading
    feature_heading = "{feature_keyword} {short_description}".format(
        feature_keyword=cf.bold_white("Feature:"),
        short_description=cf.white(feature.short_description),
    )
    print(feature_heading, flush=True)

    # write Feature description if available
    if feature.description:
        feature_description = "\n".join(INDENT_STEP + l for l in feature.description)
        print(feature_description + "\n", flush=True)

    # write Background if available
    if feature.background:
        background = "{background_keyword} {short_description}".format(
            background_keyword=cf.bold_white("Background:"),
            short_description=cf.white(feature.background.short_description)
            if feature.background.short_description
            else "",
        )

        # TODO: write background steps

        print(INDENT_STEP + background + "\n", flush=True)


@after.each_feature()
def write_feature_footer(feature):
    """Write the Feature Footer

    The Feature Footer is a blank line in case the Feature
    was empty.
    """
    if not feature.description and not feature.rules:
        print("", flush=True)


@before.each_rule()
def write_rule_header(rule):
    """Write the Rule header

    The short description is only written if it's not a DefaultRule
    """
    if isinstance(rule, DefaultRule):
        return

    rule_heading = "{rule_keyword} {short_description}".format(
        rule_keyword=cf.bold_white("Rule:"),
        short_description=cf.white(rule.short_description),
    )

    print(INDENT_STEP + rule_heading + "\n", flush=True)


@before.each_scenario()
def write_scenario_header(scenario):
    """Write the Scenario header"""
    indentation_level = 1 if isinstance(scenario.rule, DefaultRule) else 2
    indentation = INDENT_STEP * indentation_level

    scenario_heading = "{scenario_keyword} {short_description}".format(
        scenario_keyword=cf.bold_white("Scenario:"),
        short_description=cf.white(scenario.short_description),
    )

    for tag in scenario.tags:
        write_tagline(tag, indentation)
    print(indentation + scenario_heading, flush=True)


@after.each_scenario()
def write_scenario_footer(scenario):
    """Write the Scenario footer"""
    print(flush=True)


@before.each_step()
def write_step_running(step):
    """Write the Step before it's running"""
    indentation_level = 2 if isinstance(step.rule, DefaultRule) else 3
    indentation = INDENT_STEP * indentation_level

    scenario_heading = "{step_keyword} {text}".format(
        step_keyword=cf.orange(step.keyword), text=cf.orange(step.text)
    )

    print(indentation + scenario_heading, flush=True)


@after.each_step()
def write_step_result(step):
    """Write the Step after it's ran"""
    indentation_level = 2 if isinstance(step.rule, DefaultRule) else 3
    indentation = INDENT_STEP * indentation_level

    scenario_heading = "{step_keyword} {text}".format(
        step_keyword=cf.forestGreen(step.keyword), text=cf.forestGreen(step.text)
    )

    print(LINE_UP_JUMP, end="", flush=True)
    print(indentation + scenario_heading, flush=True)


@after.all()
def write_endreport(features):
    """Write the end report after all Feature Files are ran"""
    total_duration = sum((f.duration() for f in features), timedelta())
    timing_information = cf.deepSkyBlue3(
        "Run finished within {duration} seconds".format(
            duration=cf.bold_deepSkyBlue3(total_duration.total_seconds())
        )
    )

    print(timing_information, flush=True)
