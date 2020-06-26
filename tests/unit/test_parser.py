"""
This module contains test for the radish EBNF gherkin parser.
"""

from pathlib import Path

import pytest

from radish.models import (
    ConstantTag,
    DefaultRule,
    PreconditionTag,
    Scenario,
    ScenarioLoop,
    ScenarioOutline,
)
from radish.parser import FeatureFileParser
from radish.parser.errors import (
    RadishFirstStepMustUseFirstLevelKeyword,
    RadishLanguageNotFound,
    RadishMisplacedBackground,
    RadishMissingFeatureShortDescription,
    RadishMissingRuleShortDescription,
    RadishMissingScenarioShortDescription,
    RadishMultipleBackgrounds,
    RadishScenarioLoopInvalidIterationsValue,
    RadishScenarioLoopMissingIterations,
    RadishScenarioOutlineExamplesInconsistentCellCount,
    RadishScenarioOutlineExamplesMissingClosingVBar,
    RadishScenarioOutlineExamplesMissingOpeningVBar,
    RadishScenarioOutlineWithoutExamples,
    RadishStepDataTableInconsistentCellCount,
    RadishStepDataTableMissingClosingVBar,
    RadishStepDocStringNotClosed,
    RadishStepDoesNotStartWithKeyword,
)

FEATURE_FILES_DIR = Path(__file__).parent / "features"


@pytest.fixture(name="parser")
def setup_default_featurefileparser(mocker):
    parser = FeatureFileParser()
    parser._resolve_preconditions = mocker.MagicMock()
    return parser


def test_parse_empty_feature_file(parser):
    """The parser should parse an empty Feature File"""
    # given
    feature_file = ""

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast is None


def test_parse_short_description_from_empty_feature(parser):
    """The parser should parse the short description of an empty Feature"""
    # given
    feature_file = """
        Feature: My Feature
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.short_description == "My Feature"


def test_parse_fail_no_short_description_from_feature(parser):
    """The parser should be fail to parse a Feature without a short description"""
    # given
    feature_file = """
        Feature:
    """

    # then
    with pytest.raises(RadishMissingFeatureShortDescription):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.xfail(
    reason="Not implemented yet. Currently the second Feature is parsed as description"
)
def test_parse_fail_multiple_features_in_file(parser):
    """The parser should fail to parse multiple Features in a single Feature File"""
    # given
    feature_file = """
        Feature: My first Feature
        Feature: My second Feature
    """

    # then
    # with pytest.raises(RadishMissingFeatureShortDescription):
    # when
    parser.parse_contents(None, feature_file)


def test_parse_short_description_and_description_from_feature(parser):
    """The parser should parse the short description and the description of a Feature"""
    # given
    feature_file = """
        Feature: My Feature
            This is the description
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.short_description == "My Feature"
    assert ast.description == ["This is the description"]


def test_parse_multiline_description_from_feature(parser):
    """The parser should parse a multiline description of a Feature"""
    # given
    feature_file = """
        Feature: My Feature
            This is the description
            on multiple lines.
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.description == ["This is the description", "on multiple lines."]


def test_parse_multiline_description_with_blanklines_from_feature(parser):
    """
    The parser should parse a multiline description
    containing blank lines of a Feature
    """
    # given
    feature_file = """
        Feature: My Feature
            This is the description
            on multiple lines.

            It even contains blank lines
            which is great for readability.
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.description == [
        "This is the description",
        "on multiple lines." "",
        "It even contains blank lines",
        "which is great for readability.",
    ]


def test_parse_tag_from_a_feature(parser):
    """The parser should parse a Tag from a Feature"""
    # given
    feature_file = """
        @tag-a
        Feature: My Feature
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.tags) == 1
    assert ast.tags[0].name == "tag-a"


def test_parse_tags_on_multiple_lines_from_a_feature(parser):
    """The parser should parse multiple Tags on multiple lines from a Feature"""
    # given
    feature_file = """
        @tag-a
        @tag-b
        Feature: My Feature
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.tags) == 2
    assert ast.tags[0].name == "tag-a"
    assert ast.tags[1].name == "tag-b"


def test_parse_tags_on_same_line_from_a_feature(parser):
    """The parser should parse multiple Tags on the same line from a Feature"""
    # given
    feature_file = """
        @tag-a @tag-b
        Feature: My Feature
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.tags) == 2
    assert ast.tags[0].name == "tag-a"
    assert ast.tags[1].name == "tag-b"


def test_parse_tags_on_multiple_and_same_line_from_a_feature(parser):
    """
    The parser should parse multiple Tags on multiple and
    the same line from a Feature
    """
    # given
    feature_file = """
        @tag-a
        @tag-b @tag-c
        @tag-d
        Feature: My Feature
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.tags) == 4
    assert ast.tags[0].name == "tag-a"
    assert ast.tags[1].name == "tag-b"
    assert ast.tags[2].name == "tag-c"
    assert ast.tags[3].name == "tag-d"


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Rule: My Rule
    """,
        pytest.param(
            """
        Feature: My Feature
        Rule: My Rule
    """,
            marks=pytest.mark.xfail(
                reason="A Feature without description must have a blank line before the first block"
            ),
        ),
    ],
    ids=[
        "with a blank line between the Feature and the Rule",
        "without a blank line between the Feature and the Rule",
    ],
)
def test_parse_single_empty_rule(parser, feature_file):
    """The parser should parse a single empty Rule"""
    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules) == 1
    assert ast.rules[0].short_description == "My Rule"


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Rule: My first Rule
            Rule: My second Rule
    """,
        """
        Feature: My Feature

            Rule: My first Rule

            Rule: My second Rule
    """,
    ],
    ids=[
        "without a blank line between the Rules",
        "With a blank line between the Rules",
    ],
)
def test_parse_multiple_empty_rules(parser, feature_file):
    """The parser should parse multiple empty Rules"""
    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules) == 2
    assert ast.rules[0].short_description == "My first Rule"
    assert ast.rules[1].short_description == "My second Rule"


