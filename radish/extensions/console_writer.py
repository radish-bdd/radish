# -*- coding: utf-8 -*-

"""
    This radish extension provides the functionality to write the feature file run to the console.
"""

# disable no-member lint error because of dynamic method from colorful
# pylint: disable=no-member

import os
import re
import colorful

from radish.terrain import world
from radish.hookregistry import before, after
from radish.feature import Feature
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.stepmodel import Step
from radish.extensionregistry import extension
from radish.utils import console_write as write


@extension
class ConsoleWriter(object):
    """
        Console writer radish extension
    """
    OPTIONS = [
        ("--no-ansi", "print features without any ANSI sequences (like colors, line jump)"),
        ("--no-line-jump", "print features without line jumps (overwriting steps)"),
        ("--write-steps-once", "does not rewrite the steps (this option only makes sense in combination with the --no-ansi flag)"),
        ("--write-ids", "write the feature, scenario and step id before the sentences")
    ]
    LOAD_IF = staticmethod(lambda config: True)
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

        self._placeholder_regex = re.compile(r'(<[\w-]+>)', flags=re.UNICODE)

    def get_color_func(self, state):
        """
            Returns the color func to use
        """
        if state == Step.State.PASSED:
            return colorful.bold_green
        elif state == Step.State.FAILED:
            return colorful.bold_red
        elif state == Step.State.PENDING:
            return colorful.bold_yellow
        elif state:
            return colorful.cyan

    def get_line_jump_seq(self):
        """
            Returns the line jump ANSI sequence
        """
        line_jump_seq = ""
        if not world.config.no_ansi and not world.config.no_line_jump and not world.config.write_steps_once:
            line_jump_seq = "\r\033[A\033[K"
        return line_jump_seq

    def get_id_sentence_prefix(self, model, color_func, max_rows=None):
        """
            Returns the id from a model as sentence prefix

            :param Model model: a model with an id property
            :param function color_func: a function which gives coloring
            :param int max_rows: the maximum rows. Used for padding
        """
        padding = len("{0}. ".format(max_rows)) if max_rows else 0
        return color_func("{1: >{0}}. ".format(padding, model.id)) if world.config.write_ids else ""

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
            output += colorful.cyan(u"@{0}{1}\n".format(tag.name, "({0})".format(tag.arg) if tag.arg else ""))

        leading = "\n    " if feature.description else ""

        output += u"{0}{1}: {2}  # {3}{4}{5}".format(
            self.get_id_sentence_prefix(feature, colorful.bold_cyan),
            colorful.bold_white(feature.keyword),
            colorful.bold_white(feature.sentence),
            colorful.bold_black(feature.path),
            leading,
            colorful.white("\n    ".join(feature.description))
        )

        if feature.background:
            output += u"\n\n    {0}: {1}".format(
                colorful.bold_white(feature.background.keyword),
                colorful.bold_white(feature.background.sentence)
            )
            for step in feature.background.all_steps:
                output += '\n' + self._get_step_before_output(step, colorful.cyan)

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

            id_prefix = self.get_id_sentence_prefix(scenario, colorful.bold_yellow, len(scenario.parent.scenarios))
            colored_pipe = colorful.bold_white("|")
            output = u"        {0}{1} {2} {1}".format(
                id_prefix,
                colored_pipe,
                (u" {0} ").format(colored_pipe).join(
                    str(colorful.bold_yellow(u"{1: <{0}}".format(scenario.parent.get_column_width(i), x))) for i, x in enumerate(scenario.example.data)
                )
            )
        elif isinstance(scenario.parent, ScenarioLoop):
            if world.config.write_steps_once:
                return

            id_prefix = self.get_id_sentence_prefix(scenario, colorful.bold_yellow, len(scenario.parent.scenarios))
            colored_pipe = colorful.bold_white("|")
            output = u"        {0}{1} {2: <18} {1}".format(id_prefix, colored_pipe, str(colorful.bold_yellow(scenario.iteration)))
        else:
            id_prefix = self.get_id_sentence_prefix(scenario, colorful.bold_cyan)
            for tag in scenario.tags:
                if tag.name == "precondition" and world.config.expand and world.config.show:  # exceptional for show command when scenario steps expand and tag is a precondition -> comment it out
                    output += colorful.white(u"    # @{0}{1}\n".format(tag.name, "({0})".format(tag.arg) if tag.arg else ""))
                else:
                    output += colorful.cyan(u"    @{0}{1}\n".format(tag.name, u"({0})".format(tag.arg) if tag.arg else ""))
            output += u"    {0}{1}: {2}".format(id_prefix, colorful.bold_white(scenario.keyword), colorful.bold_white(scenario.sentence))
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
                output += colorful.italic_white(u"      As Background Precondition from {0}: {1}\n".format(os.path.basename(step.as_precondition.path), step.as_precondition.sentence))
            else:
                output += colorful.italic_white(u"      As Precondition from {0}: {1}\n".format(os.path.basename(step.as_precondition.path), step.as_precondition.sentence))
        elif step.as_background and self.last_background != step.as_background:
            output += colorful.italic_white(u"      From Background: {0}\n".format(step.as_background.sentence))
        elif step.as_precondition and self.last_precondition and not step.as_background and self.last_background:
            output += colorful.italic_white(u"      From Precondition Scenario: {0}: {1}\n".format(os.path.basename(step.as_precondition.path), step.as_precondition.sentence))
        elif (not step.as_precondition and self.last_precondition) or (not step.as_background and self.last_background):
            output += colorful.italic_white(u"      From Scenario\n")

        self.last_precondition = step.as_precondition
        self.last_background = step.as_background
        output += self._get_step_before_output(step)

        write(output)

    def _get_step_before_output(self, step, color_func=None):
        if color_func is None:
            color_func = colorful.bold_yellow
        output = u"\r        {0}{1}".format(self.get_id_sentence_prefix(step, color_func), color_func(step.sentence))

        if step.text:
            id_padding = self.get_id_padding(len(step.parent.steps))
            output += colorful.bold_white(u'\n            {0}"""'.format(id_padding))
            output += colorful.cyan(u"".join(["\n                {0}{1}".format(id_padding, l) for l in step.raw_text]))
            output += colorful.bold_white(u'\n            {0}"""'.format(id_padding))

        if step.table:
            colored_pipe = colorful.bold_white("|")
            col_widths = self.get_table_col_widths(step.table)
            for row in step.table:
                output += u"\n          {0} {1} {0}".format(colored_pipe, (" {0} ").format(colored_pipe).join(
                    str(color_func(u"{1: <{0}}".format(col_widths[i], x))) for i, x in enumerate(row)
                ))

        return output


    def console_writer_after_each_step(self, step):
        """
            Writes the step to the console after it was run

            :param Step step: the step to write to the console
        """
        if not isinstance(step.parent.parent, Feature):
            return

        color_func = self.get_color_func(step.state)
        line_jump_seq = self.get_line_jump_seq() * (((len(step.raw_text) + 3) if step.text else 1) + (len(step.table) if step.table else 0))
        output = u'{0}        '.format(line_jump_seq)

        if isinstance(step.parent, ScenarioOutline):
            # Highlight ScenarioOutline placeholders e.g. '<method>'
            output += (u''.join(str(colorful.white(item) if (self._placeholder_regex.search(item)
                                and item.strip('<>') in step.parent.examples_header)
                                else color_func(item))
                                for item in self._placeholder_regex.split(step.sentence)))
        else:
            output += u"{0}{1}".format(self.get_id_sentence_prefix(step, colorful.bold_cyan), color_func(step.sentence))

        if step.text:
            id_padding = self.get_id_padding(len(step.parent.steps))
            output += colorful.bold_white(u'\n            {0}"""'.format(id_padding))
            output += colorful.cyan(u"".join(["\n                {0}{1}".format(id_padding, l) for l in step.raw_text]))
            output += colorful.bold_white(u'\n            {0}"""'.format(id_padding))

        if step.table:
            colored_pipe = colorful.bold_white("|")
            col_widths = self.get_table_col_widths(step.table)
            for row in step.table:
                output += u"\n          {0} {1} {0}".format(colored_pipe, (" {0} ").format(colored_pipe).join(
                    str(color_func(u"{1: <{0}}".format(col_widths[i], x))) for i, x in enumerate(row)
                ))

        if step.state == step.State.FAILED:
            if world.config.with_traceback:
                output += u"\n          {0}{1}".format(self.get_id_padding(len(step.parent.steps) - 2), "\n          ".join([str(colorful.red(l)) for l in step.failure.traceback.split("\n")[:-2]]))
            output += u"\n          {0}{1}: {2}".format(self.get_id_padding(len(step.parent.steps) - 2), colorful.bold_red(step.failure.name), colorful.red(step.failure.reason))

        write(output)

    def console_writer_after_each_scenario(self, scenario):
        """
            If the scenario is a ExampleScenario it will write the Examples header

            :param Scenario scenario: the scenario which was ran.
        """
        output = ""
        if isinstance(scenario, ScenarioOutline):
            output += u"\n    {0}:\n".format(colorful.bold_white(scenario.example_keyword))
            output += colorful.bold_white(u"        {0}| {1} |".format(
                self.get_id_padding(len(scenario.scenarios), offset=2),
                u" | ".join("{1: <{0}}".format(scenario.get_column_width(i), x) for i, x in enumerate(scenario.examples_header))
            ))
        elif isinstance(scenario, ScenarioLoop):
            output += u"\n    {0}: {1}".format(colorful.bold_white(scenario.iterations_keyword), colorful.cyan(scenario.iterations))
        elif isinstance(scenario.parent, ScenarioOutline):
            colored_pipe = colorful.bold_white("|")
            color_func = self.get_color_func(scenario.state)
            output += u"{0}        {1}{2} {3} {2}".format(
                self.get_line_jump_seq(),
                self.get_id_sentence_prefix(scenario, colorful.bold_cyan, len(scenario.parent.scenarios)),
                colored_pipe,
                (u" {0} ").format(colored_pipe).join(
                    str(color_func(u"{1: <{0}}".format(scenario.parent.get_column_width(i), x))) for i, x in enumerate(scenario.example.data)
                )
            )

            if scenario.state == Step.State.FAILED:
                failed_step = scenario.failed_step
                if world.config.with_traceback:
                    output += u"\n          {0}{1}".format(self.get_id_padding(len(scenario.parent.scenarios)), "\n          ".join([str(colorful.red(l)) for l in failed_step.failure.traceback.split("\n")[:-2]]))
                output += u"\n          {0}{1}: {2}".format(self.get_id_padding(len(scenario.parent.scenarios)), colorful.bold_red(failed_step.failure.name), colorful.red(failed_step.failure.reason))
        elif isinstance(scenario.parent, ScenarioLoop):
            colored_pipe = colorful.bold_white("|")
            color_func = self.get_color_func(scenario.state)
            output += u"{0}        {1}{2} {3: <18} {2}".format(self.get_line_jump_seq(), self.get_id_sentence_prefix(scenario, colorful.bold_cyan, len(scenario.parent.scenarios)), colored_pipe, str(color_func(scenario.iteration)))

            if scenario.state == Step.State.FAILED:
                failed_step = scenario.failed_step
                if world.config.with_traceback:
                    output += u"\n          {0}{1}".format(self.get_id_padding(len(scenario.parent.scenarios)), "\n          ".join([str(colorful.red(l)) for l in failed_step.failure.traceback.split("\n")[:-2]]))
                output += u"\n          {0}{1}: {2}".format(self.get_id_padding(len(scenario.parent.scenarios)), colorful.bold_red(failed_step.failure.name), colorful.red(failed_step.failure.reason))

        if output:
            write(output)

    def console_writer_after_each_feature(self, feature):  # pylint: disable=unused-argument
        """
            Writes a newline after each feature

            :param Feature feature: the feature which was ran.
        """
        write("")
