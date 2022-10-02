# -*- coding: utf-8 -*-

"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

import tagexpressions

from radish.core import Core
from radish.parser import FeatureParser
from radish.model import Tag
from radish.scenariooutline import ScenarioOutline
from radish.scenarioloop import ScenarioLoop
from radish.background import Background
import radish.exceptions as errors


@pytest.mark.parametrize("parser", [("empty-feature",)], indirect=["parser"])
def test_parse_invalid_state(parser):
    """
    Test invalid state when parsing
    """
    # given
    parser._current_state = "not_existing_state"

    # when
    with pytest.raises(errors.RadishError) as exc:
        parser.parse()

    # then
    assert str(exc.value) == "FeatureParser state not_existing_state is not supported"


@pytest.mark.parametrize(
    "language, feature_keyword, scenario_keyword",
    [("en", "Feature", "Scenario"), ("de", "Funktionalität", "Szenario")],
)
def test_creating_language_agnostic_parser(
    language, feature_keyword, scenario_keyword, core
):
    """
    Test creating a language agnostic parser
    """
    # given & when
    parser = FeatureParser(core, "/", 1, language=language)

    # then
    assert parser.keywords.feature == feature_keyword
    assert parser.keywords.scenario == scenario_keyword


def test_creating_parser_for_not_supported_lang(core):
    """
    Test creating a Parser for a not supported language
    """
    # given & when
    with pytest.raises(errors.LanguageNotSupportedError) as exc:
        FeatureParser(core, "/", 1, language="chruesimuesi")

    # then
    assert str(exc.value) == "Language chruesimuesi could not be found"


def test_creating_parser_with_unsupported_lang_detection(core):
    """
    Test creating a Parser with yet unsupported language auto detection
    """
    # given & when
    with pytest.raises(NotImplementedError) as exc:
        FeatureParser(core, "/", 1, language=None)

    # then
    assert str(exc.value) == "Auto detect language is not implemented yet"


@pytest.mark.parametrize("parser", [("german",)], indirect=["parser"])
def test_parse_featurefile_with_language_tag(parser):
    """
    Test parsing a Feature File with a language tag
    """
    # when
    parser.parse()

    # then
    assert parser.feature.sentence == "Das ist eine radish Funktionalität"
    assert parser.feature.scenarios[0].sentence == "Dies ist ein Szenario"


def test_parse_not_existing_featurefile(core):
    """
    Test parsing a not existing Feature File
    """
    # given & when
    with pytest.raises(OSError) as exc:
        FeatureParser(core, "does-not-exist.feature", 1)

    # then
    assert str(exc.value) == "Feature file at 'does-not-exist.feature' does not exist"