@pytest.mark.xfail(reason="Not Supported Yet")
def test_parse_rule_description(parser):
    """The parser should parse the Rule description"""
    # given
    feature_file = """
        Feature: My Feature

            Rule: My Rule
                This is the Rule description
                on multiple lines even.
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].description == [
        "This is the Rule description",
        "on multiple lines even.",
    ]


def test_parse_fail_no_short_description_in_rule(parser):
    """The parser should fail to parse a Rule without a short description"""
    # given
    feature_file = """
        Feature: My Feature

            Rule:
    """
    # then
    with pytest.raises(RadishMissingRuleShortDescription):
        # when
        parser.parse_contents(None, feature_file)


def test_parse_single_empty_scenario_outside_rule(parser):
    """The parser should parse a single empty Scenario outside any Rule"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert ast.rules[0].scenarios[0].short_description == "My Scenario"


def test_parse_example_synonym_for_scenario(parser):
    """The parser should recognize Example as a synonym for Scenario"""
    # given
    feature_file = """
        Feature: My Feature

            Example: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert isinstance(ast.rules[0].scenarios[0], Scenario)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario"


def test_parse_create_default_rule_for_scenario_outside_rule(parser):
    """The parser should create a DefaultRule for a Scenario outside any Rule"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules) == 1
    assert isinstance(ast.rules[0], DefaultRule)
    assert ast.rules[0].short_description is None
    assert ast.rules[0].line == 4
    assert len(ast.rules[0].scenarios) == 1


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario: My first Scenario
            Scenario: My second Scenario
    """,
        """
        Feature: My Feature

            Scenario: My first Scenario

            Scenario: My second Scenario
    """,
    ],
    ids=[
        "without a blank line between the Scenarios",
        "With a blank line between the Scenario",
    ],
)
def test_parse_multiple_empty_scenarios_outside_rule(parser, feature_file):
    """The parser should parse multiple empty Scenarios outside any Rule"""
    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 2
    assert ast.rules[0].scenarios[0].short_description == "My first Scenario"
    assert ast.rules[0].scenarios[1].short_description == "My second Scenario"


def test_parse_fail_no_short_description_in_scenario(parser):
    """The parser should fail to parse a Scenario without a short description"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario:
    """
    # then
    with pytest.raises(RadishMissingScenarioShortDescription):
        # when
        parser.parse_contents(None, feature_file)


def test_parse_single_empty_scenario_inside_rule(parser):
    """The parser should parse a single empty Scenario inside a Rule"""
    # given
    feature_file = """
        Feature: My Feature

            Rule: My Rule
                Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].short_description == "My Rule"
    assert ast.rules[0].scenarios[0].short_description == "My Scenario"


def test_parse_multiple_empty_scenario_inside_rule(parser):
    """The parser should parse multiple empty Scenarios inside a Rule"""
    # given
    feature_file = """
        Feature: My Feature

            Rule: My Rule
                Scenario: My first Scenario
                Scenario: My second Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].short_description == "My Rule"
    assert ast.rules[0].scenarios[0].short_description == "My first Scenario"
    assert ast.rules[0].scenarios[1].short_description == "My second Scenario"


def test_parse_single_empty_scenario_inside_multiple_rules(parser):
    """The parser should parse a single empty Scenario inside multiple Rules"""
    # given
    feature_file = """
        Feature: My Feature

            Rule: My first Rule
                Scenario: My Scenario

            Rule: My second Rule
                Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].short_description == "My first Rule"
    assert ast.rules[0].scenarios[0].short_description == "My Scenario"
    assert ast.rules[1].short_description == "My second Rule"
    assert ast.rules[1].scenarios[0].short_description == "My Scenario"


def test_parse_multiple_empty_scenarios_inside_multiple_rules(parser):
    """The parser should parse multiple empty Scenarios inside multiple Rules"""
    # given
    feature_file = """
        Feature: My Feature

            Rule: My first Rule
                Scenario: My first Scenario
                Scenario: My second Scenario

            Rule: My second Rule
                Scenario: My first Scenario
                Scenario: My second Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].short_description == "My first Rule"
    assert ast.rules[0].scenarios[0].short_description == "My first Scenario"
    assert ast.rules[0].scenarios[1].short_description == "My second Scenario"
    assert ast.rules[1].short_description == "My second Rule"
    assert ast.rules[1].scenarios[0].short_description == "My first Scenario"
    assert ast.rules[1].scenarios[1].short_description == "My second Scenario"


def test_parse_defaultrule_scenario_and_named_rule_scenario(parser):
    """The parser should parse a Scenario outside any Rules followed by a Scenario inside a Rule"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario

            Rule: My Rule
                Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert isinstance(ast.rules[0], DefaultRule)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario"
    assert ast.rules[1].short_description == "My Rule"
    assert ast.rules[1].scenarios[0].short_description == "My Scenario"


