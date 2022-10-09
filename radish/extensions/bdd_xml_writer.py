# -*- coding: utf-8 -*-

"""
This module provides a hook which generates a BDD XML result file at the end of the run.
"""

from os import getlogin
from getpass import getuser
from socket import gethostname
from datetime import timedelta
import re

from radish.terrain import world
from radish.hookregistry import after
from radish.exceptions import RadishError
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.stepmodel import Step
from radish.extensionregistry import extension
from radish.exceptions import RadishError
import radish.utils as utils


@extension
class BDDXMLWriter(object):
    """
    BDD XML Writer radish extension
    """

    OPTIONS = [("--bdd-xml=<bddxml>", "write BDD XML result file after run")]
    LOAD_IF = staticmethod(lambda config: config.bdd_xml)
    LOAD_PRIORITY = 60

    def __init__(self):
        try:
            from lxml import etree
        except ImportError:
            raise RadishError(
                'if you want to use the BDD xml writer you have to "pip install radish-bdd[bdd-xml]"'
            )

        after.all(self.generate_bdd_xml)

    def _get_element_from_model(self, what, model):
        """
        Create a etree.Element from a given model
        """
        from lxml import etree

        # round duration to 10 decimal points, to avoid it being printed in
        # scientific notation
        duration = (
            "%.10f" % model.duration.total_seconds()
            if model.starttime and model.endtime
            else ""
        )
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

    def generate_bdd_xml(self, features, marker):
        """
            Generates the bdd xml
        """
        from lxml import etree

        if not features:
            raise RadishError("No features given to generate BDD xml file")

        duration = timedelta()
        for feature in features:
            if feature.state in [Step.State.PASSED, Step.State.FAILED]:
                duration += feature.duration

        try:
            user = getuser()
        except ModuleNotFoundError:
            # Note(FN):
            # File "Python\Python39\lib\getpass.py", line 168, in getuser
            # +     import pwd
            # + ModuleNotFoundError: No module named 'pwd'
            # Somehow getuser() fails on windows sometimes,
            # we fallback on getlogin which seems to work in these situations
            user = getlogin()

        testrun_element = etree.Element(
            "testrun",
            starttime=utils.format_utc_to_local_tz(features[0].starttime),
            endtime=utils.format_utc_to_local_tz(features[-1].endtime),
            duration=str(duration.total_seconds()),
            agent="{0}@{1}".format(user, gethostname()),
        )

        for feature in features:
            if not feature.has_to_run(world.config.scenarios):
                continue

            feature_element = self._get_element_from_model("feature", feature)

            description_element = etree.Element("description")
            description_element.text = etree.CDATA("\n".join(feature.description))

            tags_element = etree.Element("tags")

            for tag in feature.tags:
                tag_element = etree.Element("tag")
                tag_element.text = tag.name
                tags_element.append(tag_element)

            scenarios_element = etree.Element("scenarios")

            for scenario in (
                s
                for s in feature.all_scenarios
                if not isinstance(s, (ScenarioOutline, ScenarioLoop))
            ):
                if not scenario.has_to_run(world.config.scenarios):
                    continue
                scenario_element = self._get_element_from_model("scenario", scenario)

                scenario_tags_element = etree.Element("tags")
                scenario_element.append(scenario_tags_element)

                for tag in scenario.tags:
                    tag_element = etree.Element("tag")
                    tag_element.text = tag.name
                    if tag.arg:
                        tag_element.text += "({0})".format(tag.arg)
                    scenario_tags_element.append(tag_element)

                for step in scenario.all_steps:
                    step_element = self._get_element_from_model("step", step)
                    if step.state is Step.State.FAILED:
                        failure_element = etree.Element(
                            "failure",
                            type=step.failure.name,
                            message=step.failure.reason,
                        )
                        failure_element.text = etree.CDATA(
                            self._strip_ansi(step.failure.traceback)
                        )
                        step_element.append(failure_element)
                    scenario_element.append(step_element)
                scenarios_element.append(scenario_element)
            feature_element.append(description_element)
            feature_element.append(tags_element)
            feature_element.append(scenarios_element)
            testrun_element.append(feature_element)

        with open(world.config.bdd_xml, "w+") as f:
            content = etree.tostring(
                testrun_element,
                pretty_print=True,
                xml_declaration=True,
                encoding="utf-8",
            )
            try:
                if not isinstance(content, str):
                    content = content.decode("utf-8")
            except Exception:
                pass
            finally:
                f.write(content)
