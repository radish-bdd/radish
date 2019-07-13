"""
This module contains test for the radish EBNF gherkin parser.
"""

from pathlib import Path

import pytest

from radish.models import (
    Background,
    DefaultRule,
    Feature,
    Rule,
    Scenario,
    ScenarioLoop,
    ScenarioOutline,
)
from radish.parser import FeatureFileParser

FEATURE_FILES_DIR = Path(__file__).parent / "features"


@pytest.fixture(name="parser")
def setup_default_featurefileparser():
    parser = FeatureFileParser()
    return parser


def test_parse_empty_feature_file(parser):
    """The parser should be able to parse an empty Feature File"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "empty.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert ast is None


def test_parse_empty_feature_without_description(parser):
    """The parser should be able to parse a Feature without a Description"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-without-description.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert isinstance(ast, Feature)
    assert ast.short_description == "Parse a Feature without a Description"
    assert ast.description is None


@pytest.mark.parametrize(
    "feature_file_name",
    ["feature-only.feature", "feature-only-no-trailing-blankline.feature"],
    ids=["With trailing blank line", "Without trailing blank line"],
)
def test_parse_feature_without_a_scenario(parser, feature_file_name):
    """The parser should be able to parse a Feature without a Scenario"""
    # given
    feature_file_path = FEATURE_FILES_DIR / feature_file_name

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert isinstance(ast, Feature)
    assert ast.short_description == "Parse a Feature without a Scenario"
    assert ast.description == [
        "The radish parser should be able to",
        "parse a Feature File containing only",
        "a Feature, but no Scenarios.",
    ]


def test_parse_feature_with_scenario_without_steps(parser):
    """The parser should be able to parse a Feature with a single Scenario without any Steps"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-only.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    assert isinstance(ast.rules[0], DefaultRule)
    assert len(ast.rules[0].scenarios) == 1
    assert ast.rules[0].scenarios[0].short_description == "A scenario without any Steps"


def test_parse_feature_with_scenario_with_steps(parser):
    """The parser should be able to parse a Feature with a single Scenario with Steps"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-steps.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, DefaultRule)
    assert len(rule.scenarios) == 1
    scenario = rule.scenarios[0]
    assert scenario.short_description == "A simple Scenario containing three Steps"
    assert len(scenario.steps) == 3
    assert scenario.steps[0].keyword == "Given"
    assert scenario.steps[0].text == "the webservice is started"
    assert scenario.steps[1].keyword == "When"
    assert scenario.steps[1].text == "the /foo/bar route is queried"
    assert scenario.steps[2].keyword == "Then"
    assert scenario.steps[2].text == "the status code is 200"


def test_parse_feature_with_multiple_scenarios_with_steps(parser):
    """The parser should be able to parse a Feature with multiple Scenarios with Steps"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-multiple-scenarios-steps.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, DefaultRule)
    assert len(rule.scenarios) == 2
    first_scenario = rule.scenarios[0]
    assert (
        first_scenario.short_description == "A simple Scenario containing three Steps"
    )
    assert len(first_scenario.steps) == 3
    assert first_scenario.steps[0].keyword == "Given"
    assert first_scenario.steps[0].text == "the webservice is started"
    assert first_scenario.steps[1].keyword == "When"
    assert first_scenario.steps[1].text == "the /foo/bar route is queried"
    assert first_scenario.steps[2].keyword == "Then"
    assert first_scenario.steps[2].text == "the status code is 200"
    second_scenario = rule.scenarios[1]
    assert second_scenario.short_description == (
        "Another simple Scenario containing three Steps"
    )
    assert len(second_scenario.steps) == 3
    assert second_scenario.steps[0].keyword == "Given"
    assert second_scenario.steps[0].text == "the webservice is started"
    assert second_scenario.steps[1].keyword == "When"
    assert second_scenario.steps[1].text == "the /foo/not-existent route is queried"
    assert second_scenario.steps[2].keyword == "Then"
    assert second_scenario.steps[2].text == "the status code is 404"


def test_parse_feature_without_description_with_scenario_with_steps(parser):
    """
    The parser should be able to parse a Feature without
    a Description but with a single Scenario with Steps
    """
    # given
    feature_file_path = (
        FEATURE_FILES_DIR / "feature-without-description-scenario-steps.feature"
    )

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert ast.description == []
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, DefaultRule)
    assert len(rule.scenarios) == 1
    scenario = rule.scenarios[0]
    assert scenario.short_description == "A simple Scenario containing three Steps"
    assert len(scenario.steps) == 3
    assert scenario.steps[0].keyword == "Given"
    assert scenario.steps[0].text == "the webservice is started"
    assert scenario.steps[1].keyword == "When"
    assert scenario.steps[1].text == "the /foo/bar route is queried"
    assert scenario.steps[2].keyword == "Then"
    assert scenario.steps[2].text == "the status code is 200"


def test_parse_feature_with_background_without_scenario(parser):
    """The parser should be able to parse a Feature with a Background but no Scenario"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-background-no-scenario.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert isinstance(ast.background, Background)
    assert len(ast.background.steps) == 1
    assert ast.background.steps[0].keyword == "Given"
    assert ast.background.steps[0].text == "the webservice is started"


