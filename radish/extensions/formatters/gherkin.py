# -*- coding: utf-8 -*-

"""
This radish extension provides the functionality to write the feature file run to the console.
"""

# disable no-member lint error because of dynamic method from colorful
# pylint: disable=no-member

import os
import re

from radish.terrain import world
from radish.hookregistry import before, after
from radish.feature import Feature
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.stepmodel import Step
from radish.extensionregistry import extension
from radish.utils import console_write as write, styled_text


@extension
class ConsoleWriter(object):
    """
    Console writer radish extension
    """

    OPTIONS = [
        (
            "--no-ansi",
            "print features without any ANSI sequences (like colors, line jump)",
        ),
        ("--no-line-jump", "print features without line jumps (overwriting steps)"),
        (
            "--write-steps-once",
            "does not rewrite the steps (this option only makes sense in combination with the --no-ansi flag)",
        ),
        ("--write-ids", "write the feature, scenario and step id before the sentences"),
    ]
    LOAD_IF = staticmethod(lambda config: config.formatter == "gherkin")
    LOAD_PRIORITY = 30

    def __init__(self):
        before.each_feature(self.console_writer_before_each_feature)
        before.each_scenario(self.console_writer_before_each_scenario)
        before.each_step(self.console_writer_before_each_step)
        after.each_feature(self.console_writer_after_each_feature)
        after.each_scenario(self.console_writer_after_each_scenario)
        after.each_step(self.console_writer_after_each_step)

        self.last_precondition = None
        self.last_background = None

        self._placeholder_regex = re.compile(r"(<[\w-]+>)", flags=re.UNICODE)

    def get_color_func(self, state):
        """
        Returns the color func to use
        """
        if state == Step.State.PASSED:
            return lambda x: styled_text(x, "bold green")
        elif state == Step.State.FAILED:
            return lambda x: styled_text(x, "bold red")
        elif state == Step.State.PENDING:
            return lambda x: styled_text(x, "bold yellow")
        elif state:
            return lambda x: styled_text(x, "cyan")
        
    def get_line_jump_seq(self):
        """
        Returns the line jump ANSI sequence
        """
        line_jump_seq = ""
        if not world.config.no_ansi and not world.config.no_line_jump and not world.config.write_steps_once:
            line_jump_seq = "\r\033[A\033[K"
        return line_jump_seq

    def get_id_sentence_prefix(self, model, style, max_rows=None):
        """
        Returns the id from a model as sentence prefix

        :param Model model: a model with an id property
        :param function style: a function which gives coloring
        :param int max_rows: the maximum rows. Used for padding
        """
        padding = len("{0}. ".format(max_rows)) if max_rows else 0
        return styled_text("{1: >{0}}. ".format(padding, model.id), style) if world.config.write_ids else ""

    def get_id_padding(self, max_rows, offset=0):
        """
        Returns the id padding
        """
        if not world.config.write_ids:
            return ""

        return " " * (len(str(max_rows)) + 2 + offset)

    def get_table_col_widths(self, table):
        """
        Returns the width for every column of a table (lists in list)
        """
        return [max(len(str(col)) for col in row) for row in zip(*table)]  # pylint: disable=star-args

    def console_writer_before_each_feature(self, feature):
        """
        Writes feature header to the console

        :param Feature feature: the feature to write to the console
        """
        output = ""
        for tag in feature.tags:
            output += styled_text("@{0}{1}\n".format(tag.name, "({0})".format(tag.arg) if tag.arg else ""), "cyan")

        leading = "\n    " if feature.description else ""

        output += "{0}{1}: {2}  # {3}{4}{5}".format(
            self.get_id_sentence_prefix(feature, "bold cyan"),
            styled_text(feature.keyword, "bold white"),
            styled_text(feature.sentence, "bold white"),
            styled_text(feature.path, "bold black"),
            leading,
            styled_text("\n    ".join(feature.description), "white"),
        )

        if feature.background:
            output += "\n\n    {0}: {1}".format(
                styled_text(feature.background.keyword, "bold white"),
                styled_text(feature.background.sentence, "bold white"),
            )
            for step in feature.background.all_steps:
                output += "\n" + self._get_step_before_output(step, "cyan")

        write(output)

    def console_writer_before_each_scenario(self, scenario):
        """
        Writes the scenario header to the console

        :param Scenario scenario: the scenario to write to the console
        """
        output = "\n"
        if isinstance(scenario.parent, ScenarioOutline):
            if world.config.write_steps_once:
                return

            id_prefix = self.get_id_sentence_prefix(scenario, "bold yellow", len(scenario.parent.scenarios))
            colored_pipe = styled_text("|", "bold white")
            output = "        {0}{1} {2} {1}".format(
                id_prefix,
                colored_pipe,
                (" {0} ")
                .format(colored_pipe)
                .join(
                    str(styled_text("{1: <{0}}".format(scenario.parent.get_column_width(i), x), "bold yellow"))
                    for i, x in enumerate(scenario.example.data)
                ),
            )
        elif isinstance(scenario.parent, ScenarioLoop):
            if world.config.write_steps_once:
                return

            id_prefix = self.get_id_sentence_prefix(scenario, "bold yellow", len(scenario.parent.scenarios))
            colored_pipe = styled_text("|", "bold white")
            output = "        {0}{1} {2: <18} {1}".format(
                id_prefix, colored_pipe, styled_text(str(scenario.iteration), "bold yellow")
            )
        else:
            id_prefix = self.get_id_sentence_prefix(scenario, "bold cyan")
            for tag in scenario.tags:
                if (
                    tag.name == "precondition" and world.config.expand and world.config.show
                ):  # exceptional for show command when scenario steps expand and tag is a precondition -> comment it out
                    output += styled_text(
                        "    # @{0}{1}\n".format(tag.name, "({0})".format(tag.arg) if tag.arg else ""),
                        "white"
                    )
                else:
                    output += styled_text(
                        "    @{0}{1}\n".format(tag.name, "({0})".format(tag.arg) if tag.arg else ""),
                        "cyan"
                    )
            output += "    {0}{1}: {2}".format(
                id_prefix,
                styled_text(scenario.keyword, "bold white"),
                styled_text(scenario.sentence, "bold white"),
            )
        write(output)

    def console_writer_before_each_step(self, step):
        """
        Writes the step to the console before it is run

        :param Step step: the step to write to the console
        """
        if not isinstance(step.parent.parent, Feature):
            return

        if world.config.write_steps_once:
            return

        output = ""
        if step.as_precondition and self.last_precondition != step.as_precondition:
            if step.as_background:
                output += styled_text(
                    "      As Background Precondition from {0}: {1}\n".format(
                        os.path.basename(step.as_precondition.path),
                        step.as_precondition.sentence,
                    ), 
                    "italic white"
                )
            else:
                output += styled_text(
                    "      As Precondition from {0}: {1}\n".format(
                        os.path.basename(step.as_precondition.path),
                        step.as_precondition.sentence,
                    ),
                    "italic white"
                )
        elif step.as_background and self.last_background != step.as_background:
            output += styled_text("      From Background: {0}\n".format(step.as_background.sentence), "italic white")
        elif step.as_precondition and self.last_precondition and not step.as_background and self.last_background:
            output += styled_text(
                "      From Precondition Scenario: {0}: {1}\n".format(
                    os.path.basename(step.as_precondition.path),
                    step.as_precondition.sentence,
                ), 
                "italic white"
            )
        elif (not step.as_precondition and self.last_precondition) or (not step.as_background and self.last_background):
            output += styled_text("      From Scenario\n", "italic white")

        self.last_precondition = step.as_precondition
        self.last_background = step.as_background
        output += self._get_step_before_output(step)

        write(output)

    def _get_step_before_output(self, step, style=None):
        if style is None:
            #todo make this color func again after migration
            style = "bold yellow"
        output = "\r        {0}{1}".format(self.get_id_sentence_prefix(step, style), styled_text(step.sentence, style))

        if step.text:
            id_padding = self.get_id_padding(len(step.parent.steps))
            output += styled_text('\n            {0}"""'.format(id_padding), "bold white")
            output += styled_text("".join(["\n                {0}{1}".format(id_padding, l) for l in step.raw_text]), "cyan")
            output += styled_text('\n            {0}"""'.format(id_padding), "bold white")

        if step.table_header:
            colored_pipe = styled_text("|", "bold white")
            col_widths = self.get_table_col_widths([step.table_header] + step.table_data)

            # output table header
            output += "\n          {0} {1} {0}".format(
                colored_pipe,
                (" {0} ")
                .format(colored_pipe)
                .join(
                    str(styled_text("{1: <{0}}".format(col_widths[i], x)), "white") for i, x in enumerate(step.table_header)
                ),
            )

            # output table data
            for row in step.table_data:
                output += "\n          {0} {1} {0}".format(
                    colored_pipe,
                    (" {0} ")
                    .format(colored_pipe)
                    .join(str(styled_text("{1: <{0}}".format(col_widths[i], x), style)) for i, x in enumerate(row)),
                )

        return output

    def console_writer_after_each_step(self, step):
        """
        Writes the step to the console after it was run

        :param Step step: the step to write to the console
        """
        if not isinstance(step.parent.parent, Feature):
            return

        color_func = self.get_color_func(step.state)
        line_jump_seq = self.get_line_jump_seq() * (
            ((len(step.raw_text) + 3) if step.text else 1) + (len(step.table) + 1 if step.table_header else 0)
        )
        output = "{0}        ".format(line_jump_seq)

        if isinstance(step.parent, ScenarioOutline):
            # Highlight ScenarioOutline placeholders e.g. '<method>'
            output += "".join(
                str(
                    styled_text(item, "white")
                    if (self._placeholder_regex.search(item) and item.strip("<>") in step.parent.examples_header)
                    else color_func(item)
                )
                for item in self._placeholder_regex.split(step.sentence)
            )
        else:
            output += "{0}{1}".format(
                self.get_id_sentence_prefix(step, "bold cyan"),
                color_func(step.sentence),
            )

        if step.text:
            id_padding = self.get_id_padding(len(step.parent.steps))
            output += styled_text('\n            {0}"""'.format(id_padding), "bold white")
            output += styled_text("".join(["\n                {0}{1}".format(id_padding, l) for l in step.raw_text]), "cyan")
            output += styled_text('\n            {0}"""'.format(id_padding), "bold whitestyled_text")

        if step.table_header:
            colored_pipe = styled_text("|", "bold white")
            col_widths = self.get_table_col_widths([step.table_header] + step.table_data)

            # output table header
            output += "\n          {0} {1} {0}".format(
                colored_pipe,
                (" {0} ")
                .format(colored_pipe)
                .join(
                    str(styled_text("{1: <{0}}".format(col_widths[i], x), "white")) for i, x in enumerate(step.table_header)
                ),
            )

            # output table data
            for row in step.table_data:
                output += "\n          {0} {1} {0}".format(
                    colored_pipe,
                    (" {0} ")
                    .format(colored_pipe)
                    .join(str(color_func("{1: <{0}}".format(col_widths[i], x))) for i, x in enumerate(row)),
                )

        if step.state == step.State.FAILED:
            if world.config.with_traceback:
                output += "\n          {0}{1}".format(
                    self.get_id_padding(len(step.parent.steps) - 2),
                    "\n          ".join([str(styled_text(l, "red")) for l in step.failure.traceback.split("\n")[:-2]]),
                )
            output += "\n          {0}{1}: {2}".format(
                self.get_id_padding(len(step.parent.steps) - 2),
                styled_text(step.failure.name, "bold red"),
                styled_text(step.failure.reason, "red"),
            )

        write(output)

    def console_writer_after_each_scenario(self, scenario):
        """
        If the scenario is a ExampleScenario it will write the Examples header

        :param Scenario scenario: the scenario which was ran.
        """
        output = ""
        if isinstance(scenario, ScenarioOutline):
            output += "\n    {0}:\n".format(styled_text(scenario.example_keyword, "bold white"))
            output += styled_text(
                "        {0}| {1} |".format(
                    self.get_id_padding(len(scenario.scenarios), offset=2),
                    " | ".join(
                        "{1: <{0}}".format(scenario.get_column_width(i), x)
                        for i, x in enumerate(scenario.examples_header)
                    ),
                ), "bold white"
            )
        elif isinstance(scenario, ScenarioLoop):
            output += "\n    {0}: {1}".format(
                styled_text(scenario.iterations_keyword, "bold white"),
                styled_text(str(scenario.iterations), "cyan"),
            )
        elif isinstance(scenario.parent, ScenarioOutline):
            colored_pipe = styled_text("|", "bold white")
            color_func = self.get_color_func(scenario.state)
            output += "{0}        {1}{2} {3} {2}".format(
                self.get_line_jump_seq(),
                self.get_id_sentence_prefix(scenario, "bold cyan", len(scenario.parent.scenarios)),
                colored_pipe,
                (" {0} ")
                .format(colored_pipe)
                .join(
                    str(color_func("{1: <{0}}".format(scenario.parent.get_column_width(i), x)))
                    for i, x in enumerate(scenario.example.data)
                ),
            )

            if scenario.state == Step.State.FAILED:
                failed_step = scenario.failed_step
                if world.config.with_traceback:
                    output += "\n          {0}{1}".format(
                        self.get_id_padding(len(scenario.parent.scenarios)),
                        "\n          ".join(
                            [str(styled_text(l, "red")) for l in failed_step.failure.traceback.split("\n")[:-2]]
                        ),
                    )
                output += "\n          {0}{1}: {2}".format(
                    self.get_id_padding(len(scenario.parent.scenarios)),
                    styled_text(failed_step.failure.name, "bold red"),
                    styled_text(failed_step.failure.reason, "red"),
                )
        elif isinstance(scenario.parent, ScenarioLoop):
            colored_pipe = styled_text("|", "bold white")
            color_func = self.get_color_func(scenario.state)
            output += "{0}        {1}{2} {3: <18} {2}".format(
                self.get_line_jump_seq(),
                self.get_id_sentence_prefix(scenario, "bold cyan", len(scenario.parent.scenarios)),
                colored_pipe,
                color_func(str(scenario.iteration)),
            )

            if scenario.state == Step.State.FAILED:
                failed_step = scenario.failed_step
                if world.config.with_traceback:
                    output += "\n          {0}{1}".format(
                        self.get_id_padding(len(scenario.parent.scenarios)),
                        "\n          ".join(
                            [str(styled_text(l, "red")) for l in failed_step.failure.traceback.split("\n")[:-2]]
                        ),
                    )
                output += "\n          {0}{1}: {2}".format(
                    self.get_id_padding(len(scenario.parent.scenarios)),
                    styled_text(failed_step.failure.name, "bold red"),
                    styled_text(failed_step.failure.reason, "red"),
                )

        if output:
            write(output)

    def console_writer_after_each_feature(self, feature):  # pylint: disable=unused-argument
        """
        Writes a newline after each feature

        :param Feature feature: the feature which was ran.
        """
        write("")
