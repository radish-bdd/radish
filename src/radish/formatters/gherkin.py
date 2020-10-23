"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import itertools
import textwrap
from collections import Counter
from datetime import timedelta

import click
import colorful as cf

from radish.extensionregistry import extension
from radish.hookregistry import after, before
from radish.models import DefaultRule
from radish.models.state import State
from radish.terrain import world

#: Holds the amount of spaces to indent per block
INDENT_STEP = " " * 4

#: Holds the ANSI escape sequence for a line up jump
LINE_UP_JUMP = "\r\033[A\033[K"


@extension
class GherkinFormatter:
    OPTIONS = [
        click.Option(
            param_decls=("--no-step-rewrites", "no_step_rewrites"),
            is_flag=True,
            help=(
                "Turn off all Step rewrites. "
                "Steps are rewritten once they finished running. [GherkinFormatter]"
            ),
        )
    ]

    @classmethod
    def load(cls, config):
        if config.formatter == "Gherkin":
            return cls()
        else:
            return None

    def __init__(self):
        before.each_feature(is_formatter=True)(write_feature_header)
        after.each_feature(is_formatter=True)(write_feature_footer)

        before.each_rule(is_formatter=True)(write_rule_header)

        before.each_scenario(is_formatter=True)(write_scenario_header)
        after.each_scenario(is_formatter=True)(write_scenario_footer)

        before.each_step(is_formatter=True)(write_step_running)
        after.each_step(is_formatter=True)(write_step_result)

        after.all(is_formatter=True)(write_summary)


def write_tagline(tag, indentation=""):
    tagline = cf.deepSkyBlue3("@{name}".format(name=tag.name))
    print(indentation + tagline, flush=True)


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
    feature_heading = "{feature_keyword}: {short_description}".format(
        feature_keyword=cf.bold_white(feature.keyword),
        short_description=cf.white(feature.short_description),
    )
    print(feature_heading, flush=True)

    # write Feature description if available
    if feature.description:
        feature_description = "\n".join(
            INDENT_STEP + line for line in feature.description
        )
        print(feature_description + "\n", flush=True)

    # write Background if available
    if feature.background:
        background = "{background_keyword}: {short_description}".format(
            background_keyword=cf.bold_white(feature.background.keyword),
            short_description=cf.white(feature.background.short_description)
            if feature.background.short_description
            else "",
        )

        print(INDENT_STEP + background, flush=True)

        # TODO: write background steps
        for step in feature.background.steps:
            write_step(step, cf.deepSkyBlue3, indentation=INDENT_STEP + INDENT_STEP)

        print("", flush=True)


def write_feature_footer(feature):
    """Write the Feature Footer

    The Feature Footer is a blank line in case the Feature
    was empty.
    """
    if not feature.description and not feature.rules:
        print("", flush=True)


def write_rule_header(rule):
    """Write the Rule header

    The short description is only written if it's not a DefaultRule
    """
    if isinstance(rule, DefaultRule):
        return

    rule_heading = "{rule_keyword}: {short_description}".format(
        rule_keyword=cf.bold_white(rule.keyword),
        short_description=cf.white(rule.short_description),
    )

    print(INDENT_STEP + rule_heading + "\n", flush=True)


def write_scenario_header(scenario):
    """Write the Scenario header"""
    indentation_level = 1 if isinstance(scenario.rule, DefaultRule) else 2
    indentation = INDENT_STEP * indentation_level

    scenario_heading = "{scenario_keyword}: {short_description}".format(
        scenario_keyword=cf.bold_white(scenario.keyword),
        short_description=cf.white(scenario.short_description),
    )

    for tag in scenario.tags:
        write_tagline(tag, indentation)
    print(indentation + scenario_heading, flush=True)


def write_scenario_footer(scenario):
    """Write the Scenario footer"""
    print(flush=True)


def write_step_running(step):
    """Write the Step before it's running"""
    if not world.config.no_step_rewrites:
        write_step(step, cf.orange)


def get_color_func_for_state(state):
    if state == State.PASSED:
        return cf.forestGreen
    elif state == State.FAILED:
        return cf.firebrick
    elif state == State.PENDING:
        return cf.orange
    else:
        return cf.deepSkyBlue3


def write_step_result(step):
    """Write the Step after it's ran"""
    step_color_func = get_color_func_for_state(step.state)

    if not world.config.no_ansi and not world.config.no_step_rewrites:
        # calculate how many line-ups are needed to rewrite the entire Step
        step_doc_string_lines = (
            step.doc_string.count("\n") + 2 if step.doc_string else 0
        )
        step_data_table_lines = len(step.data_table) if step.data_table else 0
        line_jumps = 1 + step_doc_string_lines + step_data_table_lines
        print(LINE_UP_JUMP * line_jumps, end="", flush=True)

    write_step(step, step_color_func)

    if step.failure_report:
        indentation_level = 2 if isinstance(step.rule, DefaultRule) else 3
        indentation = INDENT_STEP * indentation_level
        failure_report_indentation = indentation + INDENT_STEP
        report = step.failure_report

        if world.config.with_traceback:
            failure_information = report.traceback
        else:
            failure_information = "{}: {}\n".format(report.name, report.reason)

        print(
            step_color_func(
                textwrap.indent(failure_information, failure_report_indentation)
            ),
            end="",
            flush=True,
        )


