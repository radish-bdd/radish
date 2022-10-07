# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import os
import io
import sys
import tempfile

import pytest

from radish.main import main


@pytest.mark.parametrize(
    "given_featurefiles, given_cli_args, expected_exitcode, expected_output",
    [
        (["empty"], [], 1, "empty"),
        (["empty-feature"], [], 1, "empty-feature"),
        (["feature-only-description"], [], 1, "feature-only-description"),
        (["feature-scenario-steps"], [], 0, "feature-scenario-steps"),
        (["feature-scenarios"], [], 0, "feature-scenarios"),
        (["comments"], [], 0, "comments"),
        (["german"], [], 0, "german"),
        (["unicode"], [], 0, "unicode"),
        (["multi-features"], [], 1, "multi-features"),
        (["empty-scenario"], [], 0, "empty-scenario"),
        (["scenario-outline"], [], 0, "scenario-outline"),
        (["regular-scenario-examples"], [], 1, "regular-scenario-examples"),
        (["scenario-loop"], [], 0, "scenario-loop"),
        (["step-tabular-data"], [], 0, "step-tabular-data"),
        (["step-tabular-data-invalid"], [], 1, "step-tabular-data-invalid"),
        (["step-text-data"], [], 0, "step-text-data"),
        (["tags-feature"], [], 0, "tags-feature"),
        (["tags-feature"], ["--tags", "foo"], 0, "tags-feature"),
        (["tags-feature"], ["--tags", "foo or bar"], 0, "tags-feature"),
        (["tags-feature"], ["--tags", "foo and bar"], 0, "tags-feature"),
        (["tags-scenario"], [], 0, "tags-scenario"),
        (["tags-scenario"], ["--tags", "foo"], 0, "tags-scenario"),
        (["tags-scenario"], ["--tags", "foo or bar"], 0, "tags-scenario"),
        (["tags-scenario"], ["--tags", "foo and bar"], 0, "tags-scenario"),
        (["tags-everywhere"], [], 0, "tags-everywhere"),
        (
            ["tags-everywhere"],
            ["--tags", "regular_scenario"],
            0,
            "tags-everywhere-regular-scenario-only",
        ),
        (
            ["tags-everywhere"],
            ["--tags", "scenario_outline"],
            0,
            "tags-everywhere-scenario-outline-only",
        ),
        (
            ["tags-everywhere"],
            ["--tags", "scenario_loop"],
            0,
            "tags-everywhere-scenario-loop-only",
        ),
        (
            ["tags-everywhere"],
            ["--tags", "scenario_loop or scenario_outline"],
            0,
            "tags-everywhere-scenario-loop-and-outline",
        ),
        (["tags-arguments"], [], 0, "tags-arguments"),
        (["tags-ignored-scenario"], [], 0, "tags-ignored-scenario"),
        (
            ["tags-ignored-scenario"],
            ["--tags", "foo"],
            0,
            "tags-ignored-scenario-foo-only",
        ),
        (
            ["tags-ignored-scenario"],
            ["--tags", "bar"],
            0,
            "tags-ignored-scenario-bar-only",
        ),
        (
            ["tags-ignored-scenario"],
            ["--tags", "bar or foo"],
            0,
            "tags-ignored-scenario-bar-or-foo",
        ),
        (
            ["tags-ignored-scenario"],
            ["--tags", "not bar and not foo"],
            0,
            "tags-ignored-scenario-not-bar-not-foo",
        ),
        (["background"], [], 0, "background"),
        (["background-scenariooutline"], [], 0, "background-scenariooutline"),
        (["background-scenarioloop"], [], 0, "background-scenarioloop"),
        (["background-subsequent-tag"], [], 0, "background-subsequent-tag"),
        (["background-misplaced"], [], 1, "background-misplaced"),
        (["background-multiple"], [], 1, "background-multiple"),
        (["constants"], [], 0, "constants"),
        (["scenario-sentence-duplicate"], [], 1, "scenario-sentence-duplicate"),
        (["precondition-level-0"], [], 0, "precondition-level-0"),
        (["precondition-level-1"], [], 0, "precondition-level-1"),
        (["precondition-level-2"], [], 0, "precondition-level-2"),
        (["precondition-same-feature"], [], 0, "precondition-same-feature"),
        (
            ["precondition-unknown-scenario-same-feature"],
            [],
            1,
            "precondition-unknown-scenario-same-feature",
        ),
        (["precondition-malformed"], [], 1, "precondition-malformed"),
        (["failing-scenario"], [], 1, "failing-scenario"),
        (["failing-scenario-middle"], [], 1, "failing-scenario-middle"),
        (["failing-scenario-outline"], [], 1, "failing-scenario-outline"),
        (["failing-scenario-outline-middle"], [], 1, "failing-scenario-outline-middle"),
        (
            ["failing-scenario-outline-middle"],
            ["--early-exit"],
            1,
            "failing-scenario-outline-middle-exit-early",
        ),
        (["failing-scenario-loop"], [], 1, "failing-scenario-loop"),
        (
            ["failing-scenario-loop"],
            ["--early-exit"],
            1,
            "failing-scenario-loop-exit-early",
        ),
        (
            ["feature-scenario-steps"],
            ["--write-ids"],
            0,
            "feature-scenario-steps-with-ids",
        ),
        (["scenario-outline"], ["--write-ids"], 0, "scenario-outline-with-ids"),
        (["scenario-loop"], ["--write-ids"], 0, "scenario-loop-with-ids"),
        (["background"], ["--write-ids"], 0, "background-with-ids"),
        (
            ["feature-scenario-steps"],
            ["--no-ansi"],
            0,
            "feature-scenario-steps-no-ansi",
        ),
        (
            ["feature-scenario-steps"],
            ["--no-ansi", "--write-steps-once"],
            0,
            "feature-scenario-steps-no-ansi-write-once",
        ),
        (["scenario-outline"], ["--no-ansi"], 0, "scenario-outline-no-ansi"),
        (
            ["scenario-outline"],
            ["--no-ansi", "--write-steps-once"],
            0,
            "scenario-outline-no-ansi-write-once",
        ),
        (["scenario-loop"], ["--no-ansi"], 0, "scenario-loop-no-ansi"),
        (
            ["scenario-loop"],
            ["--no-ansi", "--write-steps-once"],
            0,
            "scenario-loop-no-ansi-write-once",
        ),
        (
            ["feature-scenario-steps"],
            ["--no-line-jump"],
            0,
            "feature-scenario-steps-no-line-jump",
        ),
        (["scenario-outline"], ["--no-line-jump"], 0, "scenario-outline-no-line-jump"),
        (["scenario-loop"], ["--no-line-jump"], 0, "scenario-loop-no-line-jump"),
        (
            ["feature-scenario-steps"],
            ["--bdd-xml", tempfile.mkstemp()[1]],
            0,
            "feature-scenario-steps",
        ),
        (
            ["feature-scenario-steps"],
            ["--cucumber-json", tempfile.mkstemp()[1]],
            0,
            "feature-scenario-steps",
        ),
        (["embed"], ["--cucumber-json", tempfile.mkstemp()[1]], 0, "embed"),
        (
            ["cucumber-json"],
            ["--cucumber-json", tempfile.mkstemp()[1]],
            1,
            "cucumber-json",
        ),
        (
            ["feature-scenario-steps"],
            ["--junit-xml", tempfile.mkstemp()[1]],
            0,
            "feature-scenario-steps",
        ),
        (
            ["failing-scenario-middle"],
            ["--wip"],
            0,
            "failing-scenario-middle-success-wip",
        ),
        (["scenario-outline"], ["--wip"], 1, "scenario-outline-failed-wip"),
        (
            ["everything_with_failures"],
            ["-f", "dots"],
            1,
            "everything_with_failures_dot_formatter",
        ),
    ],
    ids=[
        "Empty Feature File",
        "Empty Featre",
        "Feature with description only",
        "Feature with one Scenario and Steps",
        "Feature with multiple Scenarios",
        "Comments in Feature",
        "German Keywords",
        "Unicode Characters in Feature File",
        "Multiple Features in single Feature File",
        "Empty Scenario",
        "Scenario Outline",
        "Regular Scenario with Scenario Outline Examples",
        "Scenario Loop",
        "Step with Tabular data",
        "Step Tabular data without previous Step",
        "Step with Text data",
        "Feature with Tags",
        "Feature with Tags filtered by Foo",
        "Feature with Tags filtered by Foo or Bar",
        "Feature with Tags filtered by Foo and Bar",
        "Scenario with Tags",
        "Scenario with Tags filtered by Foo",
        "Scenario with Tags filtered by Foo or Bar",
        "Scenario with Tags filtered by Foo and Bar",
        "Feature and Scenario, Scenario Outline and Loop with Tags",
        "Feature and Scenario, Scenario Outline and Loop with Tags filtered by regular_scenario",
        "Feature and Scenario, Scenario Outline and Loop with Tags filtered by scenario_outline",
        "Feature and Scenario, Scenario Outline and Loop with Tags filtered by scenario_loop",
        "Feature and Scenario, Scenario Outline and Loop with Tags filtered by scenario_loop or scenario_outline",
        "Tag Arguments for Feature and Scenario Tags",
        "Feature and Scenario with Tags to ignore",
        "Only show Scenarios tagged with foo",
        "Only show Scenarios tagged with bar",
        "Only show Scenarios tagged with foo or bar",
        "Only show Scenarios tagged not with foo and bar",
        "Background",
        "Background for Scenario Outline",
        "Background for Scenario Loop",
        "Background with subsequent Tag",
        "Background which is misplaced",
        "Multiple Background in one Feature",
        "Feature and Scenario Constants",
        "Scenario Sentence Duplicate",
        "Precondition Level 0",
        "Precondition Level 1",
        "Precondition Level 2",
        "Precondition from same Feature",
        "Precondition with unknown Scenario from same Feature",
        "Precondition which is malformed",
        "Failing Scenario",
        "Failing Scenario in the middle",
        "Failing Scenario Outline",
        "Failing Scenario Outline in the middle",
        "Failing Scenario Outline in the middle with early exit",
        "Failing Scenario Loop",
        "Failing Scenario Loop with early exit",
        "Feature with single Scenario and Steps with Ids",
        "Scenario Outline with Ids",
        "Scenario Loop with Ids",
        "Background with Ids",
        "Feature with single Scenario and Steps with no ANSI",
        "Feature with single Scenario and Steps with no ANSI and Steps once",
        "Scenario Outline with no ANSI",
        "Scenario Outline with no ANSI and Steps once",
        "Scenario Loop with no ANSI",
        "Scenario Loop with no ANSI and Steps once",
        "Feature with single Scenario and Steps with no line jump",
        "Scenario Outline with no line jump",
        "Scenario Loop with no line jump",
        "Feature with single Scenario and Steps producing BDD XML",
        "Feature with single Scenario and Steps producing Cucumber JSON",
        "Feature with single Scenario and Steps with embedded data producing Cucumber JSON",
        "Feature with scenario failure producing Cucumber JSON",
        "Feature with single Scenario and Steps producing JUnit XML",
        "Feature which fails with wip tag",
        "Feature which does not fail with wip tag",
        "Feature which has everything in it and some Scenario fail",
    ],
)
def test_main_cli_calls(
    given_featurefiles,
    given_cli_args,
    expected_exitcode,
    expected_output,
    featurefiledir,
    radishdir,
    outputdir,
):
    """
    Test calling main CLI
    """
    # given
    if "-m" not in given_cli_args and "--marker" not in given_cli_args:
        given_cli_args.extend(["--marker", "test-marker"])

    if "-b" not in given_cli_args and "--basedir" not in given_cli_args:
        given_cli_args.extend(["-b", radishdir])
    else:
        # fixup basedir paths
        base_dir_idx = [
            i for i, x in enumerate(given_cli_args) if x in ("-b", "--basedir")
        ]
        for idx in base_dir_idx:
            given_cli_args[idx + 1] = os.path.join(radishdir, given_cli_args[idx + 1])

    featurefiles = [
        os.path.join(featurefiledir, x + ".feature") for x in given_featurefiles
    ]
    cli_args = featurefiles + given_cli_args

    expected_output_file = os.path.join(outputdir, "unix", expected_output + ".txt")
    if os.name == 'nt':
        expected_output_file_win = os.path.join(outputdir, "windows", expected_output + ".txt")
        if os.path.exists(expected_output_file_win):
            expected_output_file = expected_output_file_win


    with io.open(expected_output_file, "r", encoding="utf-8") as output_file:
        expected_output_string = output_file.read()

    # when
    original_stdout = sys.stdout

    with tempfile.TemporaryFile() as tmp:
        tmp_stdout = io.open(tmp.fileno(), mode='w+', encoding='utf-8', closefd=False)
        # patch sys.stdout
        sys.stdout = tmp_stdout

        try:
            actual_exitcode = main(args=cli_args)
        except SystemExit as exc:
            actual_exitcode = exc.code
        finally:
            tmp_stdout.seek(0)
            actual_output = tmp_stdout.read()
            # restore stdout
            sys.stdout = original_stdout

    # patch featurefile paths in actual output
    feature_parent_dir = os.path.abspath(os.path.join(featurefiledir, ".."))
    for featurefile in featurefiles:
        rel_featurefile = os.path.relpath(featurefile, feature_parent_dir)
        actual_output = actual_output.replace(featurefile, rel_featurefile)
    # then
    assert actual_output == expected_output_string
    assert actual_exitcode == expected_exitcode
