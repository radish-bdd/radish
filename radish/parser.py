# -*- coding: utf-8 -*-

"""
    Feature file parser.
    One Feature file parser instance is able to parse one feature file.
"""

import os
import codecs
import re
import json

from .exceptions import RadishError, FeatureFileSyntaxError, LanguageNotSupportedError
from .feature import Feature
from .scenario import Scenario
from .scenariooutline import ScenarioOutline
from .scenarioloop import ScenarioLoop
from .stepmodel import Step
from .model import Tag


class Keywords(object):
    """
        Represent config object for gherkin keywords.
    """
    def __init__(self, feature, scenario, scenario_outline, examples, scenario_loop, iterations):
        self.feature = feature
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

    class State(object):
        """
            Represents the parser state
        """
        INIT = "init"
        FEATURE = "feature"
        SCENARIO = "scenario"
        SCENARIO_OUTLINE = "scenario_outline"
        STEP = "step"
        EXAMPLES = "examples"
        EXAMPLES_ROW = "examples_row"
        SCENARIO_LOOP = "scenario_loop"
        STEP_TEXT = "step_text"
        SKIP_SCENARIO = "skip_scenario"

    def __init__(self, core, featurefile, featureid, feature_tag_expr=None, scenario_tag_expr=None, language="en"):
        if not os.path.exists(featurefile):
            raise OSError("Feature file at '{0}' does not exist".format(featurefile))

        self._core = core
        self._featureid = featureid
        self._featurefile = featurefile
        self._feature_tag_expr = feature_tag_expr
        self._scenario_tag_expr = scenario_tag_expr
        self.keywords = {}
        self._keywords_delimiter = ":"

        self._current_state = FeatureParser.State.FEATURE
        self._current_line = 0
        self._current_tags = []
        self._current_preconditions = []
        self._current_constants = []
        self._in_step_text = False
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
            with codecs.open(language_path, "rb", "utf-8") as f:
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
        with codecs.open(self._featurefile, "rb", "utf-8") as f:
            for line in f.readlines():
                self._current_line += 1
                line = line.strip()
                if not line:  # line is empty
                    continue

                if line.startswith("#"):
                    # try to detect feature file language
                    language = self._detect_language(line)
                    if language:
                        self._load_language(language)

                    continue

                if self.feature and self._detect_feature(line):
                    raise FeatureFileSyntaxError("radish supports only one Feature per feature file")

                result = self._parse_context(line)
                if result is False:
                    raise FeatureFileSyntaxError("Syntax error in feature file {0} on line {1}".format(self._featurefile, self._current_line))

                if result is None:  # feature did not match tag expression, thus do not continue to parse
                    return None

        if not self.feature:
            raise FeatureFileSyntaxError("No Feature found in file {0}".format(self._featurefile))

        if self.feature.scenarios:
            self.feature.scenarios[-1].after_parse()

        return self.feature

    def _parse_context(self, line):
        """
            Parses arbitrary context from a line

            :param string line: the line to parse from
        """
        parse_context_func = getattr(self, "_parse_" + self._current_state)
        if not parse_context_func:
            raise RadishError("FeatureParser state {0} is not support".format(self._current_state))

        return parse_context_func(line)

    def _parse_feature(self, line):
        """
            Parses a Feature Sentence

            The `INIT` state is used as initiale state.

            :param string line: the line to parse from
        """
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

        # all tags of this feature have been consumed so we can
        # check if this feature has to be evaluated or not.
        if self._feature_tag_expr:
            feature_in_tags = self._feature_tag_expr.evaluate([t.name for t in self._current_tags])
            if not feature_in_tags:  # this feature does not match the given tag expression.
                return None

        self.feature = Feature(self._featureid, self.keywords.feature, detected_feature, self._featurefile, self._current_line, self._current_tags)
        self.feature.context.constants = self._current_constants
        self._current_state = FeatureParser.State.SCENARIO
        self._current_tags = []
        self._current_constants = []
        return True

    def _parse_scenario(self, line):
        """
            Parses a Feature context

            :param string line: the line to parse from
        """
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
                            self._current_preconditions.append(scenario)
                        elif tag[0] == "constant":
                            name, value = self._parse_constant(tag[1])
                            self._current_constants.append((name, value))
                        return True

                    self.feature.description.append(line)
                    return True

                detected_scenario, iterations = detected_scenario  # pylint: disable=unpacking-non-sequence
                scenario_type = ScenarioLoop
                keywords = (self.keywords.scenario_loop, self.keywords.iterations)

        if detected_scenario in self.feature:
            raise FeatureFileSyntaxError("Scenario with name '{0}' defined twice in feature '{1}'".format(detected_scenario, self.feature.path))

        scenario_id = 1
        if self.feature.scenarios:
            previous_scenario = self.feature.scenarios[-1]
            if hasattr(previous_scenario, "scenarios") and previous_scenario.scenarios:
                scenario_id = previous_scenario.scenarios[-1].id + 1
            else:
                scenario_id = previous_scenario.id + 1

        # all tags of this scneario have been consumed so we can
        # check if this scenario has to be evaluated or not
        if self._scenario_tag_expr:
            scenario_in_tags = self._scenario_tag_expr.evaluate([t.name for t in self._current_tags])
            if not scenario_in_tags:  # this scenario does not match the given tag expression
                self._current_tags = []
                self._current_preconditions = []
                self._current_constants = []
                self._current_state = FeatureParser.State.SKIP_SCENARIO
                return True

        self.feature.scenarios.append(scenario_type(scenario_id, *keywords, sentence=detected_scenario, path=self._featurefile, line=self._current_line, parent=self.feature, tags=self._current_tags, preconditions=self._current_preconditions))
        self.feature.scenarios[-1].context.constants = self._current_constants
        self._current_tags = []
        self._current_preconditions = []
        self._current_constants = []

        if scenario_type == ScenarioLoop:
            self.feature.scenarios[-1].iterations = iterations
        self._current_state = FeatureParser.State.STEP
        return True

    def _parse_examples(self, line):
        """
            Parses the Examples header line

            :param string line: the line to parse from
        """
        if not isinstance(self.feature.scenarios[-1], ScenarioOutline):
            raise FeatureFileSyntaxError("Scenario does not support Examples. Use 'Scenario Outline'")

        self.feature.scenarios[-1].examples_header = [x.strip() for x in line.split("|")[1:-1]]
        self._current_state = FeatureParser.State.EXAMPLES_ROW
        return True

    def _parse_examples_row(self, line):
        """
            Parses an Examples row

            :param string line: the line to parse from
        """
        # detect next keyword
        if self._detect_scenario(line) or self._detect_scenario_outline(line) or self._detect_scenario_loop(line):
            self.feature.scenarios[-1].after_parse()
            return self._parse_scenario(line)

        example = ScenarioOutline.Example([x.strip() for x in line.split("|")[1:-1]], self._featurefile, self._current_line)
        self.feature.scenarios[-1].examples.append(example)
        return True

    def _parse_step(self, line):
        """
            Parses a single step

            :param string line: the line to parse from
        """
        # detect next keyword
        if self._detect_scenario(line) or self._detect_scenario_outline(line) or self._detect_scenario_loop(line) or self._detect_tag(line):
            self.feature.scenarios[-1].after_parse()
            return self._parse_scenario(line)

        if self._detect_step_text(line):
            self._current_state = self.State.STEP_TEXT
            return self._parse_step_text(line)

        if self._detect_table(line):
            self._parse_table(line)
            return True

        if self._detect_examples(line):
            self._current_state = FeatureParser.State.EXAMPLES
            return True

        step_id = len(self.feature.scenarios[-1].all_steps) + 1
        not_runable = isinstance(self.feature.scenarios[-1], (ScenarioOutline, ScenarioLoop))
        step = Step(step_id, line, self._featurefile, self._current_line, self.feature.scenarios[-1], not not_runable)
        self.feature.scenarios[-1].steps.append(step)
        return True

    def _parse_table(self, line):
        """
            Parses a step table row

            :param string line: the line to parse from
        """
        if not self.feature.scenarios[-1].steps:
            raise FeatureFileSyntaxError("Found step table without previous step definition on line {0}".format(self._current_line))

        self.feature.scenarios[-1].steps[-1].table.append([x.strip() for x in line.split("|")[1:-1]])
        return True

    def _parse_step_text(self, line):
        """
            Parses additional step text

            :param str line: the line to parse
        """
        if line.startswith('"""') and not self._in_step_text:
            self._in_step_text = True
            line = line[3:]

        if line.endswith('"""') and self._in_step_text:
            self._current_state = self.State.STEP
            self._in_step_text = False
            line = line[:-3]

        if line:
            self.feature.scenarios[-1].steps[-1].raw_text.append(line.strip())
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
            raise FeatureFileSyntaxError("Scenario @precondition tag must have argument in format: 'test.feature: Some scenario'")

        feature_file_name, scenario_sentence = match.groups()
        feature_file = os.path.join(os.path.dirname(self._featurefile), feature_file_name)

        try:
            feature = self._core.parse_feature(feature_file)
        except RuntimeError as e:
            if str(e) == "maximum recursion depth exceeded":  # precondition cycling
                raise FeatureFileSyntaxError("Your feature '{0}' has cycling preconditions with '{1}: {2}' starting at line {3}".format(self._featurefile, feature_file_name, scenario_sentence, self._current_line))
            raise

        if scenario_sentence not in feature:
            raise FeatureFileSyntaxError("Cannot import precondition scenario '{0}' from feature '{1}': No such scenario".format(scenario_sentence, feature_file))

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
        if self._detect_tag(line) or self._detect_scenario(line) or self._detect_scenario_loop(line) or self._detect_scenario_outline(line):
            return self._parse_scenario(line)

        return True

    def _detect_feature(self, line):
        """
            Detects a feature on the given line

            :param string line: the line to detect a feature

            :returns: if a feature was found on the given line
            :rtype: bool
        """
        if line.startswith(self.keywords.feature + self._keywords_delimiter):
            return line[len(self.keywords.feature) + len(self._keywords_delimiter):].strip()

        return None

    def _detect_scenario(self, line):
        """
            Detects a scenario on the given line

            :param string line: the line to detect a scenario

            :returns: if a scenario was found on the given line
            :rtype: bool
        """
        if line.startswith(self.keywords.scenario + self._keywords_delimiter):
            return line[len(self.keywords.scenario) + len(self._keywords_delimiter):].strip()

        return None

    def _detect_scenario_outline(self, line):
        """
            Detects a scenario outline on the given line

            :param string line: the line to detect a scenario outline

            :returns: if a scenario outline was found on the given line
            :rtype: bool
        """
        if line.startswith(self.keywords.scenario_outline + self._keywords_delimiter):
            return line[len(self.keywords.scenario_outline) + len(self._keywords_delimiter):].strip()

        return None

    def _detect_examples(self, line):
        """
            Detects an Examples block on the given line

            :param string line: the line to detect the Examples

            :returns: if an Examples block was found on the given line
            :rtype: bool
        """
        if line.startswith(self.keywords.examples + self._keywords_delimiter):
            return True

        return None

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
