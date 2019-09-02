"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import json
import functools

import click

from radish.errors import RadishError
from radish.extensionregistry import extension
from radish.hookregistry import after
from radish.models import ScenarioOutline, ScenarioLoop, State


@extension
class CucumberJSONWriter:
    """Cucumber JSON writer radish extension"""

    OPTIONS = [
        click.Option(
            param_decls=("--cucumber-json", "cucumber_json"),
            is_flag=True,
            help=("Report run results in a cucumber JSON file"),
        ),
        click.Option(
            param_decls=("--cucumber-json-file", "cucumber_json_file"),
            default="cucumber.json",
            help=("Specify the file path for the cucumber JSON report"),
        ),
    ]

    @classmethod
    def load(cls, config):
        if config.cucumber_json:
            return cls(
                config.cucumber_json_file, config.tag_expression, config.scenario_ids
            )
        else:
            return None

    def __init__(self, cucumber_json_file, tag_expression, scenario_ids):
        after.all(order=500)(
            functools.partial(
                generate_cucumber_json, cucumber_json_file, tag_expression, scenario_ids
            )
        )


def generate_cucumber_json(cucumber_json_file, tag_expression, scenario_ids, features):
    """Generate a cucumber JSON report for the run"""
    if not features:
        raise RadishError("No features given to generate cucumber json file")

    ccjson = []
    for feature in features:
        if not feature.has_to_run(tag_expression, scenario_ids):
            continue

        feature_description = "\n".join(feature.description)
        feature_tags = []
        for tag in feature.tags:
            feature_tags.append({"name": "@" + tag.name, "line": tag.line})

        feature_json = {
            "uri": str(feature.path),
            "type": "feature",
            "keyword": "Feature",
            "id": str(feature.id),
            "name": feature.short_description,
            "line": feature.line,
            "description": feature_description,
            "tags": feature_tags,
            "elements": [],
        }

        for rule in feature.rules:
            for scenario in rule.scenarios:
                if not scenario.has_to_run(tag_expression, scenario_ids):
                    continue

                if isinstance(scenario, ScenarioOutline):
                    scenario_type = "scenario_outline"
                elif isinstance(scenario, ScenarioLoop):
                    scenario_type = "scenario_loop"
                else:
                    scenario_type = "scenario"

                scenario_tags = []
                for tag in scenario.tags:
                    scenario_tags.append({"name": "@" + tag.name, "line": tag.line})
                scenario_json = {
                    "keyword": "Scenario",
                    "type": scenario_type,
                    "id": str(scenario.id),
                    "name": scenario.short_description,
                    "line": scenario.line,
                    "description": "",
                    "steps": [],
                    "tags": scenario_tags,
                }

                for step in scenario.steps:
                    step_json = {
                        "keyword": step.keyword,
                        "name": step.text,
                        "line": step.line,
                        "result": {
                            "status": step.state.name.lower(),
                            "duration": step.duration().total_seconds() * 1e9,
                        },
                    }
                    if step.state is State.FAILED:
                        step_json["result"][
                            "error_message"
                        ] = step.failure_report.reason
                    if step.state is State.UNTESTED:
                        if step.starttime is None:
                            step_json["result"]["status"] = State.PENDING.name.lower()
                        else:
                            step_json["result"]["status"] = State.SKIPPED.name.lower()
                    if step.embeddings:
                        step_json["embeddings"] = step.embeddings
                    scenario_json["steps"].append(step_json)
                feature_json["elements"].append(scenario_json)
        ccjson.append(feature_json)

    with open(cucumber_json_file, "w+") as f:
        content = json.dumps(ccjson, indent=4, sort_keys=True)
        f.write(content)