def test_parse_feature_with_background_and_scenario(parser):
    """The parser should be able to parse a Feature with a Background and a Scenario"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-background-and-scenario.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.background.steps) == 1
    assert ast.background.steps[0].keyword == "Given"
    assert ast.background.steps[0].text == "the webservice is started"

    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, DefaultRule)
    assert len(rule.scenarios) == 1
    scenario = rule.scenarios[0]
    assert scenario.short_description == "A simple Scenario containing three Steps"
    assert len(scenario.steps) == 2
    assert scenario.steps[0].keyword == "When"
    assert scenario.steps[0].text == "the /foo/bar route is queried"
    assert scenario.steps[1].keyword == "Then"
    assert scenario.steps[1].text == "the status code is 200"


def test_parse_feature_with_tags(parser):
    """The parser should be able to parse a Feature with Tags"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-with-tags.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.tags) == 2
    assert ast.tags[0].name == "tag-a"
    assert ast.tags[1].name == "tag-b"
    assert ast.short_description == "Parse a Feature with Tags"


def test_parse_feature_with_scenario_with_tags(parser):
    """The parser should be able to parse a Feature with a Scenario with Tags"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-with-tags.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    scenario = ast.rules[0].scenarios[0]
    assert len(scenario.tags) == 2
    assert scenario.tags[0].name == "tag-a"
    assert scenario.tags[1].name == "tag-b"
    assert scenario.short_description == "A simple Scenario containing three Steps"


def test_parse_feature_with_scenario_outline(parser):
    """The parser should be able to parse a Feature with a Scenario Outline"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-outline.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, DefaultRule)
    assert len(rule.scenarios) == 1
    scenario_outline = rule.scenarios[0]
    assert isinstance(scenario_outline, ScenarioOutline)
    assert (
        scenario_outline.short_description == "A simple Scenario containing three Steps"
    )
    assert len(scenario_outline.steps) == 3
    assert scenario_outline.steps[0].keyword == "Given"
    assert scenario_outline.steps[0].text == "the webservice is started"
    assert scenario_outline.steps[1].keyword == "When"
    assert scenario_outline.steps[1].text == "the <route> route is queried"
    assert scenario_outline.steps[2].keyword == "Then"
    assert scenario_outline.steps[2].text == "the status code is <status-code>"

    examples = scenario_outline.examples
    assert len(examples) == 2
    assert isinstance(examples[0], Scenario)
    assert examples[0].steps[0].text == "the webservice is started"
    assert examples[0].steps[1].text == "the /foo/bar route is queried"
    assert examples[0].steps[2].text == "the status code is 200"
    assert isinstance(examples[1], Scenario)
    assert examples[1].steps[0].text == "the webservice is started"
    assert examples[1].steps[1].text == "the /non-existant route is queried"
    assert examples[1].steps[2].text == "the status code is 404"


def test_parse_feature_with_scenario_outline_escaped_vbars(parser):
    """The parser should be able to parse a Feature with a Scenario Outline having escaped VBARs"""
    # given
    feature_file_path = (
        FEATURE_FILES_DIR / "feature-scenario-outline-escaped-vbars.feature"
    )

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    rule = ast.rules[0]
    scenario_outline = rule.scenarios[0]
    examples = scenario_outline.examples
    assert len(examples) == 2
    assert isinstance(examples[0], Scenario)
    assert examples[0].steps[0].text == "the webservice is started"
    assert examples[0].steps[1].text == "the /foo/bar route is queried"
    assert examples[0].steps[2].text == "the status code is 200|201"
    assert isinstance(examples[1], Scenario)
    assert examples[1].steps[0].text == "the webservice is started"
    assert examples[1].steps[1].text == "the /non-existant|foo route is queried"
    assert examples[1].steps[2].text == "the status code is 404"


def test_parse_feature_with_background_and_scenario_outline(parser):
    """The parser should be able to parse a Feature with a Background a a Scenario Outline"""
    # given
    feature_file_path = (
        FEATURE_FILES_DIR / "feature-background-and-scenario-outline.feature"
    )

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.background.steps) == 1
    rule = ast.rules[0]
    scenario_outline = rule.scenarios[0]
    examples = scenario_outline.examples
    assert len(examples) == 2
    assert examples[0].background == ast.background
    assert examples[1].background == ast.background