def test_parse_tag_from_a_scenario(parser):
    """The parser should parse a Tag from a Scenario"""
    # given
    feature_file = """
        Feature: My Feature

            @tag-a
            Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].tags) == 1
    assert ast.rules[0].scenarios[0].tags[0].name == "tag-a"


def test_parse_tags_on_multiple_lines_from_a_scenario(parser):
    """The parser should parse multiple Tags on multiple lines from a Scenario"""
    # given
    feature_file = """
        Feature: My Feature

            @tag-a
            @tag-b
            Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].tags) == 2
    assert ast.rules[0].scenarios[0].tags[0].name == "tag-a"
    assert ast.rules[0].scenarios[0].tags[1].name == "tag-b"


def test_parse_empty_background_without_short_description(parser):
    """The parser should parse an empty Background without a short description"""
    # given
    feature_file = """
        Feature: My Feature

            Background:
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.background is not None


def test_parse_empty_background_with_short_description(parser):
    """The parser should parse an empty Background with a short description"""
    # given
    feature_file = """
        Feature: My Feature

            Background: My Background
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.background.short_description == "My Background"


def test_parse_background_has_assigned_feature(parser):
    """The parser should assign the Feature to the Background"""
    # given
    feature_file = """
        Feature: My Feature

            Background: My Background
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.background.feature is not None


@pytest.mark.xfail(
    reason="RadishMultipleBackgrounds is not matched. Probably a bug in lark?"
)
def test_parse_fail_multiple_backgrounds(parser):
    """The parser should fail if multiple Backgrounds exist"""
    # given
    feature_file = """
        Feature: My Feature

            Background: My first Background
            Background: My second Background
    """

    # when
    with pytest.raises(RadishMultipleBackgrounds):
        # when
        parser.parse_contents(None, feature_file)


def test_parser_assign_background_to_single_scenario_outside_rule(parser):
    """The parser should assign a parsed Background to a single Scenario outside any Rules"""
    # given
    feature_file = """
        Feature: My Feature

            Background: My Background

            Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].scenarios[0].background is not None


def test_parser_assign_background_to_multiple_scenarios_outside_rule(parser):
    """The parser should assign a parsed Background to a every Scenario outside any Rules"""
    # given
    feature_file = """
        Feature: My Feature

            Background: My Background

            Scenario: My first Scenario
            Scenario: My second Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].scenarios[0].background is not None
    assert ast.rules[0].scenarios[1].background is not None

    assert (
        ast.rules[0].scenarios[0].background is not ast.rules[0].scenarios[1].background
    )


def test_parser_assign_background_to_single_scenario_inside_rule(parser):
    """The parser should assign a parsed Background to a single Scenario inside a Rules"""
    # given
    feature_file = """
        Feature: My Feature

            Background: My Background

            Rule: My Rule
                Scenario: My Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].scenarios[0].background is not None


def test_parser_assign_background_to_every_scenario_inside_rules(parser):
    """The parser should assign a parsed Background to a every Scenarios inside Rules"""
    # given
    feature_file = """
        Feature: My Feature

            Background: My Background

            Rule: My first Rule
                Scenario: My first Scenario
                Scenario: My second Scenario

            Rule: My second Rule
                Scenario: My first Scenario
                Scenario: My second Scenario
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].scenarios[0].background is not None
    assert ast.rules[0].scenarios[1].background is not None
    assert ast.rules[1].scenarios[0].background is not None
    assert ast.rules[1].scenarios[1].background is not None

    assert (
        ast.rules[0].scenarios[0].background is not ast.rules[0].scenarios[1].background
    )
    assert (
        ast.rules[0].scenarios[1].background is not ast.rules[1].scenarios[0].background
    )
    assert (
        ast.rules[1].scenarios[0].background is not ast.rules[1].scenarios[1].background
    )


@pytest.mark.xfail(
    reason="RadishMisplacedBackground is not matched. Probably a bug in lark?"
)
def test_parse_fail_misplaced_background(parser):
    """The parser should fail for misplaced Backgrounds"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario

            Background: My Background
    """

    # when
    with pytest.raises(RadishMisplacedBackground):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.parametrize("keyword", ["Given", "When", "Then"])
def test_parse_single_scenario_with_single_step(parser, keyword):
    """The parser should parse a single Scenario with a single Step"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                {} there is a Step
    """.format(
        keyword
    )

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == keyword
    assert ast.rules[0].scenarios[0].steps[0].used_keyword == keyword
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a Step"


def test_parse_fail_step_with_invalid_keyword(parser):
    """The parser should fail to parse a Step with an invalid keyword"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Foo there is a Step
    """

    # then
    with pytest.raises(RadishStepDoesNotStartWithKeyword):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario: My Scenario
                And there is a Step
    """,
        """
        Feature: My Feature

            Scenario: My first Scenario
                Given there is a Step

            Scenario: My second Scenario
                And there is a Step
    """,
        """
        Feature: My Feature

            Scenario: My Scenario
                But there is a Step
    """,
        """
        Feature: My Feature

            Scenario: My first Scenario
                Given there is a Step

            Scenario: My second Scenario
                But there is a Step
    """,
    ],
    ids=[
        "'And' in first Scenario",
        "'And' in second Scenario",
        "'But' in first Scenario",
        "'But' in second Scenario",
    ],
)
def test_parse_fail_first_step_no_first_level_keyword(parser, feature_file):
    """The parser should fail to parse if the first Step has no first level keyword"""
    # then
    with pytest.raises(RadishFirstStepMustUseFirstLevelKeyword):
        # when
        parser.parse_contents(None, feature_file)


