# -*- coding: utf-8 -*-

"""
This radish extension module provide the functionality to write the end report
"""


from datetime import timedelta

import humanize

from radish.hookregistry import after
from radish.stepmodel import Step
from radish.utils import console_write as write, make_unique_obj_list, get_func_code, styled_text
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.extensionregistry import extension
from radish.terrain import world
from radish.stepregistry import StepRegistry


@extension
class EndreportWriter(object):
    """
    Endreport writer radish extension
    """

    LOAD_IF = staticmethod(lambda config: not config.show)
    LOAD_PRIORITY = 50

    def __init__(self):
        after.all(self.console_write)

    def console_write(self, features, marker):
        """
        Writes the endreport for all features

        :param list features: all features
        """
        stats = {
            "features": {
                "amount": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "untested": 0,
                "pending": 0,
            },
            "scenarios": {
                "amount": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "untested": 0,
                "pending": 0,
            },
            "steps": {
                "amount": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "untested": 0,
                "pending": 0,
            },
        }
        pending_steps = []
        duration = timedelta()
        for feature in features:
            if not feature.has_to_run(world.config.scenarios):
                continue
            stats["features"]["amount"] += 1
            stats["features"][feature.state] += 1

            if feature.state in [Step.State.PASSED, Step.State.FAILED]:
                duration += feature.duration

            for scenario in feature.all_scenarios:
                if not scenario.has_to_run(world.config.scenarios):
                    continue

                if isinstance(scenario, ScenarioOutline):  # skip ScenarioOutlines
                    continue
                if isinstance(scenario, ScenarioLoop):  # skip ScenarioLoop
                    continue

                stats["scenarios"]["amount"] += 1
                stats["scenarios"][scenario.state] += 1
                for step in scenario.steps:
                    stats["steps"]["amount"] += 1
                    stats["steps"][step.state] += 1

                    if step.state == Step.State.PENDING:
                        pending_steps.append(step)

        colored_closing_paren = styled_text(")", "bold white")
        colored_comma = styled_text(", ", "bold white")
        passed_word = styled_text("{0} passed", "bold green")
        failed_word = styled_text("{0} failed", "bold red")
        skipped_word = styled_text("{0} skipped", "cyan")
        pending_word = styled_text("{0} pending", "bold yellow")

        output = styled_text("{0} features (".format(stats["features"]["amount"]), "bold white")
        output += passed_word.format(stats["features"]["passed"])
        if stats["features"]["failed"]:
            output += colored_comma + failed_word.format(stats["features"]["failed"])
        if stats["features"]["skipped"]:
            output += colored_comma + skipped_word.format(stats["features"]["skipped"])
        if stats["features"]["pending"]:
            output += colored_comma + pending_word.format(stats["features"]["pending"])
        output += colored_closing_paren

        output += "\n"
        output += styled_text("{} scenarios (".format(stats["scenarios"]["amount"]), "bold white")
        output += passed_word.format(stats["scenarios"]["passed"])
        if stats["scenarios"]["failed"]:
            output += colored_comma + failed_word.format(stats["scenarios"]["failed"])
        if stats["scenarios"]["skipped"]:
            output += colored_comma + skipped_word.format(stats["scenarios"]["skipped"])
        if stats["scenarios"]["pending"]:
            output += colored_comma + pending_word.format(stats["scenarios"]["pending"])
        output += colored_closing_paren

        output += "\n"
        output += styled_text("{} steps (".format(stats["steps"]["amount"]), "bold white")
        output += passed_word.format(stats["steps"]["passed"])
        if stats["steps"]["failed"]:
            output += colored_comma + failed_word.format(stats["steps"]["failed"])
        if stats["steps"]["skipped"]:
            output += colored_comma + skipped_word.format(stats["steps"]["skipped"])
        if stats["steps"]["pending"]:
            output += colored_comma + pending_word.format(stats["steps"]["pending"])
        output += colored_closing_paren

        if pending_steps:
            sr = StepRegistry()
            pending_step_implementations = make_unique_obj_list(pending_steps, lambda x: x.definition_func)
            output += styled_text(
                "\nYou have {0} pending step implementation{1} affecting {2} step{3}:\n  {4}\n\nNote: this could be the reason for some failing subsequent steps".format(
                    len(pending_step_implementations),
                    "s" if len(pending_step_implementations) != 1 else "",
                    len(pending_steps),
                    "s" if len(pending_steps) != 1 else "",
                    "\n  ".join(
                        [
                            "-  '{0}' @ {1}".format(
                                sr.get_pattern(s.definition_func),
                                get_func_code(s.definition_func).co_filename,
                            )
                            for s in pending_step_implementations
                        ]
                    ),
                ), 
                "white"
            )

        output += "\n"

        if world.config.wip:
            if stats["scenarios"]["passed"] > 0:
                output += styled_text(
                    "\nThe --wip switch was used, so I didn't expect anything to pass. These scenarios passed:\n",
                    "red"
                )

                has_passed_scenarios = False
                for feature in features:
                    passed_scenarios = list(
                        filter(
                            lambda s: s.state == Step.State.PASSED,
                            feature.all_scenarios,
                        )
                    )
                    for scenario in passed_scenarios:
                        output += styled_text("\n - {}: {}".format(feature.path, scenario.sentence), "red")
                        has_passed_scenarios = True

                if has_passed_scenarios:
                    output += "\n"
            else:
                output += styled_text("\nThe --wip switch was used, so the failures were expected. All is good.\n", "green")

        output += styled_text("Run {0} finished within {1}".format(marker, humanize.naturaldelta(duration)), "cyan")

        write(output)
