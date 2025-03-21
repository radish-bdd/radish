"""
This module provides a hook which generates a JUnit XML result file at the end of the run.
"""

import re
from datetime import timedelta

import radish.utils as utils
from radish.exceptions import RadishError
from radish.extensionregistry import extension
from radish.hookregistry import after
from radish.scenarioloop import ScenarioLoop
from radish.scenariooutline import ScenarioOutline
from radish.stepmodel import Step
from radish.terrain import world


@extension
class JUnitXMLWriter(object):
    """
    JUnit XML Writer radish extension
    """

    OPTIONS = [
        ("--junit-xml=<junitxml>", "write JUnit XML result file after run"),
        ("--junit-relaxed", "producing a non standard JUnit XML with added features like tags in testcases"),
    ]
    LOAD_IF = staticmethod(lambda config: config.junit_xml)
    LOAD_PRIORITY = 60

    def __init__(self):
        try:
            from lxml import etree
        except ImportError:
            raise RadishError('if you want to use the JUnit XML writer you have to "pip install radish-bdd lxml"')

        after.all(self.generate_junit_xml)

    def _get_element_from_model(self, what, model):
        """
        Create a etree.Element from a given model
        """
        from lxml import etree

        # round duration to 3 decimal points, to avoid it being printed in
        # scientific notation (According to the junit people 3 is enough)
        # https://issues.jenkins-ci.org/browse/JENKINS-52152
        duration = "%.3f" % model.duration.total_seconds() if model.starttime and model.endtime else ""
        return etree.Element(
            what,
            sentence=model.sentence,
            id=str(model.id),
            result=model.state,
            starttime=utils.format_utc_to_local_tz(model.starttime),
            endtime=utils.format_utc_to_local_tz(model.endtime),
            duration=duration,
            testfile=model.path,
        )

    def _strip_ansi(self, text):
        """
        Strips ANSI modifiers from the given text
        """
        pattern = re.compile(r"(\\033\[\d+(?:;\d+)*m)")
        return pattern.sub("", text)

    def _write_xml_to_disk(self, content):
        """
        Persist JUnit XML string to file
        """
        with open(world.config.junit_xml, "w+") as f:
            try:
                if not isinstance(content, str):
                    content = content.decode("utf-8")
            except Exception:
                pass
            finally:
                f.write(content)

    def generate_junit_xml(self, features, marker):
        """
        Generates the JUnit XML
        """
        from lxml import etree

        if not features:
            raise RadishError("No features given to generate JUnit XML file")

        duration = timedelta()
        for feature in features:
            if feature.state in [Step.State.PASSED, Step.State.FAILED]:
                duration += feature.duration

        testsuites_element = etree.Element("testsuites", time="%.3f" % duration.total_seconds())

        for feature in features:
            if not feature.has_to_run(world.config.scenarios):
                continue

            testsuite_states = {"failures": 0, "errors": 0, "skipped": 0, "tests": 0}

            for scenario in (s for s in feature.all_scenarios if not isinstance(s, (ScenarioOutline, ScenarioLoop))):
                if not scenario.has_to_run(world.config.scenarios):
                    continue

                testsuite_states["tests"] += 1
                if scenario.state in [
                    Step.State.UNTESTED,
                    Step.State.PENDING,
                    Step.State.SKIPPED,
                ]:
                    testsuite_states["skipped"] += 1
                if scenario.state is Step.State.FAILED:
                    testsuite_states["failures"] += 1

            testsuite_element = etree.Element(
                "testsuite",
                name=feature.sentence,
                failures=str(testsuite_states["failures"]),
                errors=str(testsuite_states["errors"]),
                skipped=str(testsuite_states["skipped"]),
                tests=str(testsuite_states["tests"]),
                time="%.3f" % feature.duration.total_seconds(),
            )

            for scenario in (s for s in feature.all_scenarios if not isinstance(s, (ScenarioOutline, ScenarioLoop))):
                if not scenario.has_to_run(world.config.scenarios):
                    continue

                if scenario.state not in [
                    Step.State.UNTESTED,
                    Step.State.PENDING,
                    Step.State.SKIPPED,
                ]:
                    testcase_element = etree.Element(
                        "testcase",
                        classname=feature.sentence,
                        name=scenario.sentence,
                        time="%.3f" % scenario.duration.total_seconds(),
                    )

                if world.config.junit_relaxed:
                    properties_element = etree.Element("properties")
                    for tag in scenario.all_tags:
                        value = str(tag.arg) if tag.arg else ""
                        property_element = etree.Element(
                            "property",
                            name=str(tag.name),
                            value=value,
                        )
                        properties_element.append(property_element)

                    testcase_element.append(properties_element)

                if scenario.state in [
                    Step.State.UNTESTED,
                    Step.State.PENDING,
                    Step.State.SKIPPED,
                ]:
                    skipped_element = etree.Element("skipped")
                    testcase_element.append(skipped_element)

                if scenario.state is Step.State.FAILED:
                    steps_sentence = []
                    for step in scenario.all_steps:
                        steps_sentence.append(step.sentence)
                        if step.state is Step.State.FAILED:
                            failure_element = etree.Element("failure", type=step.failure.name, message=step.sentence)
                            failure_element.text = etree.CDATA(
                                "%s\n\n%s"
                                % (
                                    "\n".join(steps_sentence),
                                    self._strip_ansi(step.failure.traceback),
                                )
                            )
                            testcase_element.append(failure_element)

                testsuite_element.append(testcase_element)

            testsuites_element.append(testsuite_element)

        content = etree.tostring(
            testsuites_element,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )
        self._write_xml_to_disk(content)
