"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import re
import textwrap

import colorful as cf
import pytest

from radish.formatters.gherkin import (
    write_feature_footer,
    write_feature_header,
    write_rule_header,
    write_scenario_footer,
    write_scenario_header,
    write_step,
    write_step_result,
    write_tagline,
)
from radish.models import (
    Background,
    DefaultRule,
    Feature,
    Rule,
    Scenario,
    State,
    Step,
    Tag,
)


@pytest.fixture(name="disabled_colors", scope="function")
def disable_ansi_colors(world_default_config):
    """Fixture to disable ANSI colors"""
    orig_colormode = cf.colormode
    cf.disable()
    world_default_config.no_ansi = True
    yield
    cf.colormode = orig_colormode


def dedent_feature_file(contents):
    """Dedent the given Feature File contents"""
    dedented = textwrap.dedent(contents)
    # remove first empty line
    return "\n".join(dedented.splitlines()[1:]) + "\n"


def assert_output(capsys, expected_stdout):
    """Assert that the captured stdout matches"""
    actual_stdout = capsys.readouterr().out
    for actual_stdout_line, expected_stdout_line in zip(
        actual_stdout.splitlines(), expected_stdout.splitlines()
    ):
        assert re.match(
            "^" + expected_stdout_line + "$", actual_stdout_line
        ), "{!r} == {!r}".format(expected_stdout_line, actual_stdout_line)


