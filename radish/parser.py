# -*- coding: utf-8 -*-

"""
Feature file parser.
One Feature file parser instance is able to parse one feature file.
"""

import os
import io
import re
import json
import filecmp
import copy
import string

from .compat import RecursionError
from .exceptions import RadishError, FeatureFileSyntaxError, LanguageNotSupportedError
from .feature import Feature
from .scenario import Scenario
from .scenariooutline import ScenarioOutline
from .scenarioloop import ScenarioLoop
from .stepmodel import Step
from .background import Background
from .model import Tag
from . import utils


class Keywords(object):
    """
    Represent config object for gherkin keywords.
    """

    def __init__(
        self,
        feature,
        background,
        scenario,
        scenario_outline,
        examples,
        scenario_loop,
        iterations,
    ):
        self.feature = feature
        self.background = background
        self.scenario = scenario
        self.scenario_outline = scenario_outline
        self.examples = examples
        self.scenario_loop = scenario_loop
        self.iterations = iterations


class FeatureParser(object):
    """
    Class to parse a feature file.
    A feature file contains just one feature.
    """

    LANGUAGE_LOCATION = os.path.join(os.path.dirname(__file__), "languages")
    DEFAULT_LANGUAGE = "en"
    CONTEXT_CLASSES = ["given", "when", "then", "but"]

    class State(object):
        """
        Represents the parser state
        """

        INIT = "init"
        FEATURE = "feature"
        BACKGROUND = "background"
        SCENARIO = "scenario"
        STEP = "step"
        EXAMPLES = "examples"
        EXAMPLES_ROW = "examples_row"
        STEP_TEXT = "step_text"
        SKIP_SCENARIO = "skip_scenario"

    def __init__(
        self,
        core,
        featurefile,
        featureid,
        tag_expr=None,
        inherited_tags=None,
        language="en",
    ):
        if not os.path.exists(featurefile):
            raise OSError("Feature file at '{0}' does not exist".format(featurefile))

        self._core = core
        self._featureid = featureid
        self._featurefile = featurefile
        self._tag_expr = tag_expr
        self.keywords = {}
        self._keywords_delimiter = ":"
        self._inherited_tags = inherited_tags or []

        self._current_state = FeatureParser.State.FEATURE
        self._current_line = 0
        self._current_tags = []
        self._current_preconditions = []
        self._current_constants = []
        self._current_scenario = None
        #: Holds the current context class for a Step.
        #  eg. If a step is: 'And I have the number'
        #  and this step was preceeded by 'Given I have the number
        #  it's context class is 'Given'. This is used to correctly
        #  match the 'And' sentences
        self._current_context_class = None
        # used to save text indention
        # - negative number indicates that there is now step text parsing
        self._in_step_text_index = -1
        self.feature = None

        self._load_language(language)

    def _load_language(self, language=None):
        """
        Loads all keywords of the given language

        :param string language: the lanugage to use for the feature files.
                                if None is given `radish` tries to detect the language.

        :returns: if the language could be loaded or not
        :rtype: bool

        :raises LanguageNotSupportedError: if the given language is not supported by radish
        """
        if not language:  # try to detect language
            raise NotImplementedError("Auto detect language is not implemented yet")

        language_path = os.path.join(self.LANGUAGE_LOCATION, language + ".json")
        try:
            with io.open(language_path, "r", encoding="utf-8") as f:
                language_pkg = json.load(f)
        except IOError:
            raise LanguageNotSupportedError(language)

        self.keywords = Keywords(**language_pkg["keywords"])

    def parse(self):
        """
        Parses the feature file of this `FeatureParser` instance

        :returns: if the parsing was successful or not
        :rtype: bool
        """
        with io.open(self._featurefile, "r", encoding="utf-8") as f:
            for line in f.readlines():
                self._current_line += 1
                line_strip = line.strip()
                if not line_strip:  # line is empty
                    continue

                if line_strip.startswith("#"):
                    # try to detect feature file language
                    language = self._detect_language(line)
                    if language:
                        self._load_language(language)

                    continue

                if self.feature:
                    if self._detect_feature(line_strip):
                        raise FeatureFileSyntaxError(
                            "radish supports only one Feature per feature file"
                        )

                    if self._detect_background(line_strip):
                        if self.feature.background:
                            raise FeatureFileSyntaxError(
                                "The Background block may only appear once in a Feature"
                            )

                        if self.feature.scenarios:
                            raise FeatureFileSyntaxError(
                                "The Background block must be placed before any Scenario block"
                            )

                result = self._parse_context(line)
                if result is False:
                    raise FeatureFileSyntaxError(
                        "Syntax error in feature file {0} on line {1}".format(
                            self._featurefile, self._current_line
                        )
                    )

        if not self.feature:
            raise FeatureFileSyntaxError(
                "No Feature found in file {0}".format(self._featurefile)
            )

        if not self.feature.scenarios:
            return None

        if (
            self._current_scenario and not self._current_scenario.complete
        ):  # for the last scenario
            self._current_scenario.after_parse()

        return self.feature

    def _parse_context(self, line):
        """
        Parses arbitrary context from a line

        :param string line: the line to parse from
        """
        parse_context_func = getattr(self, "_parse_" + self._current_state, None)
        if not parse_context_func:
            raise RadishError(
                "FeatureParser state {0} is not supported".format(self._current_state)
            )

        return parse_context_func(line)

    def _parse_feature(self, line):
        """
        Parses a Feature Sentence

        The `INIT` state is used as initiale state.

        :param string line: the line to parse from
        """
        line = line.strip()
        detected_feature = self._detect_feature(line)
        if not detected_feature:
            tag = self._detect_tag(line)
            if tag:
                self._current_tags.append(Tag(tag[0], tag[1]))
                if tag[0] == "constant":
                    name, value = self._parse_constant(tag[1])
                    self._current_constants.append((name, value))
                return True

            return False

        self.feature = Feature(
            self._featureid,
            self.keywords.feature,
            detected_feature,
            self._featurefile,
            self._current_line,
            self._current_tags,
        )
        self.feature.context.constants = self._current_constants
        self._current_state = FeatureParser.State.BACKGROUND
        self._current_tags = []
        self._current_constants = []
        return True

    def _parse_background(self, line):
        """
        Parses a background context

        :param str line: the line to parse the background
        """
        line = line.strip()
        detected_background = self._detect_background(line)
        if detected_background is None:
            # try to find a scenario
            if self._detect_scenario_type(line):
                return self._parse_scenario(line)

            # this line is interpreted as a feature description line
            self.feature.description.append(line)
            return True

        self.feature.background = Background(
            self.keywords.background,
            detected_background,
            self._featurefile,
            self._current_line,
            self.feature,
        )
        self._current_scenario = self.feature.background
        self._current_state = FeatureParser.State.STEP
        return True

    def _parse_scenario(self, line):
        """
        Parses a Feature context

        :param string line: the line to parse from
        """
        line = line.strip()
        detected_scenario = self._detect_scenario(line)
        scenario_type = Scenario
        keywords = (self.keywords.scenario,)
        if not detected_scenario:
            detected_scenario = self._detect_scenario_outline(line)
            scenario_type = ScenarioOutline
            keywords = (self.keywords.scenario_outline, self.keywords.examples)

            if not detected_scenario:
                detected_scenario = self._detect_scenario_loop(line)
                if not detected_scenario:
                    tag = self._detect_tag(line)
                    if tag:
                        self._current_tags.append(Tag(tag[0], tag[1]))
                        if tag[0] == "precondition":
                            scenario = self._parse_precondition(tag[1])
                            if scenario is not None:
                                self._current_preconditions.append(scenario)
                        elif tag[0] == "constant":
                            name, value = self._parse_constant(tag[1])
                            self._current_constants.append((name, value))
                        return True

                    raise FeatureFileSyntaxError(
                        "The parser expected a scenario or a tag on this line. Given: '{0}'".format(
                            line
                        )
                    )

                detected_scenario, iterations = (
                    detected_scenario
                )  # pylint: disable=unpacking-non-sequence
                scenario_type = ScenarioLoop
                keywords = (self.keywords.scenario_loop, self.keywords.iterations)

        if detected_scenario in self.feature:
            raise FeatureFileSyntaxError(
                "Scenario with name '{0}' defined twice in feature '{1}'".format(
                    detected_scenario, self.feature.path
                )
            )

        scenario_id = 1
        if self.feature.scenarios:
            previous_scenario = self._current_scenario
            if hasattr(previous_scenario, "scenarios") and previous_scenario.scenarios:
                scenario_id = previous_scenario.scenarios[-1].id + 1
            else:
                scenario_id = previous_scenario.id + 1

        # all tags of this scenario have been consumed so we can
        # check if this scenario has to be evaluated or not
        if self._tag_expr:
            # inherit the tags from the current feature and the explicitely
            # inherited tags given to the parser. This tags are coming from precondition scenarios
            current_tags = self._current_tags + self.feature.tags + self._inherited_tags
            scenario_in_tags = self._tag_expr.evaluate([t.name for t in current_tags])
            if (
                not scenario_in_tags
            ):  # this scenario does not match the given tag expression
                self._current_tags = []
                self._current_preconditions = []
                self._current_constants = []
                self._current_state = FeatureParser.State.SKIP_SCENARIO
                return True

        background = self._create_scenario_background(
            steps_runable=scenario_type is Scenario
        )
        scenario = scenario_type(
            scenario_id,
            *keywords,
            sentence=detected_scenario,
            path=self._featurefile,
            line=self._current_line,
            parent=self.feature,
            tags=self._current_tags,
            preconditions=self._current_preconditions,
            background=background
        )
        self.feature.scenarios.append(scenario)
        self._current_scenario = scenario
        self._current_scenario.context.constants = self._current_constants
        self._current_tags = []
        self._current_preconditions = []
        self._current_constants = []

        if scenario_type == ScenarioLoop:
            self._current_scenario.iterations = iterations
        self._current_state = FeatureParser.State.STEP
        return True

    def _parse_examples(self, line):
        """
        Parses the Examples header line

        :param string line: the line to parse from
        """
        line = line.strip()
        if not isinstance(self._current_scenario, ScenarioOutline):
            raise FeatureFileSyntaxError(
                "Scenario does not support Examples. Use 'Scenario Outline'"
            )

        self._current_scenario.examples_header = [
            x.strip() for x in line.split("|")[1:-1]
        ]
        self._current_state = FeatureParser.State.EXAMPLES_ROW
        return True

    def _parse_examples_row(self, line):
        """
        Parses an Examples row

        :param string line: the line to parse from
        """
        line = line.strip()
        # detect next keyword
        if self._detect_scenario_type(line):
            self._current_scenario.after_parse()
            return self._parse_scenario(line)

        example = ScenarioOutline.Example(
            [x.strip() for x in utils.split_unescape(line, "|")[1:-1]],
            self._featurefile,
            self._current_line,
        )
        self._current_scenario.examples.append(example)
        return True

    def _parse_step(self, line):
        """
        Parses a single step

        :param string line: the line to parse from
        """
        line_strip = line.strip()
        # detect next keyword
        if self._detect_scenario_type(line_strip):
            self._current_scenario.after_parse()
            return self._parse_scenario(line_strip)

        if self._detect_step_text(line_strip):
            self._current_state = self.State.STEP_TEXT
            return self._parse_step_text(line)

        if self._detect_table(line_strip):
            self._parse_table(line_strip)
            return True

        if self._detect_examples(line_strip):
            self._current_state = FeatureParser.State.EXAMPLES
            return True

        # get context class
        step_context_class = line_strip.split()[0].lower()
        if step_context_class in FeatureParser.CONTEXT_CLASSES:
            self._current_context_class = step_context_class

        step_id = len(self._current_scenario.all_steps) + 1
        not_runable = isinstance(
            self._current_scenario, (ScenarioOutline, ScenarioLoop, Background)
        )
        step = Step(
            step_id,
            line_strip,
            self._featurefile,
            self._current_line,
            self._current_scenario,
            not not_runable,
            context_class=self._current_context_class,
        )
        self._current_scenario.steps.append(step)
        return True

    def _parse_table(self, line):
        """
        Parses a step table row

        :param string line: the line to parse from
        """
        line = line.strip()
        if not self._current_scenario.steps:
            raise FeatureFileSyntaxError(
                "Found step table without previous step definition on line {0}".format(
                    self._current_line
                )
            )

        current_step = self._current_scenario.steps[-1]
        table_columns = [x.strip() for x in utils.split_unescape(line, "|")[1:-1]]
        if not current_step.table_header:  # it's the table heading
            current_step.table_header = table_columns
        else:  # it's a table data row
            table_data = {
                k: v for k, v in zip(current_step.table_header, table_columns)
            }
            current_step.table_data.append(table_columns)
            current_step.table.append(table_data)
        return True

    def _parse_step_text(self, line):
        """
        Parses additional step text

        :param str line: the line to parse
        """

        def dedent(_str):
            ret_line = ''
            for char_index in range(len(_str)):
                if not ret_line and char_index < self._in_step_text_index and _str[char_index] in string.whitespace:
                    continue
                else:
                    ret_line += _str[char_index]
            return ret_line.rstrip()

        line_strip = line.strip()
        if line_strip.startswith('"""') and self._in_step_text_index == -1:
            self._in_step_text_index = line.index('"')
            line_strip = line_strip[3:]
            if line_strip:
                self._current_scenario.steps[-1].raw_text.append(line_strip.rstrip())
        elif line_strip.endswith('"""') and self._in_step_text_index >= 0:
            self._current_state = self.State.STEP
            line = line.rstrip()[:-3]
            line_dedent = dedent(line)
            self._in_step_text_index = -1
            if line_dedent:
                self._current_scenario.steps[-1].raw_text.append(line_dedent)
        else:
            line_dedent = dedent(line)
            self._current_scenario.steps[-1].raw_text.append(line_dedent)
        return True

    def _parse_precondition(self, arguments):
        """
        Parses scenario preconditions

        The arguments must be in format:
            File.feature: Some scenario

        :param str arguments: the raw arguments
        """
        match = re.search(r"(.*?\.feature): (.*)", arguments)
        if not match:
            raise FeatureFileSyntaxError(
                "Scenario @precondition tag must have argument in format: 'test.feature: Some scenario'"
            )

        feature_file_name, scenario_sentence = match.groups()
        feature_file = os.path.join(
            os.path.dirname(self._featurefile), feature_file_name
        )

        # check if the precondition Scenario is in the same feature file.
        # If this happens to be the case the current feature is just copied as is.
        if filecmp.cmp(self._featurefile, feature_file):
            if scenario_sentence not in self.feature:
                raise FeatureFileSyntaxError(
                    "Cannot import precondition scenario '{0}' from feature '{1}': No such scenario".format(
                        scenario_sentence, feature_file
                    )
                )

            feature = copy.deepcopy(self.feature)
            self._core.features.append(feature)
        else:
            try:
                current_tags = (
                    self._current_tags + self.feature.tags + self._inherited_tags
                )
                feature = self._core.parse_feature(
                    feature_file, self._tag_expr, inherited_tags=current_tags
                )
            except (RuntimeError, RecursionError) as e:
                if str(e).startswith(
                    "maximum recursion depth exceeded"
                ):  # precondition cycling
                    raise FeatureFileSyntaxError(
                        "Your feature '{0}' has cycling preconditions with '{1}: {2}' starting at line {3}".format(
                            self._featurefile,
                            feature_file_name,
                            scenario_sentence,
                            self._current_line,
                        )
                    )
                raise

        if feature is None:
            return None

        if scenario_sentence not in feature:
            raise FeatureFileSyntaxError(
                "Cannot import precondition scenario '{0}' from feature '{1}': No such scenario".format(
                    scenario_sentence, feature_file
                )
            )

        return feature[scenario_sentence]

    def _parse_constant(self, arguments):
        """
        Parses tag arguments as a constant containing name and value

        The arguments must be in format:
            ConstantName: SomeValue
            ConstantName: 5

        :param str arguments: the raw arguments to parse
        """
        name, value = arguments.split(":", 1)
        return name.strip(), value.strip()

    def _parse_skip_scenario(self, line):
        """
        Parses the next lines until the next scenario is reached
        """
        line = line.strip()
        if self._detect_scenario_type(line):
            return self._parse_scenario(line)

        return True

    def _detect_keyword(self, keyword, line):
        """
        Detects a keyword on a given line

        :param keyword: the keyword to detect
        :param line: the line in which we want to detect the keyword

        :return: the line without the detected keyword
        :rtype: string or None
        """

        pattern = r"^{keyword}\s*{delimiter}(.*)$".format(
            keyword=keyword, delimiter=self._keywords_delimiter
        )
        match = re.match(pattern, line)

        if match:
            return match.group(1).strip()

        return None

    def _detect_feature(self, line):
        """
        Detects a feature on the given line

        :param string line: the line to detect a feature

        :returns: the detected feature on the given line
        :rtype: string or None
        """

        return self._detect_keyword(self.keywords.feature, line)

    def _detect_background(self, line):
        """
        Detects a background on the given line

        :param string line: the line to detect a background

        :returns: the detected background on the given line
        :rtype: string or None
        """

        return self._detect_keyword(self.keywords.background, line)

    def _detect_scenario_type(self, line):
        """
        Detect a Scenario/ScenarioOutline/ScenarioLoop/Tag on the given line.

        :returns: if a scenario of any type is present on the given line
        :rtype: bool
        """
        if (
            self._detect_scenario(line)
            or self._detect_scenario_outline(line)
            or self._detect_scenario_loop(line)
            or self._detect_tag(line)
        ):
            self._current_state = FeatureParser.State.SCENARIO
            return True

        return False

    def _detect_scenario(self, line):
        """
        Detects a scenario on the given line

        :param string line: the line to detect a scenario

        :returns: the scenario detected on the given line
        :rtype: string or None
        """

        return self._detect_keyword(self.keywords.scenario, line)

    def _detect_scenario_outline(self, line):
        """
        Detects a scenario outline on the given line

        :param string line: the line to detect a scenario outline

        :returns: the scenario outline detected on the given line
        :rtype: string or None
        """

        return self._detect_keyword(self.keywords.scenario_outline, line)

    def _detect_examples(self, line):
        """
        Detects an Examples block on the given line

        :param string line: the line to detect the Examples

        :returns: if an Examples block was found on the given line
        :rtype: bool
        """

        return self._detect_keyword(self.keywords.examples, line) is not None

    def _detect_scenario_loop(self, line):
        """
        Detects a scenario loop on the given line

        :param string line: the line to detect a scenario loop

        :returns: if a scenario loop was found on the given line
        :rtype: string
        """
        match = re.search(r"^{0} (\d+):(.*)".format(self.keywords.scenario_loop), line)
        if match:
            return match.group(2).strip(), int(match.group(1))

        return None

    def _detect_table(self, line):
        """
        Detects a step table row on the given line

        :param string line: the line to detect the table row

        :returns: if an step table row was found or not
        :rtype: bool
        """
        return line.startswith("|")

    def _detect_step_text(self, line):
        """
        Detects the beginning of an additional step text block

        :param str line: the line to detect the step text block

        :returns: if a step text block was found or not
        :rtype: bool
        """
        return line.startswith('"""')

    def _detect_language(self, line):
        """
        Detects a language on the given line

        :param string line: the line to detect the language

        :returns: the language or None
        :rtype: str or None
        """
        match = re.search("^# language: (.*)", line)
        if match:
            return match.group(1)

        return None

    def _detect_tag(self, line):
        """
        Detects a tag on the given line

        :param string line: the line to detect the tag

        :returns: the tag or None
        :rtype: str or None
        """
        match = re.search(r"^@([^\s(]+)(?:\((.*?)\))?", line)
        if match:
            return match.group(1), match.group(2)

        return None

    def _create_scenario_background(self, steps_runable):
        """
        Creates a new instance of the features current
        Background to assign to a new Scenario.
        """
        if not self.feature.background:
            return None

        return self.feature.background.create_instance(steps_runable=steps_runable)
