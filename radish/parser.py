# -*- coding: utf-8 -*-

import os
import io
import json

from radish.exceptions import RadishError, LanguageNotSupportedError
from radish.feature import Feature
from radish.scenario import Scenario
from radish.scenariooutline import ScenarioOutline
from radish.step import Step


class Keywords(object):
    def __init__(self, feature, scenario, scenario_outline, examples):
        self.feature = feature
        self.scenario = scenario
        self.scenario_outline = scenario_outline
        self.examples = examples


class FeatureParser(object):
    """
        Class to parse a feature file.
        A feature file contains just one feature.
    """

    LANGUAGE_LOCATION = os.path.join(os.path.dirname(__file__), "languages")
    DEFAULT_LANGUAGE = "en"

    class State(object):
        INIT = "init"
        FEATURE = "feature"
        SCENARIO = "scenario"
        SCENARIO_OUTLINE = "scenario_outline"
        STEP = "step"
        EXAMPLES = "examples"
        EXAMPLES_ROW = "examples_row"

    def __init__(self, featurefile, language="en"):
        if not os.path.exists(featurefile):
            raise OSError("Feature file at '{}' does not exist".format(featurefile))

        self._featurefile = featurefile
        self.keywords = {}
        self._keywords_delimiter = ":"

        self._current_state = FeatureParser.State.FEATURE
        self._current_line = 0
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
        if not os.path.exists(language_path):
            raise LanguageNotSupportedError(language)

        with io.open(language_path, "r", encoding="utf-8") as f:
            language_pkg = json.load(f)

        self.keywords = Keywords(**language_pkg["keywords"])

    def parse(self):
        """
            Parses the feature file of this `FeatureParser` instance

            :returns: if the parsing was successful or not
            :rtype: bool
        """
        with io.open(self._featurefile) as f:
            for line in f.readlines():
                self._current_line += 1
                line = line.strip()
                if not line or line.startswith("#"):  # line is empty or contains comment
                    continue

                if self.feature and self._detect_feature(line):
                    raise RadishError("radish supports only one Feature per feature file")

                if not self._parse_context(line):
                    raise RadishError("Syntax error in feature file {} on line {}".format(self._featurefile, self._current_line))

        if not self.feature:
            raise RadishError("No Feature found in file {}".format(self._featurefile))

    def _parse_context(self, line):
        """
            Parses arbitrary context from a line

            :param string line: the line to parse from
        """
        parse_context_func = getattr(self, "_parse_" + self._current_state)
        if not parse_context_func:
            raise RadishError("FeatureParser state {} is not support".format(self._current_state))

        return parse_context_func(line)

    def _parse_feature(self, line):
        """
            Parses a Feature Sentence

            The `INIT` state is used as initiale state.

            :param string line: the line to parse from
        """
        detected_feature = self._detect_feature(line)
        if not detected_feature:
            return False

        self.feature = Feature(detected_feature, self._featurefile, self._current_line)
        self._current_state = FeatureParser.State.SCENARIO
        return True

    def _parse_scenario(self, line):
        """
            Parses a Feature context

            :param string line: the line to parse from
        """
        detected_scenario = self._detect_scenario(line)
        scenario = Scenario
        if not detected_scenario:
            detected_scenario = self._detect_scenario_outline(line)
            scenario = ScenarioOutline
            if not detected_scenario:
                self.feature.description.append(line)
                return True

        self.feature.scenarios.append(scenario(detected_scenario, self._featurefile, self._current_line))
        self._current_state = FeatureParser.State.STEP
        return True

    def _parse_step(self, line):
        """
            Parses a single step

            :param string line: the line to parse from
        """
        # detect next keyword
        if self._detect_scenario(line) or self._detect_scenario_outline(line):
            return self._parse_scenario(line)

        if self._detect_examples(line):
            self._current_state = FeatureParser.State.EXAMPLES
            return True

        step = Step(line, self._featurefile, self._current_line)
        self.feature.scenarios[-1].steps.append(step)
        return True

    def _parse_examples(self, line):
        """
            Parses the Examples header line

            :param string line: the line to parse from
        """
        if not isinstance(self.feature.scenarios[-1], ScenarioOutline):
            raise RadishError("Scenario does not support Examples. Use 'Scenario Outline'")

        self.feature.scenarios[-1].examples.header = [x.strip() for x in line.split("|")[1:-1]]
        self._current_state = FeatureParser.State.EXAMPLES_ROW
        return True

    def _parse_examples_row(self, line):
        """
            Parses an Examples row

            :param string line: the line to parse from
        """
        # detect next keyword
        if self._detect_scenario(line) or self._detect_scenario_outline(line):
            return self._parse_scenario(line)

        self.feature.scenarios[-1].examples.rows.append([x.strip() for x in line.split("|")[1:-1]])
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
