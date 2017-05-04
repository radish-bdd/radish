# -*- coding: utf-8 -*-

"""
    This module provides a hook which generates a cucumber json result file at the end of the run.
"""

from getpass import getuser
from socket import gethostname
from datetime import timedelta
import re
import json
import logging

from radish.terrain import world
from radish.hookregistry import after
from radish.exceptions import RadishError
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.stepmodel import Step
from radish.extensionregistry import extension
import radish.utils as utils


@extension
class CucumberJSONWriter(object):
    """
        cucumber json Writer radish extension
    """
    OPTIONS = [("--cucumber-json=<ccjson>", "write cucumber json result file after run")]
    LOAD_IF = staticmethod(lambda config: config.cucumber_json)
    LOAD_PRIORITY = 60

    def __init__(self):
        after.all(self.generate_ccjson)

    def generate_ccjson(self, features, marker):
        """
            Generates the cucumber json
        """

        if not features:
            raise RadishError("No features given to generate cucumber json file")

        duration = timedelta()
        for feature in features:
            if feature.state in [Step.State.PASSED, Step.State.FAILED]:
                duration += feature.duration

        ccjson = []
        for feature in features:
            if not feature.has_to_run(world.config.scenarios):
                continue
            feature_description = "\n".join(feature.description)
            feature_json = {
                "uri": feature.path,
                "type": "feature",
                "keyword": feature.keyword,
                "id": str(feature.id),
                "name": feature.sentence,
                "line": feature.line,
                "description": feature_description,
                "tags": [],
                "elements": []
                }
            for i,j in enumerate(feature.tags):
                feature_json["tags"].append({"name": "@" + j.name, "line": feature.line - len(feature.tags) + i})
            for scenario in (s for s in feature.all_scenarios if not isinstance(s, (ScenarioOutline, ScenarioLoop))):
                if not scenario.has_to_run(world.config.scenarios):
                    continue
                scenario_json = {
                    "keyword": scenario.keyword,
                    "type": "scenario",
                    "id": str(scenario.id),
                    "name": scenario.sentence,
                    "line": scenario.line,
                    "description": "",
                    "steps": [],
                    "tags": []
                }
                start_line_no = scenario.line - len(scenario.tags)
                for i, tag in enumerate(scenario.tags):
                    scenario_json["tags"].append({"name": "@" + tag.name, "line": start_line_no + i})
                for step in scenario.all_steps:
                    duration = step.duration.total_seconds() * 1e9 if step.starttime and step.endtime else 0.0
                    step_json = {
                        "keyword": step.sentence.split()[0],
                        "name": step.sentence,
                        "line": step.line,
                        "result": {
                            "status": step.state,
                            "duration": duration
                        }
                    }
                    if step.state is Step.State.FAILED:
                        step_json["result"]["error_message"] = step.failure.reason
                    if step.state is Step.State.UNTESTED:
                        step_json["result"]["status"] = "skipped"
                    scenario_json["steps"].append(step_json)
                feature_json["elements"].append(scenario_json)
            ccjson.append(feature_json)

        with open(world.config.cucumber_json, "w+") as f:
            content = json.dumps(ccjson, indent=4, sort_keys=True)
            f.write(content)