def test_parse_second_level_keyword_assigned_correct_first_level_keyword(parser):
    """
    The parser should assign the correct first level keyword to a Step with a second level keyword
    """
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a Step
                And there is a Step
                When there is a Step
                And there is a Step
                Then there is a Step
                And there is a Step
                But there is a Step
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    steps = ast.rules[0].scenarios[0].steps
    assert steps[0].keyword == "Given"
    assert steps[0].used_keyword == "Given"
    assert steps[1].keyword == "Given"
    assert steps[1].used_keyword == "And"
    assert steps[2].keyword == "When"
    assert steps[2].used_keyword == "When"
    assert steps[3].keyword == "When"
    assert steps[3].used_keyword == "And"
    assert steps[4].keyword == "Then"
    assert steps[4].used_keyword == "Then"
    assert steps[5].keyword == "Then"
    assert steps[5].used_keyword == "And"
    assert steps[6].keyword == "Then"
    assert steps[6].used_keyword == "But"


def test_parse_keyword_context_reset_after_scenario(parser):
    """The parser should reset the frist level keyword context for each new Scenario"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My first Scenario
                Given there is a Step
                And there is a Step

            Scenario: My second Scenario
                When there is a Step
                And there is a Step
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    first_scenario_steps = ast.rules[0].scenarios[0].steps
    second_scenario_steps = ast.rules[0].scenarios[1].steps
    assert first_scenario_steps[0].keyword == "Given"
    assert first_scenario_steps[1].keyword == "Given"
    assert second_scenario_steps[0].keyword == "When"
    assert second_scenario_steps[1].keyword == "When"


def test_parse_single_scenario_with_multiple_steps(parser):
    """The parser should parse a single Scenario with multiple Steps"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                When there is an action
                Then there is an assertion
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 3
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[1].keyword == "When"
    assert ast.rules[0].scenarios[0].steps[1].text == "there is an action"
    assert ast.rules[0].scenarios[0].steps[2].keyword == "Then"
    assert ast.rules[0].scenarios[0].steps[2].text == "there is an assertion"


def test_parse_scenario_with_multiple_steps_separated_by_blanklines(parser):
    """The parser should parse a Scenario with multiple Steps separated by blank lines"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup

                When there is an action

                Then there is an assertion
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 3
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[1].keyword == "When"
    assert ast.rules[0].scenarios[0].steps[1].text == "there is an action"
    assert ast.rules[0].scenarios[0].steps[2].keyword == "Then"
    assert ast.rules[0].scenarios[0].steps[2].text == "there is an assertion"


def test_parse_background_with_multiple_steps(parser):
    """The parser should parse a Background with multiple Steps"""
    # given
    feature_file = """
        Feature: My Feature

            Background:
                Given there is a setup
                When there is an action
                Then there is an assertion
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.background.steps) == 3
    assert ast.background.steps[0].keyword == "Given"
    assert ast.background.steps[0].text == "there is a setup"
    assert ast.background.steps[1].keyword == "When"
    assert ast.background.steps[1].text == "there is an action"
    assert ast.background.steps[2].keyword == "Then"
    assert ast.background.steps[2].text == "there is an assertion"


def test_parse_multiple_scenarios_with_multiple_steps(parser):
    """The parser should parse multiple Scenarios with multiple Steps"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My first Scenario
                Given there is a setup
                When there is an action
                Then there is an assertion

            Scenario: My second Scenario
                Given there is a setup
                When there is an action
                Then there is an assertion
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 2
    assert len(ast.rules[0].scenarios[0].steps) == 3
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[1].keyword == "When"
    assert ast.rules[0].scenarios[0].steps[1].text == "there is an action"
    assert ast.rules[0].scenarios[0].steps[2].keyword == "Then"
    assert ast.rules[0].scenarios[0].steps[2].text == "there is an assertion"
    assert len(ast.rules[0].scenarios[1].steps) == 3
    assert ast.rules[0].scenarios[1].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[1].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[1].steps[1].keyword == "When"
    assert ast.rules[0].scenarios[1].steps[1].text == "there is an action"
    assert ast.rules[0].scenarios[1].steps[2].keyword == "Then"
    assert ast.rules[0].scenarios[1].steps[2].text == "there is an assertion"


def test_parse_step_with_single_line_doc_string(parser):
    """The parser should parse a Step with a single-line Doc String"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                \"\"\"
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == "My Doc String\n"


def test_parse_step_with_single_line_doc_string_consecutive_step(parser):
    """The parser should parse a Step with a single-line Doc String and a following Step"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                \"\"\"
                When there is a Step
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 2
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == "My Doc String\n"
    assert ast.rules[0].scenarios[0].steps[1].keyword == "When"
    assert ast.rules[0].scenarios[0].steps[1].text == "there is a Step"
    assert ast.rules[0].scenarios[0].steps[1].doc_string is None


def test_parse_step_with_multi_line_doc_string(parser):
    """The parser should parse a Step with a multi-line Doc String"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                Another line in the Doc String
                \"\"\"
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == (
        "My Doc String\nAnother line in the Doc String\n"
    )