def test_parse_feature_with_scenario_outline_with_tags(parser):
    """The parser should be able to parse a Feature with a Scenario Outline with Tags"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-outline-with-tags.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    scenario = ast.rules[0].scenarios[0]
    assert isinstance(scenario, ScenarioOutline)
    assert len(scenario.tags) == 2
    assert scenario.tags[0].name == "tag-a"
    assert scenario.tags[1].name == "tag-b"
    assert scenario.short_description == "A simple Scenario containing three Steps"


def test_parse_feature_with_scenario_loop(parser):
    """The parser should be able to parse a Feature with a Scenario Loop"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-loop.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, DefaultRule)
    assert len(rule.scenarios) == 1
    scenario_loop = rule.scenarios[0]
    assert isinstance(scenario_loop, ScenarioLoop)
    assert scenario_loop.short_description == "A simple Scenario containing three Steps"
    assert len(scenario_loop.steps) == 3
    assert scenario_loop.steps[0].keyword == "Given"
    assert scenario_loop.steps[0].text == "the webservice is started"
    assert scenario_loop.steps[1].keyword == "When"
    assert scenario_loop.steps[1].text == "the <route> route is queried"
    assert scenario_loop.steps[2].keyword == "Then"
    assert scenario_loop.steps[2].text == "the status code is <status-code>"

    examples = scenario_loop.examples
    assert len(examples) == 2
    assert isinstance(examples[0], Scenario)
    assert examples[0].steps[0].text == scenario_loop.steps[0].text
    assert examples[0].steps[1].text == scenario_loop.steps[1].text
    assert examples[0].steps[2].text == scenario_loop.steps[2].text
    assert isinstance(examples[1], Scenario)
    assert examples[1].steps[0].text == scenario_loop.steps[0].text
    assert examples[1].steps[1].text == scenario_loop.steps[1].text
    assert examples[1].steps[2].text == scenario_loop.steps[2].text


def test_parse_feature_with_background_and_scenario_loop(parser):
    """The parser should be able to parse a Feature with a Background a a Scenario Loop"""
    # given
    feature_file_path = (
        FEATURE_FILES_DIR / "feature-background-and-scenario-loop.feature"
    )

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.background.steps) == 1
    rule = ast.rules[0]
    scenario_outline = rule.scenarios[0]
    examples = scenario_outline.examples
    assert len(examples) == 2
    assert examples[0].background == ast.background
    assert examples[1].background == ast.background


def test_parse_feature_with_scenario_loop_with_tags(parser):
    """The parser should be able to parse a Feature with a Scenario Loop with Tags"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-loop-with-tags.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    scenario = ast.rules[0].scenarios[0]
    assert isinstance(scenario, ScenarioLoop)
    assert len(scenario.tags) == 2
    assert scenario.tags[0].name == "tag-a"
    assert scenario.tags[1].name == "tag-b"
    assert scenario.short_description == "A simple Scenario containing three Steps"


def test_parse_feature_with_scenario_with_steps_doc_string(parser):
    """The parser should be able to parse a Feature with a Scenario and Steps with doc strings"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-steps-doc-strings.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    rule = ast.rules[0]
    scenario = rule.scenarios[0]
    assert len(scenario.steps) == 3
    assert scenario.steps[0].keyword == "Given"
    assert scenario.steps[0].text == "the webservice is started"
    assert scenario.steps[1].keyword == "When"
    assert scenario.steps[1].text == (
        "the /foo/bar route is queried with the following body"
    )
    assert scenario.steps[1].doc_string == (
        """{
  "foo": "Bar",
  "Bar": "foo"
}"""
    )
    assert scenario.steps[1].data_table is None
    assert scenario.steps[2].keyword == "Then"
    assert scenario.steps[2].text == "the status code is 200"


