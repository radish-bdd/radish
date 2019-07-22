"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import textwrap
from datetime import timedelta

import colorful as cf

from radish.hookregistry import before, after
from radish.models import DefaultRule
from radish.models.state import State

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

        print(INDENT_STEP + background, flush=True)

        # TODO: write background steps
        for step in feature.background.steps:
            write_step(step, cf.deepSkyBlue3, indentation=INDENT_STEP + INDENT_STEP)

        print("", flush=True)


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
    write_step(step, cf.orange)


@after.each_step()
def write_step_result(step):
    """Write the Step after it's ran"""
    step_color_func = None
    if step.state == State.PASSED:
        step_color_func = cf.forestGreen
    elif step.state == State.FAILED:
        step_color_func = cf.firebrick
    elif step.state == State.PENDING:
        step_color_func = cf.orange
    else:
        step_color_func = cf.deepSkyBlue3

    print(LINE_UP_JUMP, end="", flush=True)

    write_step(step, step_color_func)

    if step.failure_report:
        indentation_level = 2 if isinstance(step.rule, DefaultRule) else 3
        indentation = INDENT_STEP * indentation_level
        failure_report_indentation = indentation + INDENT_STEP
        report = step.failure_report
        print(
            step_color_func(
                textwrap.indent(report.traceback, failure_report_indentation)
            ),
            end="",
            flush=True,
        )


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


def write_step(step, step_color_func, indentation=None):
    """Write a Step with the given color function"""
    if indentation is None:
        indentation_level = 2 if isinstance(step.rule, DefaultRule) else 3
        indentation = INDENT_STEP * indentation_level

    step_text = "{step_keyword} {text}".format(
        step_keyword=step_color_func(step.keyword), text=step_color_func(step.text)
    )

    print(indentation + step_text, flush=True)

    if step.doc_string is not None:
        doc_string_indentation = indentation + INDENT_STEP
        print(doc_string_indentation + step_color_func('"""'), flush=True)
        print(
            cf.orange(textwrap.indent(step.doc_string, doc_string_indentation)),
            flush=True,
        )
        print(step_color_func(doc_string_indentation + '"""'), flush=True)

    if step.data_table is not None:
        data_table_indentation = indentation + INDENT_STEP
        print(data_table_indentation + step_color_func(step.data_table), flush=True)
