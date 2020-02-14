"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import re
import functools
from datetime import timedelta

# We need an OrderedDict because Python 3.5 does not preverse
# the order in dictionaries
from collections import OrderedDict

import click

from radish.errors import RadishError
from radish.extensionregistry import extension
from radish.hookregistry import after
from radish.models.state import State


@extension
class JUnitXMLWriter:
    """Extension to report a jUnit XML file for the radish run"""

    OPTIONS = [
        click.Option(
            param_decls=("--junit-xml", "junit_xml"),
            help="Path to the jUnit XML report",
        )
    ]

    @classmethod
    def load(cls, config):
        if config.junit_xml:
            return cls(config.junit_xml, config.tag_expression, config.scenario_ids)
        else:
            return None

    def __init__(self, junit_xml_path, tag_expression, scenario_ids):
        try:
            from lxml import etree  # noqa
        except ImportError:
            raise RadishError(
                "if you want to use the JUnit xml writer you have to "
                "'pip install lxml'"
            )

        after.all(order=500)(
            functools.partial(
                generate_junit_xml, junit_xml_path, tag_expression, scenario_ids
            )
        )


def generate_junit_xml(junit_xml_path, tag_expression, scenario_ids, features):
    from lxml import etree

    end_states = {State.PASSED, State.FAILED}
    total_duration = sum(
        (f.duration() for f in features if f.state in end_states), timedelta()
    )

    testsuites_element = etree.Element(
        "testsuites",
        OrderedDict(
            [
                ("name", "radish"),
                ("time", "{:.3f}".format(total_duration.total_seconds())),
            ]
        ),
    )

    for feature in (f for f in features if f.has_to_run(tag_expression, scenario_ids)):
        testsuite_states = {"failures": 0, "errors": 0, "skipped": 0, "tests": 0}

        for rule in feature.rules:
            # generate test suites stats
            for scenario in (
                s for s in rule.scenarios if s.has_to_run(tag_expression, scenario_ids)
            ):
                testsuite_states["tests"] += 1
                if scenario.state in [State.UNTESTED, State.PENDING, State.SKIPPED]:
                    testsuite_states["skipped"] += 1
                if scenario.state is State.FAILED:
                    testsuite_states["failures"] += 1

            testsuite_element = etree.Element(
                "testsuite",
                OrderedDict(
                    [
                        ("name", feature.short_description),
                        ("tests", str(testsuite_states["tests"])),
                        ("skipped", str(testsuite_states["skipped"])),
                        ("failures", str(testsuite_states["failures"])),
                        ("errors", str(testsuite_states["errors"])),
                        ("time", "{:.3f}".format(feature.duration().total_seconds())),
                    ]
                ),
            )

            for scenario in (
                s for s in rule.scenarios if s.has_to_run(tag_expression, scenario_ids)
            ):
                testcase_element = etree.Element(
                    "testcase",
                    OrderedDict(
                        [
                            ("classname", feature.short_description),
                            ("name", scenario.short_description),
                            (
                                "time",
                                "{:.3f}".format(scenario.duration().total_seconds()),
                            ),
                        ]
                    ),
                )

                if scenario.state in [State.UNTESTED, State.PENDING, State.SKIPPED]:
                    skipped_element = etree.Element("skipped")
                    testcase_element.append(skipped_element)

                if scenario.state is State.FAILED:
                    steps_text = []
                    steps = scenario.steps
                    if scenario.background:
                        steps = scenario.background.steps + steps

                    for step in steps:
                        step_line = "{} {}".format(step.keyword, step.text)
                        steps_text.append(step_line)
                        if step.state is State.FAILED:
                            failure_element = etree.Element(
                                "failure",
                                OrderedDict(
                                    [
                                        ("type", step.failure_report.name),
                                        ("message", step_line),
                                    ]
                                ),
                            )
                            failure_element.text = etree.CDATA(
                                "{}\n\n{}".format(
                                    "\n".join(steps_text),
                                    _strip_ansi(step.failure_report.traceback),
                                )
                            )
                            testcase_element.append(failure_element)
                testsuite_element.append(testcase_element)
            testsuites_element.append(testsuite_element)

    with open(junit_xml_path, "wb+") as f:
        content = etree.tostring(
            testsuites_element,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )
        f.write(content)


def _strip_ansi(text):
    pattern = re.compile(r"(\\033\[\d+(?:;\d+)*m)")
    return pattern.sub("", text)