def test_parse_step_with_multi_line_doc_string_with_blank_lines(parser):
    """The parser should parse a Step with a multi-line Doc String containing blank lines"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                Before blank lines


                After blank lines
                \"\"\"
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == (
        "Before blank lines\n" "\n" "\n" "After blank lines\n"
    )


def test_parse_dedent_doc_string(parser):
    """The parser should dedent the Doc String to the common leading whitespaces"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                    which is somewhat indented
                which is awesome
                    and useful
                \"\"\"
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == (
        "My Doc String\n"
        "    which is somewhat indented\n"
        "which is awesome\n"
        "    and useful\n"
    )


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                When I do something
    """,
        """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                \"
                When I do something
    """,
        """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                \"\"
                When I do something
    """,
    ],
    ids=[
        "not closed at all",
        "only one consecutive double quotes for closing",
        "only two consecutive double quotes for closing",
    ],
)
def test_parse_fail_doc_string_not_closed(parser, feature_file):
    """The parser should fail to parse a Doc String which isn't closed properly"""
    # then
    with pytest.raises(RadishStepDocStringNotClosed):
        # when
        parser.parse_contents(None, feature_file)


def test_parse_step_doc_string_should_preverse_comments(parser):
    """The parser should preserve gherkin comments in doc strings"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                # some comment
                My Doc String
                # another comment
                    foo
                \"\"\"
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == (
        "# some comment\n" "My Doc String\n" "# another comment\n" "    foo\n"
    )


def test_parse_step_empty_docstring(parser):
    """The parser should be able to parse an empty doc string"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                \"\"\"
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == ""


def test_parse_step_with_single_data_table_row(parser):
    """The parser should parse a Step with a single data table row"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                | foo | bar |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].data_table == [["foo", "bar"]]


def test_parse_step_with_multiple_data_table_rows(parser):
    """The parser should parse a Step with multiple data table rows"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                | foo | bar |
                | meh | rar |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].data_table == [
        ["foo", "bar"],
        ["meh", "rar"],
    ]


def test_parse_step_with_single_data_table_row_with_consecutive_step(parser):
    """The parser should parse a Step with a single data table row followed by another Step"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                | foo | bar |
                When there is a Step
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 2
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].data_table == [["foo", "bar"]]
    assert ast.rules[0].scenarios[0].steps[1].keyword == "When"
    assert ast.rules[0].scenarios[0].steps[1].text == "there is a Step"
    assert ast.rules[0].scenarios[0].steps[1].data_table is None


def test_parse_step_with_data_table_and_escaped_vbars(parser):
    """The parser should parse a Step with a data table containing escaped VBARs"""
    # given
    feature_file = r"""
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                | foo\|bla | bar |
                | foo | bar\|bla |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].data_table == [
        ["foo|bla", "bar"],
        ["foo", "bar|bla"],
    ]


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                | foo
    """,
        """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                | foo | bar |
                | meh | rar
                | bla | mop |
    """,
        """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                | foo | bar |
                | meh
    """,
    ],
    ids=[
        "no trailing VBAR in first row",
        "no trailing VBAR in middle row",
        "no trailing VBAR in last row",
    ],
)
def test_parse_fail_for_missing_closing_vbar_in_step_data_table(parser, feature_file):
    """The parser should fail when encountering missing VBAR in Step Data Table"""
    # then
    with pytest.raises(RadishStepDataTableMissingClosingVBar):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.parametrize(
    "feature_file",
    [
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
    ],
    ids=[
        "cell count mismatch in first row",
        "cell count mismatch in middle row",
        "cell count mismatch in last row",
    ],
)
def test_parse_fail_for_inconsistent_cell_count_in_step_data_table(
    parser, feature_file
):
    """The parser should fail when encountering inconsistent cell count in Step Data Table"""
    # then
    with pytest.raises(RadishStepDataTableInconsistentCellCount):
        # when
        parser.parse_contents(None, feature_file)


def test_parse_step_doc_string_and_step_data_table(parser):
    """The parser should parse a Step with a Doc String and a Data Table"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario: My Scenario
                Given there is a setup
                \"\"\"
                My Doc String
                \"\"\"
                | foo | bar |
                | meh | bla |
                When there is a Step
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].steps) == 2
    assert ast.rules[0].scenarios[0].steps[0].keyword == "Given"
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a setup"
    assert ast.rules[0].scenarios[0].steps[0].doc_string == "My Doc String\n"
    assert ast.rules[0].scenarios[0].steps[0].data_table == [
        ["foo", "bar"],
        ["meh", "bla"],
    ]


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario Loop: My Scenario Loop

            Iterations: 2
    """,
        """
        Feature: My Feature

            Scenario Loop: My Scenario Loop
            Iterations: 2
    """,
    ],
    ids=[
        "with blank line between Scenario Loop and Iterations",
        "without blank line between Scenario Loop and Iterations",
    ],
)
def test_parse_single_empty_scenario_loop(parser, feature_file):
    """The parser should parse a single Scenario Loop"""
    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert isinstance(ast.rules[0].scenarios[0], ScenarioLoop)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Loop"
    assert ast.rules[0].scenarios[0].iterations == 2


def test_parse_example_loop_synonym_for_scenario_loop(parser):
    """The parser should recognize Example Loop as a synonym for Scenario Loop"""
    # given
    feature_file = """
        Feature: My Feature

            Example Loop: My Scenario Loop
            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert isinstance(ast.rules[0].scenarios[0], ScenarioLoop)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Loop"