def test_gf_write_tag_after_an_at_sign(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter writes a Tag after the @-sign on a single line"""
    # given
    tag = mocker.MagicMock(spec=Tag)
    tag.name = "tag-a"

    # when
    write_tagline(tag)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "@tag-a\n"


def test_gf_write_tag_with_given_identation(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter writes a Tag with the given indentation"""
    # given
    tag = mocker.MagicMock(spec=Tag)
    tag.name = "tag-a"
    indentation = " " * 4

    # when
    write_tagline(tag, indentation)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "    @tag-a\n"


def test_gf_write_feature_header_without_tags_without_description_without_background(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    with no Tags, no description and no Background
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.keyword = "Feature"
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = None

    # when
    write_feature_header(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "Feature: My Feature\n"


def test_gf_write_feature_header_with_tags_without_description_without_background(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    with Tags, but no description and no Background
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.keyword = "Feature"
    feature.short_description = "My Feature"
    feature.description = []
    first_tag = mocker.MagicMock(spec=Tag)
    first_tag.name = "tag-a"
    second_tag = mocker.MagicMock(spec=Tag)
    second_tag.name = "tag-b"
    feature.tags = [first_tag, second_tag]
    feature.background = None

    # when
    write_feature_header(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == dedent_feature_file(
        """
        @tag-a
        @tag-b
        Feature: My Feature
        """
    )


def test_gf_write_feature_header_without_tags_with_description_without_background(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Background, but description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.keyword = "Feature"
    feature.short_description = "My Feature"
    feature.description = ["foo", "bar", "bla"]
    feature.tags = []
    feature.background = None

    # when
    write_feature_header(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == dedent_feature_file(
        """
        Feature: My Feature
            foo
            bar
            bla

        """
    )


def test_gf_write_feature_header_without_description_with_empty_background_no_short_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Description, but with an empty Background with no short description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.keyword = "Feature"
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.keyword = "Background"
    feature.background.short_description = None
    feature.background.steps = []

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                Background:[ ]

            """
        ),
    )


def test_gf_write_feature_header_with_description_with_empty_background_no_short_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags, but Description and an empty Background with no short description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.keyword = "Feature"
    feature.short_description = "My Feature"
    feature.description = ["foo", "bar", "bla"]
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.keyword = "Background"
    feature.background.short_description = None
    feature.background.steps = []

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                foo
                bar
                bla

                Background:[ ]

            """
        ),
    )


def test_gf_write_feature_header_empty_background_with_short_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Description but an empty Background with short description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.keyword = "Feature"
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.keyword = "Background"
    feature.background.short_description = "My Background"
    feature.background.steps = []

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                Background: My Background

            """
        ),
    )


def test_gf_write_feature_header_background_with_steps(disabled_colors, capsys, mocker):
    """
    Test that the Gherkin Formatter properly writes a Feature header
    without Tags and Description but a Background with Steps
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.keyword = "Feature"
    feature.short_description = "My Feature"
    feature.description = []
    feature.tags = []
    feature.background = mocker.MagicMock(spec=Background)
    feature.background.keyword = "Background"
    feature.background.short_description = "My Background"
    first_step = mocker.MagicMock(
        spec=Step,
        keyword="Given",
        used_keyword="Given",
        text="there is a Step",
        doc_string=None,
        data_table=None,
    )
    second_step = mocker.MagicMock(
        spec=Step,
        keyword="When",
        used_keyword="When",
        text="there is a Step",
        doc_string=None,
        data_table=None,
    )
    feature.background.steps = [first_step, second_step]

    # when
    write_feature_header(feature)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            Feature: My Feature
                Background: My Background
                    Given there is a Step
                    When there is a Step
            """
        ),
    )


def test_gf_write_feature_footer_blank_line_if_no_description_and_no_rules(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter writes a blank line after a Feature
    without a description and Rules
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.description = []
    feature.rules = []

    # when
    write_feature_footer(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "\n"


def test_gf_write_feature_footer_no_blank_line_if_description(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter writes no blank line after a Feature
    with a Description
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.description = ["foo"]
    feature.rules = []

    # when
    write_feature_footer(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == ""


def test_gf_write_feature_footer_no_blank_line_if_rules(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter writes no blank line after a Feature
    with a Rule
    """
    # given
    feature = mocker.MagicMock(spec=Feature)
    feature.description = []
    feature.rules = ["foo"]

    # when
    write_feature_footer(feature)

    # then
    stdout = capsys.readouterr().out
    assert stdout == ""


def test_gf_write_rule_header(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter properly writes a Rule"""
    # given
    rule = mocker.MagicMock(spec=Rule)
    rule.keyword = "Rule"
    rule.short_description = "My Rule"

    # when
    write_rule_header(rule)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>    )Rule: My Rule

            """
        ),
    )


def test_gf_write_rule_header_nothing_for_default_rule(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter writes no Rule header for a DefaultRule"""
    # given
    rule = mocker.MagicMock(spec=DefaultRule)

    # when
    write_rule_header(rule)

    # then
    stdout = capsys.readouterr().out
    assert stdout == ""


@pytest.mark.parametrize(
    "given_rule_type, expected_indentation",
    [(DefaultRule, " " * 4), (Rule, " " * 8)],
    ids=["DefaultRule", "Rule"],
)
def test_gf_write_scenario_header_without_tags(
    given_rule_type, expected_indentation, disabled_colors, capsys, mocker
):
    """Test that the Gherkin Formatter properly formatter a Scenario Header without Tags"""
    # given
    scenario = mocker.MagicMock(spec=Scenario)
    scenario.keyword = "Scenario"
    scenario.rule = mocker.MagicMock(spec=given_rule_type)
    scenario.short_description = "My Scenario"
    scenario.tags = []

    # when
    write_scenario_header(scenario)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>{indentation})Scenario: My Scenario
            """.format(
                indentation=expected_indentation
            )
        ),
    )


@pytest.mark.parametrize(
    "given_rule_type, expected_indentation",
    [(DefaultRule, " " * 4), (Rule, " " * 8)],
    ids=["DefaultRule", "Rule"],
)
def test_gf_write_scenario_header_with_tags(
    given_rule_type, expected_indentation, disabled_colors, capsys, mocker
):
    """Test that the Gherkin Formatter properly formatter a Scenario Header with Tags"""
    # given
    scenario = mocker.MagicMock(spec=Scenario)
    scenario.keyword = "Scenario"
    scenario.rule = mocker.MagicMock(spec=given_rule_type)
    scenario.short_description = "My Scenario"
    first_tag = mocker.MagicMock(spec=Tag)
    first_tag.name = "tag-a"
    second_tag = mocker.MagicMock(spec=Tag)
    second_tag.name = "tag-b"
    scenario.tags = [first_tag, second_tag]

    # when
    write_scenario_header(scenario)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>{indentation})@tag-a
            (?P<indentation>{indentation})@tag-b
            (?P<indentation>{indentation})Scenario: My Scenario
            """.format(
                indentation=expected_indentation
            )
        ),
    )


def test_gf_write_scenario_footer_always_a_blank_line(disabled_colors, capsys, mocker):
    """Test that the Gherkin Formatter always writes a blank line after a Scenario"""
    # given
    scenario = mocker.MagicMock(spec=Scenario)

    # when
    write_scenario_footer(scenario)

    # then
    stdout = capsys.readouterr().out
    assert stdout == "\n"


@pytest.mark.parametrize(
    "given_rule_type, expected_indentation",
    [(DefaultRule, " " * 8), (Rule, " " * 12)],
    ids=["DefaultRule", "Rule"],
)
def test_gf_write_step_without_doc_string_without_data_table(
    given_rule_type, expected_indentation, disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly formats a Step without a doc string and data table
    """
    # given
    step = mocker.MagicMock(spec=Step)
    step.keyword = "Given"
    step.used_keyword = "Given"
    step.text = "there is a Step"
    step.doc_string = None
    step.data_table = None
    step.rule = mocker.MagicMock(spec=given_rule_type)

    # when
    write_step(step, step_color_func=lambda x: x)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>{indentation})Given there is a Step
            """.format(
                indentation=expected_indentation
            )
        ),
    )


def test_gf_write_step_explicit_indentation_without_doc_string_without_data_table(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly formats a Step with an explicit indentation
    butwithout a doc string and data table
    """
    # given
    step = mocker.MagicMock(spec=Step)
    step.keyword = "Given"
    step.used_keyword = "Given"
    step.text = "there is a Step"
    step.doc_string = None
    step.data_table = None

    # when
    write_step(step, step_color_func=lambda x: x, indentation="   ")

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>   )Given there is a Step
            """
        ),
    )


@pytest.mark.parametrize(
    "given_rule_type, expected_indentation",
    [(DefaultRule, " " * 8), (Rule, " " * 12)],
    ids=["DefaultRule", "Rule"],
)
def test_gf_write_step_with_doc_string_without_data_table(
    given_rule_type, expected_indentation, disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly formats a Step with a doc string
    but without a data table
    """
    # given
    step = mocker.MagicMock(spec=Step)
    step.keyword = "Given"
    step.used_keyword = "Given"
    step.text = "there is a Step"
    step.doc_string = """foo
bar
bla
"""
    step.data_table = None
    step.rule = mocker.MagicMock(spec=given_rule_type)

    # when
    write_step(step, step_color_func=lambda x: x)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>{indentation})Given there is a Step
            (?P<indentation>{indentation}    )\"\"\"
            (?P<indentation>{indentation}    )foo
            (?P<indentation>{indentation}    )bar
            (?P<indentation>{indentation}    )bla
            (?P<indentation>{indentation}    )\"\"\"
            """.format(
                indentation=expected_indentation
            )
        ),
    )


@pytest.mark.parametrize(
    "given_rule_type, expected_indentation",
    [(DefaultRule, " " * 8), (Rule, " " * 12)],
    ids=["DefaultRule", "Rule"],
)
def test_gf_write_step_with_doc_string_keep_indentation_without_data_table(
    given_rule_type, expected_indentation, disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter properly formats a Step with a doc string
    that has an indentation itself
    but without a data table
    """
    # given
    step = mocker.MagicMock(spec=Step)
    step.keyword = "Given"
    step.used_keyword = "Given"
    step.text = "there is a Step"
    step.doc_string = """foo
    bar
  meh
bla
"""
    step.data_table = None
    step.rule = mocker.MagicMock(spec=given_rule_type)

    # when
    write_step(step, step_color_func=lambda x: x)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>{indentation})Given there is a Step
            (?P<indentation>{indentation}    )\"\"\"
            (?P<indentation>{indentation}    )foo
            (?P<indentation>{indentation}    )    bar
            (?P<indentation>{indentation}    )  meh
            (?P<indentation>{indentation}    )bla
            (?P<indentation>{indentation}    )\"\"\"
            """.format(
                indentation=expected_indentation
            )
        ),
    )


@pytest.mark.parametrize(
    "step_state, expected_color",
    [
        pytest.param(State.PASSED, cf.forestGreen, id="State.PASSED => cf.forestGreen"),
        pytest.param(State.FAILED, cf.firebrick, id="State.FAILED => cf.firebrick"),
        pytest.param(State.PENDING, cf.orange, id="State.PENDING => cf.orange"),
        pytest.param(
            State.UNTESTED, cf.deepSkyBlue3, id="State.UNTESTED => cf.deepSkyBlue3"
        ),
    ],
)
def test_gf_write_step_result_without_failure_report(
    step_state, expected_color, world_default_config, disabled_colors, capsys, mocker
):
    """Test that the Gherkin Formatter properly formats a Step result without a Failure Report"""
    # given
    step = mocker.MagicMock(spec=Step)
    step.keyword = "Given"
    step.used_keyword = "Given"
    step.text = "there is a Step"
    step.state = step_state
    step.failure_report = None

    write_step_mock = mocker.patch("radish.formatters.gherkin.write_step")

    # when
    write_step_result(step)

    # then
    write_step_mock.assert_called_once_with(step, expected_color)


def test_gf_write_and_as_keyword_if_not_first_step_of_keyword_context(
    disabled_colors, capsys, mocker
):
    """
    Test that the Gherkin Formatter writes the ``And`` keyword instead of the keyword itself
    if it's not the first Step of this keyword context.
    """
    # given
    first_step = mocker.MagicMock(spec=Step)
    first_step.keyword = "Given"
    first_step.used_keyword = "Given"
    first_step.text = "there is the first Step"
    first_step.doc_string = None
    first_step.data_table = None
    first_step.rule = mocker.MagicMock(spec=DefaultRule)

    second_step = mocker.MagicMock(spec=Step)
    second_step.keyword = "Given"
    second_step.used_keyword = "And"
    second_step.text = "there is the second Step"
    second_step.doc_string = None
    second_step.data_table = None
    second_step.rule = mocker.MagicMock(spec=DefaultRule)

    # when
    write_step(first_step, step_color_func=lambda x: x)
    write_step(second_step, step_color_func=lambda x: x)

    # then
    assert_output(
        capsys,
        dedent_feature_file(
            """
            (?P<indentation>        )Given there is the first Step
            (?P<indentation>        )And there is the second Step
            """
        ),
    )