def test_parse_feature_with_scenario_with_steps_data_table(parser):
    """The parser should be able to parse a Feature with a Scenario and Steps with data tables"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-scenario-steps-data-tables.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    rule = ast.rules[0]
    scenario = rule.scenarios[0]
    assert len(scenario.steps) == 3
    assert scenario.steps[0].keyword == "Given"
    assert scenario.steps[0].text == "the webservice is started"
    assert scenario.steps[1].keyword == "When"
    assert scenario.steps[1].text == "the following routes are queried"
    assert scenario.steps[1].doc_string is None
    assert scenario.steps[1].data_table == [
        ["host1.com", "/foo/bar"],
        ["host2.com", "/foo/bar"],
    ]
    assert scenario.steps[2].keyword == "Then"
    assert scenario.steps[2].text == "the status codes are"
    assert scenario.steps[2].doc_string is None
    assert scenario.steps[2].data_table == [["200"], ["404"]]


def test_parse_feature_with_scenario_with_steps_data_table_escaped(parser):
    """
    The parser should be able to parse a Feature with a Scenario
    and Steps with data tables having escaped VBARs
    """
    # given
    feature_file_path = (
        FEATURE_FILES_DIR / "feature-scenario-steps-data-tables-escaped-vbars.feature"
    )

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    rule = ast.rules[0]
    scenario = rule.scenarios[0]
    assert len(scenario.steps) == 3
    assert scenario.steps[0].keyword == "Given"
    assert scenario.steps[0].text == "the webservice is started"
    assert scenario.steps[1].keyword == "When"
    assert scenario.steps[1].text == "the following routes are queried"
    assert scenario.steps[1].doc_string is None
    assert scenario.steps[1].data_table == [
        ["host1.com|foo", "/foo/bar"],
        ["host2.com", "/foo/bar|bla"],
    ]
    assert scenario.steps[2].keyword == "Then"
    assert scenario.steps[2].text == "the status codes are"
    assert scenario.steps[2].doc_string is None
    assert scenario.steps[2].data_table == [["200|201"], ["404|405"]]


def test_parse_feature_with_empty_rule(parser):
    """The parser should be able to parse a Feature with an empty Rule"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-empty-rule.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    assert isinstance(ast.rules[0], Rule)
    assert ast.rules[0].short_description == "all routes can be queried"
    assert len(ast.rules[0].scenarios) == 0


def test_parse_feature_with_rule_with_scenario(parser):
    """The parser should be able to parse a Feature with a Rule with a Scenario"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-rule-scenario.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, Rule)
    assert rule.short_description == "all routes can be queried"
    assert len(rule.scenarios) == 1
    scenario = rule.scenarios[0]
    assert scenario.short_description == "A simple Scenario containing three Steps"
    assert len(scenario.steps) == 3
    assert scenario.steps[0].keyword == "Given"
    assert scenario.steps[0].text == "the webservice is started"
    assert scenario.steps[1].keyword == "When"
    assert scenario.steps[1].text == "the /foo/bar route is queried"
    assert scenario.steps[2].keyword == "Then"
    assert scenario.steps[2].text == "the status code is 200"


def test_parse_feature_with_background_and_rule_with_scenario(parser):
    """The parser should be able to parse a Feature with a Background and a Rule with a Scenario"""
    # given
    feature_file_path = (
        FEATURE_FILES_DIR / "feature-background-and-rule-scenario.feature"
    )

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, Rule)
    assert rule.short_description == "all routes can be queried"
    assert rule.scenarios[0].background == ast.background


def test_parse_feature_with_rule_with_multiple_scenarios(parser):
    """The parser should be able to parse a Feature with a Rule with multiple Scenarios"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-rule-multiple-scenarios.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 1
    rule = ast.rules[0]
    assert isinstance(rule, Rule)
    assert rule.short_description == "all routes can be queried"
    assert len(rule.scenarios) == 2


def test_parse_feature_with_multiple_empty_rules(parser):
    """The parser should be able to parse a Feature with multiple empty Rules"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-multiple-empty-rules.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 2
    assert len(ast.rules[0].scenarios) == 0
    assert len(ast.rules[1].scenarios) == 0


def test_parse_feature_with_multiple_rules_with_scenarios(parser):
    """The parser should be able to parse a Feature with multiple Rules with a Scenario"""
    # given
    feature_file_path = FEATURE_FILES_DIR / "feature-multiple-rules-scenario.feature"

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert len(ast.rules) == 2
    assert len(ast.rules[0].scenarios) == 1
    assert len(ast.rules[1].scenarios) == 1


def test_parse_feature_with_background_and_multiple_rules_with_scenarios(parser):
    """
    The parser should be able to parse a Feature with a Background
    and multiple Rules with a Scenario
    """
    # given
    feature_file_path = (
        FEATURE_FILES_DIR / "feature-background-and-multiple-rules-scenario.feature"
    )

    # when
    ast = parser.parse_file(feature_file_path)

    # then
    assert isinstance(ast.background, Background)
    assert len(ast.rules) == 2
    assert len(ast.rules[0].scenarios) == 1
    assert ast.rules[0].scenarios[0].background == ast.background
    assert len(ast.rules[1].scenarios) == 1
    assert ast.rules[1].scenarios[0].background == ast.background