def test_parse_single_scenario_loop_outside_rule(parser):
    """The parser should parse a single Scenario Loop outside any Rule"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Loop: My Scenario Loop
                Given there is a Step
                When there is a Step
                Then there is a Step

            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Loop"
    assert ast.rules[0].scenarios[0].iterations == 2
    assert len(ast.rules[0].scenarios[0].steps) == 3


def test_parse_single_scenario_loop_inside_rule(parser):
    """The parser should parse a single Scenario Loop inside a Rule"""
    # given
    feature_file = """
        Feature: My Feature

            Rule: My Rule
                Scenario Loop: My Scenario Loop
                    Given there is a Step
                    When there is a Step
                    Then there is a Step

                Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].short_description == "My Rule"
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Loop"
    assert ast.rules[0].scenarios[0].iterations == 2
    assert len(ast.rules[0].scenarios[0].steps) == 3


def test_parse_fail_scenario_loop_without_iterations(parser):
    """The parser should fail if a Scenario Loop has no Iterations block"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Loop: My Scenario Loop
                Given there is a Step
    """

    # then
    with pytest.raises(RadishScenarioLoopMissingIterations):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.parametrize(
    "feature_file",
    [
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
    ],
    ids=[
        "no Iterations value",
        "string as Iterations value",
        "float as Iterations value",
        "Iterations value with spaces",
    ],
)
def test_parse_fail_scenario_loop_without_iterations_value(parser, feature_file):
    """The parser should fail if a Scenario Loop has no value for the Iterations"""
    # then
    with pytest.raises(RadishScenarioLoopInvalidIterationsValue):
        # when
        parser.parse_contents(None, feature_file)


def test_parse_tag_from_a_scenario_loop(parser):
    """The parser should parse a Tag from a Scenario Loop"""
    # given
    feature_file = """
        Feature: My Feature

            @tag-a
            Scenario Loop: My Scenario
            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].tags) == 1
    assert ast.rules[0].scenarios[0].tags[0].name == "tag-a"


def test_parse_tags_on_multiple_lines_from_a_scenario_loop(parser):
    """The parser should parse multiple Tags on multiple lines from a Scenario Loop"""
    # given
    feature_file = """
        Feature: My Feature

            @tag-a
            @tag-b
            Scenario Loop: My Scenario
            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].tags) == 2
    assert ast.rules[0].scenarios[0].tags[0].name == "tag-a"
    assert ast.rules[0].scenarios[0].tags[1].name == "tag-b"


def test_parser_build_examples_for_scenario_loop(parser):
    """The parser should build Examples for every Iteration of a Scenario Loop"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Loop: My Scenario
            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].examples) == 2


def test_parser_add_iteration_id_to_scenario_loop_example(parser):
    """
    The parser should build Examples for every Iteration of a
    Scenario Loop and add the Iteration Id to it's short description"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Loop: My Scenario
            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert (
        ast.rules[0].scenarios[0].examples[0].short_description
        == "My Scenario [Iteration: 1]"
    )
    assert (
        ast.rules[0].scenarios[0].examples[1].short_description
        == "My Scenario [Iteration: 2]"
    )


def test_parser_built_examples_for_scenario_loop_have_copied_steps(parser):
    """The parser should copy the Steps for the built Examples of a Scenario Loop"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Loop: My Scenario
                Given there is a Step

            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].examples) == 2
    assert len(ast.rules[0].scenarios[0].steps) == 1
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a Step"
    assert (
        ast.rules[0].scenarios[0].examples[0].steps[0]
        is not ast.rules[0].scenarios[0].steps[0]
    )
    assert (
        ast.rules[0].scenarios[0].examples[1].steps[0]
        is not ast.rules[0].scenarios[0].steps[0]
    )


def test_parser_assign_background_to_scenario_loop(parser):
    """The parser should assign the Background to the Scenario Loop"""
    # given
    feature_file = """
        Feature: My Feature

            Background:

            Scenario Loop: My Scenario
            Iterations: 2
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.background is not None
    assert ast.rules[0].scenarios[0].background is not None
    assert ast.rules[0].scenarios[0].examples[0].background is not None
    assert ast.rules[0].scenarios[0].examples[1].background is not None
    assert (
        ast.rules[0].scenarios[0].examples[0].background
        is not ast.rules[0].scenarios[0].examples[1].background
    )


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline

            Examples:
                | hdr |
                | foo |
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
            Examples:
                | hdr |
                | foo |
    """,
    ],
    ids=[
        "with blank line between Scenario Outline and Examples",
        "without blank line between Scenario Outline and Examples",
    ],
)
def test_parse_single_empty_scenario_outline(parser, feature_file):
    """The parser should parse a single Scenario Outline"""
    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert isinstance(ast.rules[0].scenarios[0], ScenarioOutline)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Outline"
    assert len(ast.rules[0].scenarios[0].examples) == 1


def test_parse_example_outline_synonym_for_scenario_outline(parser):
    """The parser should recognize Example Outline as a synonym for Scenario Outline"""
    # given
    feature_file = """
        Feature: My Feature

            Example Outline: My Scenario Outline
            Examples:
                | hdr |
                | foo |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert isinstance(ast.rules[0].scenarios[0], ScenarioOutline)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Outline"


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
            Examples:
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
            Examples:
                | hdr |
    """,
    ],
    ids=[
        "no Examples block given without preceeding Steps",
        "no Examples block given with preceeding Steps",
        "no Examples table given",
        "only Examples Header given",
    ],
)
def test_parse_fail_no_examples_in_scenario_outline(parser, feature_file):
    """The parser should fail to parse if no Examples is given for a Scenario Outline"""
    # then
    with pytest.raises(RadishScenarioOutlineWithoutExamples):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.parametrize(
    "feature_file",
    [
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
    ],
    ids=[
        "no trailing VBAR in header",
        "no trailing VBAR in first row",
        "no trailing VBAR in middle row",
        "no trailing VBAR in last row",
    ],
)
def test_parse_fail_for_missing_closing_vbar_in_scenario_outline_examples(
    parser, feature_file
):
    """The parser should fail when encountering missing closing VBAR in Scenario Outline Examples"""
    # then
    with pytest.raises(RadishScenarioOutlineExamplesMissingClosingVBar):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.parametrize(
    "feature_file",
    [
        pytest.param(
            """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                hdr |
    """,
            marks=pytest.mark.xfail,
        ),
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                | hdr |
                  foo |
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                | hdr |
                | foo |
                  bar |
                | meh |
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                | hdr |
                | foo |
                  bar |
    """,
    ],
    ids=[
        "no opening VBAR in header",
        "no opening VBAR in first row",
        "no opening VBAR in middle row",
        "no opening VBAR in last row",
    ],
)
def test_parse_fail_for_missing_opening_vbar_in_scenario_outline_examples(
    parser, feature_file
):
    """The parser should fail when encountering missing opening VBAR in Scenario Outline Examples"""
    # then
    with pytest.raises(RadishScenarioOutlineExamplesMissingOpeningVBar):
        # when
        parser.parse_contents(None, feature_file)


