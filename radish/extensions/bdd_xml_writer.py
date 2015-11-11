# -*- coding: utf-8 -*-

"""
    This module provides a hook which generates a BDD XML result file at the end of the run.
"""

from getpass import getuser
from socket import gethostname
from lxml import etree
from datetime import timedelta
import re

from radish.terrain import world
from radish.hookregistry import after
from radish.exceptions import RadishError
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.step import Step
import radish.utils as utils


def _get_element_from_model(what, model):
    """
        Create a etree.Element from a given model
    """
    duration = str(model.duration.total_seconds()) if model.starttime and model.endtime else ""
    return etree.Element(
        what,
        sentence=model.sentence,
        id=str(model.id),
        result=model.state,
        starttime=utils.datetime_to_str(model.starttime),
        endtime=utils.datetime_to_str(model.endtime),
        duration=duration,
        testfile=model.path
    )


def _strip_ansi(text):
    """
        Strips ANSI modifiers from the given text
    """
    pattern = re.compile("(\\033\[\d+(?:;\d+)*m)")
    return pattern.sub("", text)


def generate_bdd_xml(features):
    """
        Generates the bdd xml
    """
    if not features:
        raise RadishError("No features given to generate BDD xml file")

    duration = timedelta()
    for feature in features:
        if feature.state in [Step.State.PASSED, Step.State.FAILED]:
            duration += feature.duration

    testrun_element = etree.Element(
        "testrun",
        starttime=utils.datetime_to_str(features[0].starttime),
        endtime=utils.datetime_to_str(features[-1].endtime),
        duration=str(duration.total_seconds()),
        agent="{0}@{1}".format(getuser(), gethostname())
    )

    for feature in features:
        if not feature.has_to_run(world.config.scenarios, world.config.feature_tags, world.config.scenario_tags):
            continue

        feature_element = _get_element_from_model("feature", feature)

        description_element = etree.Element("description")
        description_element.text = etree.CDATA("\n".join(feature.description))

        scenarios_element = etree.Element("scenarios")

        for scenario in (s for s in feature.all_scenarios if not isinstance(s, (ScenarioOutline, ScenarioLoop))):
            if not scenario.has_to_run(world.config.scenarios, world.config.feature_tags, world.config.scenario_tags):
                continue
            scenario_element = _get_element_from_model("scenario", scenario)

            for step in scenario.all_steps:
                step_element = _get_element_from_model("step", step)
                if step.state is Step.State.FAILED:
                    failure_element = etree.Element(
                        "failure",
                        type=step.failure.name,
                        message=step.failure.reason
                    )
                    failure_element.text = etree.CDATA(_strip_ansi(step.failure.traceback))
                    step_element.append(failure_element)
                scenario_element.append(step_element)
            scenarios_element.append(scenario_element)
        feature_element.append(description_element)
        feature_element.append(scenarios_element)
        testrun_element.append(feature_element)

    with open(world.config.bdd_xml, "w+") as f:
        content = etree.tostring(testrun_element, pretty_print=True, xml_declaration=True, encoding="utf-8")
        try:
            if not isinstance(content, str):
                content = content.decode("utf-8")
        except Exception:
            pass
        finally:
            f.write(content)


@after.all  # pylint: disable=no-member
def bdd_xml_writer_after_all(features, marker):  # pylint: disable=unused-argument
    """
        Generates a BDD XML file with the results
    """
    if not world.config.bdd_xml:
        return

    generate_bdd_xml(features)
