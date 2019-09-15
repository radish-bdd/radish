"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.errors import RadishError


class RadishSyntaxError(RadishError, SyntaxError):
    def __str__(self):
        context, line, column = self.args
        return "{} at line {}, column {}.\n\n{}".format(
            self.label, line, column, context
        )


class RadishMissingFeatureShortDescription(RadishSyntaxError):
    label = "Feature is missing a short description"
    examples = ["Feature:"]


class RadishMissingRuleShortDescription(RadishSyntaxError):
    label = "Rule is missing a short description"
    examples = [
        """
        Feature: some feature

            Rule:
        """
    ]


class RadishMissingScenarioShortDescription(RadishSyntaxError):
    label = "Scenario is missing a short description"
    examples = [
        """
        Feature: some feature

            Scenario:
        """
    ]


class RadishMultipleBackgrounds(RadishSyntaxError):
    label = "Maximum one Background is allowed per Feature"
    examples = [
        """
        Feature: some feature

            Backround: My first Background
            Background: My second Background
        """
    ]


class RadishMisplacedBackground(RadishSyntaxError):
    label = "Background must be the first block in a Feature"
    examples = [
        """
        Feature: some feature
                Test

            Scenario: some scenario
                When I do

            Background: some background
                When I do
        """
    ]


class RadishStepDoesNotStartWithKeyword(RadishSyntaxError):
    label = "Steps must start with a step keyword: Given, When, Then, And, But"
    examples = [
        """
        Feature: some feature
            Test

            Scenario: some scenario
                I do
        """
    ]


class RadishStepDocStringNotClosed(RadishSyntaxError):
    label = (
        'A Step Doc String must be closed with three-consecutive double quotes: """' ""
    )
    examples = [
        """
        Feature: some feature
            Test

            Scenario: some scenario
                Given there is a Step
                \"\"\"
                My doc string
                When there is a Step
        """,
        """
        Feature: some feature
            Test

            Scenario: some scenario
                Given there is a Step
                \"\"\"
                My doc string
                "
                When there is a Step
        """,
        """
        Feature: some feature
            Test

            Scenario: some scenario
                Given there is a Step
                \"\"\"
                My doc string
                ""
                When there is a Step
        """,
    ]


class RadishScenarioOutlineWithoutExamples(RadishSyntaxError):
    label = "Scenario Outlines must have an Examples block"
    examples = [
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
        """,
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                Given there is a Step
        """,
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do

            Examples:
        """,
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do

            Examples:
                | hdr |
        """,
    ]


class RadishStepDataTableMissingClosingVBar(RadishSyntaxError):
    label = "Missing closing VBAR in Step Data Table"
    examples = [
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do
                | foo
        """,
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do
                | foo | bar
        """,
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do
                | foo | bar |
                | meh
        """,
    ]


class RadishStepDataTableInconsistentCellCount(RadishSyntaxError):
    label = "Step Data Table rows must all have the same amount of cells"
    examples = [
        """
            Feature: My Feature

                Scenario: My Scenario
                    Given there is a setup
                    | foo |
                    | bar | meh |
        """,
        """
            Feature: My Feature

                Scenario: My Scenario
                    Given there is a setup
                    | foo | bar |
                    | meh |
                    | bla | mop |
        """,
        """
            Feature: My Feature

                Scenario: My Scenario
                    Given there is a setup
                    | foo | bar |
                    | meh | bla |
                    | mop |
        """,
    ]


class RadishScenarioLoopMissingIterations(RadishSyntaxError):
    label = "The Scenario Loop is missing the Iterations block"
    examples = [
        """
            Feature: My Feature

                Scenario Loop: My Scenario
                    Given there is a setup
        """,
        """
            Feature: My Feature

                Scenario Loop: My Scenario
        """,
    ]


class RadishScenarioLoopInvalidIterationsValue(RadishSyntaxError):
    label = "The Scenario Loop is an invalid Iterations value"
    examples = [
        """
            Feature: My Feature

                Scenario Loop: My Scenario Loop
                    Given there is a Step

                Iterations:
        """,
        """
            Feature: My Feature

                Scenario Loop: My Scenario Loop
                    Given there is a Step

                Iterations: str
        """,
        """
            Feature: My Feature

                Scenario Loop: My Scenario Loop
                    Given there is a Step

                Iterations: 0.5
        """,
        """
            Feature: My Feature

                Scenario Loop: My Scenario Loop
                    Given there is a Step

                Iterations: 1 2
        """,
    ]


class RadishScenarioOutlineExamplesMissingClosingVBar(RadishSyntaxError):
    label = "Missing closing VBAR in Scenario Outline Examples"
    examples = [
        """
            Feature: My Feature

                Scenario Outline: My Scenario Outline
                    Given there is a Step

                Examples:
                    |
        """,
        """
            Feature: My Feature

                Scenario Outline: My Scenario Outline
                    Given there is a Step

                Examples:
                    | hdr
        """,
        """
            Feature: My Feature

                Scenario Outline: My Scenario Outline
                    Given there is a Step

                Examples:
                    | hdr |
                    | foo
        """,
        """
            Feature: My Feature

                Scenario Outline: My Scenario Outline
                    Given there is a Step

                Examples:
                    | hdr |
                    | foo |
                    | bar
                    | meh |
        """,
        """
            Feature: My Feature

                Scenario Outline: My Scenario Outline
                    Given there is a Step

                Examples:
                    | hdr |
                    | foo |
                    | bar
        """,
    ]


class RadishScenarioOutlineExamplesMissingOpeningVBar(RadishSyntaxError):
    label = "Missing opening VBAR in Scenario Outline Examples"
    examples = [
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do

            Examples:
                foo
        """,
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do

            Examples:
                foo |
        """,
        """
        Feature: some feature
            Test

            Scenario Outline: some scenario
                When I do

            Examples:
                | hdr |
                  foo |
        """,
    ]


class RadishScenarioOutlineExamplesInconsistentCellCount(RadishSyntaxError):
    label = "Scenario Outline Examples rows must all have the same amount of cells"
    examples = []


class RadishFirstStepMustUseFirstLevelKeyword(RadishSyntaxError):
    label = (
        "The first Step in a Scenario must use one of the first level Step keywords: "
        "Given, When or Then"
    )
    examples = []


class RadishPreconditionScenarioDoesNotExist(RadishSyntaxError):
    examples = []

    def __init__(
        self, featurefile_path, scenario_short_description, scenario_short_descriptions
    ):
        self.label = "No Scenario '{}' found in '{}' to use as a Precondition. Use one of: {}".format(  # noqa
            scenario_short_description,
            featurefile_path,
            ", ".join(scenario_short_descriptions),
        )


class RadishPreconditionScenarioRecursion(RadishSyntaxError):
    examples = []

    def __init__(self, scenario, precondition_scenario):
        self.label = "Detected a Precondition Recursion in '{}' caused by '{}'".format(
            scenario.short_description, precondition_scenario.short_description
        )

    def __str__(self):
        return self.label


class RadishLanguageNotFound(RadishSyntaxError):
    examples = []

    def __init__(self, language):
        self.label = "The language {} is currently not supported".format(language)

    def __str__(self):
        return self.label