@pytest.mark.parametrize(
    "feature_file",
    [
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                | hdr1 | hdr1 |
                | foo  |
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                | hdr1 | hdr1 |
                | foo  |
                | bar  | meh  |
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                | hdr1 | hdr1 |
                | foo  | bar  |
                | bar  |
                | meh  | bla  |
    """,
        """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a Step

            Examples:
                | hdr1 | hdr1 |
                | foo  | bar  |
                | bar  | meh  |
                | bla  |
    """,
    ],
    ids=[
        "cell count mismatch with header",
        "cell count mismatch in first row",
        "cell count mismatch in middle row",
        "cell count mismatch in last row",
    ],
)
def test_parse_fail_for_inconsistent_cell_count_in_scenario_outline_examples(
    parser, feature_file
):
    """
    The parser should fail when encountering inconsistent cell count in Scenario Outline Examples
    """
    # then
    with pytest.raises(RadishScenarioOutlineExamplesInconsistentCellCount):
        # when
        parser.parse_contents(None, feature_file)


def test_parse_single_scenario_outline_outside_rule(parser):
    """The parser should parse a single Scenario Outline outside any Rule"""
    feature_file = """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a <hdr> Step
                When there is a <hdr> Step
                Then there is a <hdr> Step

            Examples:
                | hdr |
                | foo |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert isinstance(ast.rules[0].scenarios[0], ScenarioOutline)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Outline"
    assert len(ast.rules[0].scenarios[0].examples) == 1


def test_parse_single_scenario_outline_inside_rule(parser):
    """The parser should parse a single Scenario Outline inside a Rule"""
    feature_file = """
        Feature: My Feature

            Rule: My Rule
                Scenario Outline: My Scenario Outline
                    Given there is a <hdr> Step
                    When there is a <hdr> Step
                    Then there is a <hdr> Step

                Examples:
                    | hdr |
                    | foo |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].short_description == "My Rule"
    assert len(ast.rules[0].scenarios) == 1
    assert isinstance(ast.rules[0].scenarios[0], ScenarioOutline)
    assert ast.rules[0].scenarios[0].short_description == "My Scenario Outline"
    assert len(ast.rules[0].scenarios[0].examples) == 1


def test_parse_tag_from_a_scenario_outline(parser):
    """The parser should parse a Tag from a Scenario Outline"""
    # given
    feature_file = """
        Feature: My Feature

            @tag-a
            Scenario Outline: My Scenario Outline
                Given there is a <hdr> Step
                When there is a <hdr> Step
                Then there is a <hdr> Step

            Examples:
                | hdr |
                | foo |
                | bar |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].tags) == 1
    assert ast.rules[0].scenarios[0].tags[0].name == "tag-a"


def test_parse_tags_on_multiple_lines_from_a_scenario_outline(parser):
    """The parser should parse multiple Tags on multiple lines from a Scenario Outline"""
    # given
    feature_file = """
        Feature: My Feature

            @tag-a
            @tag-b
            Scenario Outline: My Scenario Outline
                Given there is a <hdr> Step
                When there is a <hdr> Step
                Then there is a <hdr> Step

            Examples:
                | hdr |
                | foo |
                | bar |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].tags) == 2
    assert ast.rules[0].scenarios[0].tags[0].name == "tag-a"
    assert ast.rules[0].scenarios[0].tags[1].name == "tag-b"


def test_parser_build_examples_for_scenario_outline(parser):
    """The parser should build Examples for every Iteration of a Scenario Outline"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a <hdr> Step
                When there is a <hdr> Step
                Then there is a <hdr> Step

            Examples:
                | hdr |
                | foo |
                | bar |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].examples) == 2