def write_summary(features):
    """Write the end report after all Feature Files are ran"""
    feature_states = [f.state for f in features]
    features_line = "{} Feature{} ({})".format(
        len(feature_states),
        "s" if len(feature_states) != 1 else "",
        ", ".join(
            str(get_color_func_for_state(k)("{} {}".format(v, k.name.lower())))
            for k, v in Counter(feature_states).items()
        ),
    )

    scenarios = []
    rules_scenarios = (rule.scenarios for feature in features for rule in feature.rules)
    for scenario in itertools.chain(*rules_scenarios):
        if hasattr(scenario, "examples"):
            scenarios.extend(scenario.examples)
        else:
            scenarios.append(scenario)

    scenarios_line = "{} Scenario{} ({})".format(
        len(scenarios),
        "s" if len(scenarios) != 1 else "",
        ", ".join(
            str(get_color_func_for_state(k)("{} {}".format(v, k.name.lower())))
            for k, v in Counter(s.state for s in scenarios).items()
        ),
    )

    steps = [s for s in scenarios for s in s.steps]
    steps_line = "{} Step{} ({})".format(
        len(steps),
        "s" if len(steps) != 1 else "",
        ", ".join(
            str(get_color_func_for_state(k)("{} {}".format(v, k.name.lower())))
            for k, v in Counter(s.state for s in steps).items()
        ),
    )

    print(features_line, flush=True)
    print(scenarios_line, flush=True)
    print(steps_line, flush=True)

    # remind about pending Steps
    pending_steps = [s for s in steps if s.state is State.PENDING]
    if pending_steps:
        pending_step_implementations = {s.step_impl for s in pending_steps}
        print(
            cf.orange(
                "You have {} pending Step Implementation{} affecting {} Step{}:".format(
                    cf.bold_orange(len(pending_step_implementations)),
                    "s" if len(pending_step_implementations) != 1 else "",
                    cf.bold_orange(len(pending_steps)),
                    "s" if len(pending_steps) != 1 else "",
                )
            )
        )
        for pending_step_implementation in pending_step_implementations:
            print(
                cf.orange(
                    "*  '{} {}' @ {}:{}".format(
                        cf.bold_orange(pending_step_implementation.keyword),
                        cf.bold_orange(pending_step_implementation.pattern),
                        cf.bold_orange(
                            pending_step_implementation.func.__code__.co_filename
                        ),
                        cf.bold_orange(
                            pending_step_implementation.func.__code__.co_firstlineno
                        ),
                    )
                )
            )
        print(cf.orange("Note: This may be the reason for potentially failed Steps!"))

    total_duration = sum((f.duration() for f in features), timedelta())
    timing_information = cf.deepSkyBlue3(
        "Run {marker} finished within {duration} seconds".format(
            marker=cf.bold_deepSkyBlue3(world.config.marker),
            duration=cf.bold_deepSkyBlue3(total_duration.total_seconds()),
        )
    )

    print(timing_information, flush=True)


def write_step(step, step_color_func, indentation=None):
    """Write a Step with the given color function"""
    if indentation is None:
        indentation_level = 2 if isinstance(step.rule, DefaultRule) else 3
        indentation = INDENT_STEP * indentation_level

    step_text = "{step_keyword} {text}".format(
        step_keyword=step_color_func(step.used_keyword), text=step_color_func(step.text)
    )

    print(indentation + step_text, flush=True)

    if step.doc_string is not None:
        doc_string_indentation = indentation + INDENT_STEP
        print(doc_string_indentation + cf.white('"""'), flush=True)
        print(
            cf.deepSkyBlue3(textwrap.indent(step.doc_string, doc_string_indentation)),
            end="",
            flush=True,
        )
        print(cf.white(doc_string_indentation + '"""'), flush=True)

    if step.data_table is not None:
        data_table_indentation = indentation + INDENT_STEP
        pretty_table = pretty_print_table(step.data_table, cf.white, cf.deepSkyBlue3)
        print(textwrap.indent(pretty_table, data_table_indentation), flush=True)


def pretty_print_table(table, bar_color_func, value_color_func):
    """Pretty-print the given Table"""
    column_widths = [max(len(str(col)) for col in row) for row in zip(*table)]

    colored_bar = bar_color_func("|")
    pretty_table = []
    for row in table:
        pretty_row = "{0} {1} {0}".format(
            colored_bar,
            bar_color_func(" | ").join(
                value_color_func("{1: <{0}}").format(column_widths[col_idx], col_value)
                for col_idx, col_value in enumerate(row)
            ),
        )
        pretty_table.append(pretty_row)

    return "\n".join(pretty_table)