@pytest.mark.parametrize("parser", [("empty",)], indirect=["parser"])
def test_parse_empty_featurefile(parser):
    """
    Test parsing an empty Feature File
    """
    # when
    with pytest.raises(errors.FeatureFileSyntaxError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith("No Feature found in file")


@pytest.mark.parametrize("parser", [("empty-feature",)], indirect=["parser"])
def test_parse_empty_feature(parser):
    """
    Test parsing an empty Feature
    """
    # when
    parser.parse()

    # then
    assert parser.feature.sentence == "This is an empty Feature"
    assert len(parser.feature.scenarios) == 0


@pytest.mark.parametrize("parser", [("feature-only-description",)], indirect=["parser"])
def test_parse_empty_feature_with_description(parser):
    """
    Test parsing a Feature with Description but without Scenarios
    """
    # when
    parser.parse()

    # then
    assert parser.feature.description[0] == "This is a description"
    assert parser.feature.description[1] == "with two lines"


@pytest.mark.parametrize("parser", [("multi-features",)], indirect=["parser"])
def test_parse_featurefile_with_multiple_features(parser):
    """
    Test parsing a Feature File containing multiple Features
    """
    # when
    with pytest.raises(errors.RadishError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith(
        "radish supports only one Feature per feature file"
    )


@pytest.mark.parametrize(
    "parser", [("syntax-error-unknown-keyword",)], indirect=["parser"]
)
def test_parse_featurefile_with_syntax_error(parser):
    """
    Test parsing a Feature File with Syntax Errors
    """
    # when
    with pytest.raises(errors.FeatureFileSyntaxError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith("Syntax error in feature file")


@pytest.mark.parametrize("parser", [("empty-scenario",)], indirect=["parser"])
def test_parse_feature_with_empty_scenario(parser):
    """
    Test parsing a Feature with an empty Scenario
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 1
    assert feature.scenarios[0].sentence == "This is an empty Scenario"
    assert len(feature.scenarios[0].steps) == 0


@pytest.mark.parametrize("parser", [("feature-scenario-steps",)], indirect=["parser"])
def test_parse_feature_with_scenario_and_steps(parser):
    """
    Test parsing a Feature with a Scenario and Steps
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 1
    assert len(feature.scenarios[0].steps) == 3
    assert feature.scenarios[0].steps[0].sentence == "Given I have a Step"
    assert feature.scenarios[0].steps[1].sentence == "When I do something"
    assert feature.scenarios[0].steps[2].sentence == "Then I expect something"


@pytest.mark.parametrize("parser", [("feature-scenarios",)], indirect=["parser"])
def test_parse_feature_with_scenarios(parser):
    """
    Test parsing a Feature with multiple Scenarios and Steps
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 2
    assert len(feature.scenarios[0].steps) == 3
    assert len(feature.scenarios[1].steps) == 3


@pytest.mark.parametrize("parser", [("comments",)], indirect=["parser"])
def test_parse_featurefile_with_comments(parser):
    """
    Test parsing a Feature File with comments
    """
    # when
    feature = parser.parse()

    # then
    assert feature.sentence == "Ignore comments in Parser"
    assert len(feature.description) == 1
    assert feature.description[0] == "Radish shall ignore comments in Feature Files"
    assert len(feature.scenarios) == 1
    assert len(feature.scenarios[0].steps) == 1
    assert feature.scenarios[0].steps[0].sentence == "When I do something"


@pytest.mark.parametrize("parser", [("scenario-outline",)], indirect=["parser"])
def test_parse_feature_with_scenario_outline(parser):
    """
    Test parsing a Feature with a simple Scenario Outline
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 1
    assert isinstance(feature.scenarios[0], ScenarioOutline)
    assert len(feature.scenarios[0].scenarios) == 2

    # then - expect correct scenario steps with replaced fields
    assert (
        feature.scenarios[0].scenarios[0].steps[0].sentence
        == "Given I have the number 1"
    )
    assert (
        feature.scenarios[0].scenarios[0].steps[1].sentence == "And I have the number 2"
    )
    assert feature.scenarios[0].scenarios[0].steps[2].sentence == "When I add them up"
    assert (
        feature.scenarios[0].scenarios[0].steps[3].sentence
        == "Then I expect the sum to be 3"
    )

    assert (
        feature.scenarios[0].scenarios[1].steps[0].sentence
        == "Given I have the number 4"
    )
    assert (
        feature.scenarios[0].scenarios[1].steps[1].sentence == "And I have the number 5"
    )
    assert feature.scenarios[0].scenarios[1].steps[2].sentence == "When I add them up"
    assert (
        feature.scenarios[0].scenarios[1].steps[3].sentence
        == "Then I expect the sum to be 9"
    )


@pytest.mark.parametrize(
    "parser", [("scenario-outline-step-text",)], indirect=["parser"]
)
def test_parse_scenario_outline_with_step_text(parser):
    """
    Test parsing a Scenario Outline with a Step with Text
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 1
    assert isinstance(feature.scenarios[0], ScenarioOutline)
    assert len(feature.scenarios[0].scenarios) == 3

    # then - expect correct scenario steps with replaced fields
    assert (
        feature.scenarios[0].scenarios[0].steps[0].sentence
        == "Given I have the number 10"
    )
    assert feature.scenarios[0].scenarios[0].steps[1].sentence == "And I have the text"
    assert feature.scenarios[0].scenarios[0].steps[1].text == "foobar"


@pytest.mark.parametrize(
    "parser", [("escaping-scenario-examples",)], indirect=["parser"]
)
def test_pipes_in_scenario_example_rows_can_be_escaped(parser):
    """
    Test that a PIPE (|) can be used in a Scenario Example row value
    when it's escaped with a backslash
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 1
    assert isinstance(feature.scenarios[0], ScenarioOutline)

    step = feature.scenarios[0].scenarios[0].steps[0]
    assert step.sentence == "I do some stuff 1 hei|ho 2"

    step = feature.scenarios[0].scenarios[1].steps[0]
    assert step.sentence == "I do some stuff 1 hei\\ho 2"


@pytest.mark.parametrize(
    "parser", [("regular-scenario-examples",)], indirect=["parser"]
)
def test_parse_feature_with_scenario_and_examples(parser):
    """
    Test parsing a Feature with a Scenario combined with Examples without a Scenario Outline
    """
    # when
    with pytest.raises(errors.RadishError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith(
        "Scenario does not support Examples. Use 'Scenario Outline'"
    )


@pytest.mark.parametrize("parser", [("scenario-loop",)], indirect=["parser"])
def test_parse_feature_with_scenario_loop(parser):
    """
    Test parsing a Feature with a simple Scenario Loop
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 1
    assert isinstance(feature.scenarios[0], ScenarioLoop)
    assert len(feature.scenarios[0].scenarios) == 2

    assert (
        feature.scenarios[0].scenarios[0].steps[0].sentence
        == "Given I have an instable function"
    )
    assert feature.scenarios[0].scenarios[0].steps[1].sentence == "When I execute it"
    assert (
        feature.scenarios[0].scenarios[0].steps[2].sentence
        == "Then I expect it to pass"
    )

    assert (
        feature.scenarios[0].scenarios[1].steps[0].sentence
        == "Given I have an instable function"
    )
    assert feature.scenarios[0].scenarios[1].steps[1].sentence == "When I execute it"
    assert (
        feature.scenarios[0].scenarios[1].steps[2].sentence
        == "Then I expect it to pass"
    )


@pytest.mark.parametrize("parser", [("step-tabular-data",)], indirect=["parser"])
def test_parse_step_tabular_data(parser):
    """
    Test parsing a Feature with a Scenario and Step with Tabular Data
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios[0].steps) == 3
    assert len(feature.scenarios[0].steps[0].table_header) == 3
    assert feature.scenarios[0].steps[0].table_header == [
        "firstname",
        "surname",
        "heroname",
    ]
    assert len(feature.scenarios[0].steps[0].table) == 2
    assert feature.scenarios[0].steps[0].table[0] == {
        "firstname": "Bruce",
        "surname": "Wayne",
        "heroname": "Batman",
    }
    assert feature.scenarios[0].steps[0].table[1] == {
        "firstname": "Peter",
        "surname": "Parker",
        "heroname": "Spiderman",
    }


@pytest.mark.parametrize(
    "parser", [("step-tabular-data-invalid",)], indirect=["parser"]
)
def test_parse_step_tabular_data_invalid(parser):
    """
    Test parsing a Step Table without a Step
    """
    # when
    with pytest.raises(errors.FeatureFileSyntaxError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith(
        "Found step table without previous step definition on line 6"
    )


@pytest.mark.parametrize("parser", [("step-text-data",)], indirect=["parser"])
def test_parse_step_text_data(parser):
    """
    Test parsing a Feature with a Scenario and Step with Text Data
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios[0].steps) == 3
    assert feature.scenarios[0].steps[0].text == "To be or not to be"


@pytest.mark.parametrize(
    "parser, expected_feature_tags, expected_scenarios_tags",
    [
        (["tags-feature"], [Tag("foo"), Tag("bar")], [[]]),
        (["tags-scenario"], [], [[Tag("foo"), Tag("bar")]]),
        (
            ["tags-everywhere"],
            [Tag("foo"), Tag("bar")],
            [
                [Tag("regular_scenario")],
                [Tag("scenario_outline")],
                [Tag("scenario_loop")],
            ],
        ),
        (["tags-arguments"], [Tag("foo", "bar")], [[Tag("sometag", "somevalue")]]),
    ],
    indirect=["parser"],
)
def test_parse_tags(parser, expected_feature_tags, expected_scenarios_tags):
    """
    Test parsing Feature and Scenario Tags
    """
    # when
    feature = parser.parse()

    # then
    assert feature.tags == expected_feature_tags
    assert len(feature.scenarios) == len(expected_scenarios_tags)
    for scenario, expected_scenario_tags in zip(
        feature.scenarios, expected_scenarios_tags
    ):
        assert scenario.tags == expected_scenario_tags


@pytest.mark.parametrize(
    "parser",
    [("tags-ignored-feature", [], {"tag_expr": tagexpressions.parse("not foo")})],
    indirect=["parser"],
)
def test_parse_ignored_feature_via_tag(parser):
    """
    Test parsing a Feature which is ignored because of a Tag
    """
    # when
    feature = parser.parse()

    # then
    assert feature is None


@pytest.mark.parametrize(
    "parser",
    [("tags-ignored-scenario", [], {"tag_expr": tagexpressions.parse("not foo")})],
    indirect=["parser"],
)
def test_parse_ignored_scenario_via_tag(parser):
    """
    Test parsing a Feature with ignored Scenarios because of a Tag
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 2
    assert feature.scenarios[0].sentence == "Parsed Scenario"
    assert feature.scenarios[1].sentence == "Another parsed Scenario"


@pytest.mark.parametrize(
    "parser",
    [("tags-no-feature", [], {"tag_expr": tagexpressions.parse("not foo")})],
    indirect=["parser"],
)
def test_parse_ignored_feature_empty_featurefile(parser):
    """
    Test detecting if no Feature left because of given Tag expression
    """
    # when
    feature = parser.parse()

    # then
    assert feature is None


@pytest.mark.parametrize(
    "parser, expected_scenarios",
    [
        (
            ("tag-inheritance", [], {"tag_expr": tagexpressions.parse("some_feature")}),
            3,
        ),
        (
            (
                "tag-inheritance",
                [],
                {"tag_expr": tagexpressions.parse("some_feature and good_case")},
            ),
            2,
        ),
        (
            (
                "tag-inheritance",
                [],
                {"tag_expr": tagexpressions.parse("some_feature and bad_case")},
            ),
            1,
        ),
        (
            (
                "tag-inheritance",
                [],
                {"tag_expr": tagexpressions.parse("some_feature and not bad_case")},
            ),
            2,
        ),
        (
            (
                "tag-inheritance",
                [],
                {"tag_expr": tagexpressions.parse("good_case or bad_case")},
            ),
            3,
        ),
    ],
    indirect=["parser"],
)
def test_parse_tag_inheritance(parser, expected_scenarios):
    """
    Test parsing a Feature and Scenarios with Tags and check the Tag inheritance
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == expected_scenarios


@pytest.mark.parametrize("parser", [("background",)], indirect=["parser"])
def test_parse_simple_background(parser):
    """
    Test parsing a Feature with a simple Background
    """
    # when
    feature = parser.parse()

    # then
    assert isinstance(feature.background, Background)
    assert len(feature.scenarios) == 2
    assert all(
        s.background.sentence == feature.background.sentence for s in feature.scenarios
    )


@pytest.mark.parametrize("parser", [("background-no-sentence",)], indirect=["parser"])
def test_parse_background_no_sentence(parser):
    """
    Test parsing a Feature with unnamed Background
    """
    # when
    feature = parser.parse()

    # then
    assert isinstance(feature.background, Background)
    assert feature.background.sentence == ""
    assert len(feature.scenarios) == 2
    assert all(
        s.background.sentence == feature.background.sentence for s in feature.scenarios
    )


@pytest.mark.parametrize(
    "parser", [("background-scenariooutline",)], indirect=["parser"]
)
def test_parse_background_for_scenario_outline(parser):
    """
    Test parsing a Feature with a Background and Scenario Outline
    """
    # when
    feature = parser.parse()

    # then
    assert isinstance(feature.background, Background)
    assert all(
        s.background.sentence == feature.background.sentence
        for s in feature.scenarios[0].scenarios
    )


@pytest.mark.parametrize("parser", [("background-scenarioloop",)], indirect=["parser"])
def test_parse_background_for_scenario_loop(parser):
    """
    Test parsing a Feature with a Background and Scenario Loop
    """
    # when
    feature = parser.parse()

    # then
    assert isinstance(feature.background, Background)
    assert all(
        s.background.sentence == feature.background.sentence
        for s in feature.scenarios[0].scenarios
    )


@pytest.mark.parametrize(
    "parser", [("background-subsequent-tag",)], indirect=["parser"]
)
def test_parse_background_subsequent_tag(parser):
    """
    Test parsing a Feature with Background followed by a tagged Scenario
    """
    # when
    feature = parser.parse()

    # then
    assert isinstance(feature.background, Background)
    assert len(feature.background.steps) == 2
    assert len(feature.scenarios[0].tags) == 2


@pytest.mark.parametrize("parser", [("background-misplaced",)], indirect=["parser"])
def test_parse_misplaced_background(parser):
    """
    Test detecting a misplaced Background
    """
    # when
    with pytest.raises(errors.FeatureFileSyntaxError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith(
        "The Background block must be placed before any Scenario block"
    )


@pytest.mark.parametrize("parser", [("background-multiple",)], indirect=["parser"])
def test_parse_multiple_background(parser):
    """
    Test detecting a multiple Backgrounds
    """
    # when
    with pytest.raises(errors.FeatureFileSyntaxError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith(
        "The Background block may only appear once in a Feature"
    )


@pytest.mark.parametrize("parser", [("constants",)], indirect=["parser"])
def test_parse_constants(parser):
    """
    Test parsing Feature and Scenario constants
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.constants) == 1
    assert len(feature.scenarios[0].constants) == 2
    assert len(feature.scenarios[1].constants) == 2


@pytest.mark.parametrize(
    "parser", [("scenario-sentence-duplicate",)], indirect=["parser"]
)
def test_parse_scenario_sentence_duplicate(parser):
    """
    Test detecting Scenario sentence duplicates
    """
    # when
    with pytest.raises(errors.FeatureFileSyntaxError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith(
        "Scenario with name 'A great name for a Scenario' " "defined twice in feature"
    )


@pytest.mark.parametrize("parser", [("precondition-level-2",)], indirect=["parser"])
def test_parse_simple_layered_preconditions(parser):
    """
    Test parsing simple three layered Scenario preconditions
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 1
    assert len(feature.scenarios[0].preconditions) == 1
    assert len(feature.scenarios[0].preconditions[0].preconditions) == 1


@pytest.mark.parametrize(
    "parser", [("precondition-same-feature",)], indirect=["parser"]
)
def test_parse_scenario_precondition_same_feature(parser):
    """
    Test parsing simple three layered Scenario preconditions
    """
    # when
    feature = parser.parse()

    # then
    assert len(feature.scenarios) == 2
    assert len(feature.scenarios[1].preconditions) == 1


@pytest.mark.parametrize(
    "parser, expected_error_msg",
    [
        (
            ("precondition-unknown-scenario",),
            "Cannot import precondition scenario 'Unknown Scenario' from feature",
        ),
        (
            ("precondition-unknown-scenario-same-feature",),
            "Cannot import precondition scenario 'Unknown Scenario' from feature",
        ),
        (("precondition-recursion",), "Your feature"),
        (
            ("precondition-malformed",),
            "Scenario @precondition tag must have argument in format: 'test.feature: Some scenario'",
        ),
    ],
    ids=[
        "Unknown Scenario",
        "Unknown Scenario within same Feature",
        "Recursion",
        "Malformed precondition Tag",
    ],
    indirect=["parser"],
)
def test_parse_scenario_precondition_errors(parser, expected_error_msg):
    """
    Test detecting Scenario Precondition Parsing errors
    """
    # when
    with pytest.raises(errors.FeatureFileSyntaxError) as exc:
        parser.parse()

    # then
    assert str(exc.value).startswith(expected_error_msg)