def test_parser_add_example_data_to_short_description_for_scenario_outline_examples(
    parser,
):
    """
    The parser should build Examples for every Iteration of a Scenario Outline
    and add the Example Data to it's short description
    """
    # given
    feature_file = """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a <hdr> Step
                When there is a <hdr> Step
                Then there is a <hdr> Step

            Examples:
                | hdr1 | hdr2 |
                | foo  | meh  |
                | bar  | bla  |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    examples = ast.rules[0].scenarios[0].examples
    assert (
        examples[0].short_description == "My Scenario Outline [hdr1: foo, hdr2: meh]"
        # Python 3.5 has no dict ordering
        or examples[0].short_description == "My Scenario Outline [hdr2: meh, hdr1: foo]"
    )

    assert (
        examples[1].short_description == "My Scenario Outline [hdr1: bar, hdr2: bla]"
        # Python 3.5 has no dict ordering
        or examples[1].short_description == "My Scenario Outline [hdr2: bla, hdr1: bar]"
    )


def test_parser_built_examples_for_scenario_outline_have_copied_steps(parser):
    """The parser should copy the Steps for the built Examples of a Scenario Outline"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a <hdr> Step
                When there is a <hdr> Step
                Then there is a <hdr> Step

            Examples:
                | hdr |
                | foo |
                | bar |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert len(ast.rules[0].scenarios[0].examples) == 2
    assert len(ast.rules[0].scenarios[0].steps) == 3
    assert ast.rules[0].scenarios[0].steps[0].text == "there is a <hdr> Step"
    assert (
        ast.rules[0].scenarios[0].examples[0].steps[0]
        is not ast.rules[0].scenarios[0].steps[0]
    )
    assert (
        ast.rules[0].scenarios[0].examples[1].steps[0]
        is not ast.rules[0].scenarios[0].steps[0]
    )


def test_parser_assign_background_to_scenario_outline(parser):
    """The parser should assign the Background to the Scenario Outline"""
    # given
    feature_file = """
        Feature: My Feature

            Background:

            Scenario Outline: My Scenario Outline
                Given there is a <hdr> Step
                When there is a <hdr> Step
                Then there is a <hdr> Step

            Examples:
                | hdr |
                | foo |
                | bar |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.background is not None
    assert ast.rules[0].scenarios[0].background is not None
    assert ast.rules[0].scenarios[0].examples[0].background is not None
    assert ast.rules[0].scenarios[0].examples[1].background is not None
    assert (
        ast.rules[0].scenarios[0].examples[0].background
        is not ast.rules[0].scenarios[0].examples[1].background
    )


def test_parser_replace_examples_parameter_in_scenario_outline_examples(parser):
    """The parser should replcae the Examples parameter in the built Scenario Outline Examples"""
    # given
    feature_file = """
        Feature: My Feature

            Scenario Outline: My Scenario Outline
                Given there is a <hdr1> Step
                When there is a <hdr2> Step
                Then there is a <hdr1>-<hdr2> Step

            Examples:
                | hdr1 | hdr2 |
                | foo  | bar  |
                | meh  | bla  |
    """

    # when
    ast = parser.parse_contents(None, feature_file)

    # then
    assert ast.rules[0].scenarios[0].examples[0].steps[0].text == "there is a foo Step"
    assert ast.rules[0].scenarios[0].examples[0].steps[1].text == "there is a bar Step"
    assert (
        ast.rules[0].scenarios[0].examples[0].steps[2].text == "there is a foo-bar Step"
    )

    assert ast.rules[0].scenarios[0].examples[1].steps[0].text == "there is a meh Step"
    assert ast.rules[0].scenarios[0].examples[1].steps[1].text == "there is a bla Step"
    assert (
        ast.rules[0].scenarios[0].examples[1].steps[2].text == "there is a meh-bla Step"
    )


def test_parser_precondition_tag_on_scenario(parser):
    """The parser should recognize a precondition Tag on a Scenario"""
    # given
    feature_file = """
        Feature: My Feature

            @precondition(some.feature: My Base Scenario)
            Scenario: My Scenario with a Precondition
                Given there is a Step
    """

    # when
    ast = parser.parse_contents(Path(__file__), feature_file)

    # then
    scenario = ast.rules[0].scenarios[0]
    precondition_tag = scenario.tags[0]

    assert isinstance(precondition_tag, PreconditionTag)
    assert precondition_tag.name == "precondition(some.feature: My Base Scenario)"
    assert precondition_tag.feature_filename == "some.feature"
    assert precondition_tag.scenario_short_description == "My Base Scenario"


def test_parser_constant_tag_on_feature(parser):
    """The parser should recognize a constant Tag on a Feature"""
    # given
    feature_file = """
        @constant(foo: bar)
        Feature: My Feature
    """

    # when
    ast = parser.parse_contents(Path(__file__), feature_file)

    # then
    assert isinstance(ast.tags[0], ConstantTag)


def test_parser_should_raise_error_for_unknown_language(parser):
    """The parser should raise an error for an unknown language"""
    # given
    feature_file = """
        # language: FOO
        Feature: My Feature
    """
    # then
    with pytest.raises(
        RadishLanguageNotFound, match="The language FOO is currently not supported"
    ):
        # when
        parser.parse_contents(Path(__file__), feature_file)


def test_parser_should_recognize_the_language(parser):
    """The parser should recognize the specified language in the Feature File"""
    # given
    feature_file = """
        # language: de
        Funktionalität: Meine Funktionalität

            Szenario: Mein Szenario
                Gegeben ist ein Schritt
    """

    # when
    ast = parser.parse_contents(Path(__file__), feature_file)

    # then
    assert len(ast.rules[0].scenarios) == 1
    assert ast.keyword == "Funktionalität"
