"""
radish
~~~~~~

Behavior Driven Development tool for Python - the root from red to green

Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import io
import os
import sys
import tempfile

import pytest

from radish.main import main


@pytest.mark.parametrize(
    "given_featurefiles, given_cli_args, expected_exitcode, expected_output",
    [
        pytest.param(["empty"], [], 1, "empty", id="Empty Feature File"),
        pytest.param(["empty-feature"], [], 1, "empty-feature", id="Empty Feature"),
        pytest.param(
            ["feature-only-description"], [], 1, "feature-only-description", id="Feature with description only"
        ),
        pytest.param(
            ["feature-scenario-steps"], [], 0, "feature-scenario-steps", id="Feature with one Scenario and Steps"
        ),
        pytest.param(["feature-scenarios"], [], 0, "feature-scenarios", id="Feature with multiple Scenarios"),
        pytest.param(["comments"], [], 0, "comments", id="Comments in Feature"),
        pytest.param(["german"], [], 0, "german", id="German Keywords"),
        pytest.param(["unicode"], [], 0, "unicode", id="Unicode Characters in Feature File"),
        pytest.param(["multi-features"], [], 1, "multi-features", id="Multiple Features in single Feature File"),
        pytest.param(["empty-scenario"], [], 0, "empty-scenario", id="Empty Scenario"),
        pytest.param(["scenario-outline"], [], 0, "scenario-outline", id="Scenario Outline"),
        pytest.param(
            ["regular-scenario-examples"],
            [],
            1,
            "regular-scenario-examples",
            id="Regular Scenario with Scenario Outline Examples",
        ),
        pytest.param(["scenario-loop"], [], 0, "scenario-loop", id="Scenario Loop"),
        pytest.param(["step-tabular-data"], [], 0, "step-tabular-data", id="Step with Tabular data"),
        pytest.param(
            ["step-tabular-data-invalid"],
            [],
            1,
            "step-tabular-data-invalid",
            id="Step Tabular data without previous Step",
        ),
        pytest.param(["step-text-data"], [], 0, "step-text-data", id="Step with Text data"),
        pytest.param(["tags-feature"], [], 0, "tags-feature", id="Feature with Tags"),
        pytest.param(["tags-feature"], ["--tags", "foo"], 0, "tags-feature", id="Feature with Tags filtered by Foo"),
        pytest.param(
            ["tags-feature"], ["--tags", "foo or bar"], 0, "tags-feature", id="Feature with Tags filtered by Foo or Bar"
        ),
        pytest.param(
            ["tags-feature"],
            ["--tags", "foo and bar"],
            0,
            "tags-feature",
            id="Feature with Tags filtered by Foo and Bar",
        ),
        pytest.param(["tags-scenario"], [], 0, "tags-scenario", id="Scenario with Tags"),
        pytest.param(["tags-scenario"], ["--tags", "foo"], 0, "tags-scenario", id="Scenario with Tags filtered by Foo"),
        pytest.param(
            ["tags-scenario"],
            ["--tags", "foo or bar"],
            0,
            "tags-scenario",
            id="Scenario with Tags filtered by Foo or Bar",
        ),
        pytest.param(
            ["tags-scenario"],
            ["--tags", "foo and bar"],
            0,
            "tags-scenario",
            id="Scenario with Tags filtered by Foo and Bar",
        ),
        pytest.param(
            ["tags-everywhere"],
            [],
            0,
            "tags-everywhere",
            id="Feature and Scenario, Scenario Outline and Loop with Tags",
        ),
        pytest.param(
            ["tags-everywhere"],
            ["--tags", "regular_scenario"],
            0,
            "tags-everywhere-regular-scenario-only",
            id="Feature and Scenario, Scenario Outline and Loop with Tags filtered by regular_scenario",
        ),
        pytest.param(
            ["tags-everywhere"],
            ["--tags", "scenario_outline"],
            0,
            "tags-everywhere-scenario-outline-only",
            id="Feature and Scenario, Scenario Outline and Loop with Tags filtered by scenario_outline",
        ),
        pytest.param(
            ["tags-everywhere"],
            ["--tags", "scenario_loop"],
            0,
            "tags-everywhere-scenario-loop-only",
            id="Feature and Scenario, Scenario Outline and Loop with Tags filtered by scenario_loop",
        ),
        pytest.param(
            ["tags-everywhere"],
            ["--tags", "scenario_loop or scenario_outline"],
            0,
            "tags-everywhere-scenario-loop-and-outline",
            id="Feature and Scenario, Scenario Outline and Loop with Tags filtered by scenario_loop or scenario_outline",
        ),
        pytest.param(["tags-arguments"], [], 0, "tags-arguments", id="Tag Arguments for Feature and Scenario Tags"),
        pytest.param(
            ["tags-ignored-scenario"], [], 0, "tags-ignored-scenario", id="Feature and Scenario with Tags to ignore"
        ),
        pytest.param(
            ["tags-ignored-scenario"],
            ["--tags", "foo"],
            0,
            "tags-ignored-scenario-foo-only",
            id="Only show Scenarios tagged with foo",
        ),
        pytest.param(
            ["tags-ignored-scenario"],
            ["--tags", "bar"],
            0,
            "tags-ignored-scenario-bar-only",
            id="Only show Scenarios tagged with bar",
        ),
        pytest.param(
            ["tags-ignored-scenario"],
            ["--tags", "bar or foo"],
            0,
            "tags-ignored-scenario-bar-or-foo",
            id="Only show Scenarios tagged with foo or bar",
        ),
        pytest.param(
            ["tags-ignored-scenario"],
            ["--tags", "not bar and not foo"],
            0,
            "tags-ignored-scenario-not-bar-not-foo",
            id="Only show Scenarios tagged not with foo and bar",
        ),
        pytest.param(["background"], [], 0, "background", id="Background"),
        pytest.param(
            ["background-scenariooutline"], [], 0, "background-scenariooutline", id="Background for Scenario Outline"
        ),
        pytest.param(["background-scenarioloop"], [], 0, "background-scenarioloop", id="Background for Scenario Loop"),
        pytest.param(
            ["background-subsequent-tag"], [], 0, "background-subsequent-tag", id="Background with subsequent Tag"
        ),
        pytest.param(["background-misplaced"], [], 1, "background-misplaced", id="Background which is misplaced"),
        pytest.param(["background-multiple"], [], 1, "background-multiple", id="Multiple Background in one Feature"),
        pytest.param(["constants"], [], 0, "constants", id="Feature and Scenario Constants"),
        pytest.param(
            ["scenario-sentence-duplicate"], [], 1, "scenario-sentence-duplicate", id="Scenario Sentence Duplicate"
        ),
        pytest.param(["precondition-level-0"], [], 0, "precondition-level-0", id="Precondition Level 0"),
        pytest.param(["precondition-level-1"], [], 0, "precondition-level-1", id="Precondition Level 1"),
        pytest.param(["precondition-level-2"], [], 0, "precondition-level-2", id="Precondition Level 2"),
        pytest.param(
            ["precondition-same-feature"], [], 0, "precondition-same-feature", id="Precondition from same Feature"
        ),
        pytest.param(
            ["precondition-unknown-scenario-same-feature"],
            [],
            1,
            "precondition-unknown-scenario-same-feature",
            id="Precondition with unknown Scenario from same Feature",
        ),
        pytest.param(["precondition-malformed"], [], 1, "precondition-malformed", id="Precondition which is malformed"),
        pytest.param(["failing-scenario"], [], 1, "failing-scenario", id="Failing Scenario"),
        pytest.param(
            ["failing-scenario-middle"], [], 1, "failing-scenario-middle", id="Failing Scenario in the middle"
        ),
        pytest.param(["failing-scenario-outline"], [], 1, "failing-scenario-outline", id="Failing Scenario Outline"),
        pytest.param(
            ["failing-scenario-outline-middle"],
            [],
            1,
            "failing-scenario-outline-middle",
            id="Failing Scenario Outline in the middle",
        ),
        pytest.param(
            ["failing-scenario-outline-middle"],
            ["--early-exit"],
            1,
            "failing-scenario-outline-middle-exit-early",
            id="Failing Scenario Outline in the middle with early exit",
        ),
        pytest.param(["failing-scenario-loop"], [], 1, "failing-scenario-loop", id="Failing Scenario Loop"),
        pytest.param(
            ["failing-scenario-loop"],
            ["--early-exit"],
            1,
            "failing-scenario-loop-exit-early",
            id="Failing Scenario Loop with early exit",
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--write-ids"],
            0,
            "feature-scenario-steps-with-ids",
            id="Feature with single Scenario and Steps with Ids",
        ),
        pytest.param(
            ["scenario-outline"], ["--write-ids"], 0, "scenario-outline-with-ids", id="Scenario Outline with Ids"
        ),
        pytest.param(["scenario-loop"], ["--write-ids"], 0, "scenario-loop-with-ids", id="Scenario Loop with Ids"),
        pytest.param(["background"], ["--write-ids"], 0, "background-with-ids", id="Background with Ids"),
        pytest.param(
            ["feature-scenario-steps"],
            ["--no-ansi"],
            0,
            "feature-scenario-steps-no-ansi",
            id="Feature with single Scenario and Steps with no ANSI",
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--no-ansi", "--write-steps-once"],
            0,
            "feature-scenario-steps-no-ansi-write-once",
            id="Feature with single Scenario and Steps with no ANSI and Steps once",
        ),
        pytest.param(
            ["scenario-outline"], ["--no-ansi"], 0, "scenario-outline-no-ansi", id="Scenario Outline with no ANSI"
        ),
        pytest.param(
            ["scenario-outline"],
            ["--no-ansi", "--write-steps-once"],
            0,
            "scenario-outline-no-ansi-write-once",
            id="Scenario Outline with no ANSI and Steps once",
        ),
        pytest.param(["scenario-loop"], ["--no-ansi"], 0, "scenario-loop-no-ansi", id="Scenario Loop with no ANSI"),
        pytest.param(
            ["scenario-loop"],
            ["--no-ansi", "--write-steps-once"],
            0,
            "scenario-loop-no-ansi-write-once",
            id="Scenario Loop with no ANSI and Steps once",
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--no-line-jump"],
            0,
            "feature-scenario-steps-no-line-jump",
            id="Feature with single Scenario and Steps with no line jump",
        ),
        pytest.param(
            ["scenario-outline"],
            ["--no-line-jump"],
            0,
            "scenario-outline-no-line-jump",
            id="Scenario Outline with no line jump",
        ),
        pytest.param(
            ["scenario-loop"], ["--no-line-jump"], 0, "scenario-loop-no-line-jump", id="Scenario Loop with no line jump"
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--bdd-xml", tempfile.mkstemp()[1]],
            0,
            "feature-scenario-steps",
            id="Feature with single Scenario and Steps producing BDD XML",
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--cucumber-json", tempfile.mkstemp()[1]],
            0,
            "feature-scenario-steps",
            id="Feature with single Scenario and Steps producing Cucumber JSON",
        ),
        pytest.param(
            ["embed"],
            ["--cucumber-json", tempfile.mkstemp()[1]],
            0,
            "embed",
            id="Feature with single Scenario and Steps with embedded data producing Cucumber JSON",
        ),
        pytest.param(
            ["cucumber-json"],
            ["--cucumber-json", tempfile.mkstemp()[1]],
            1,
            "cucumber-json",
            id="Feature with scenario failure producing Cucumber JSON",
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--junit-xml", tempfile.mkstemp()[1]],
            0,
            "feature-scenario-steps",
            id="Feature with single Scenario and Steps producing JUnit XML",
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--junit-xml", tempfile.mkstemp()[1], "--junit-relaxed"],
            0,
            "feature-scenario-steps",
            id="Feature with single Scenario and Steps producing relaxed JUnit XML",
        ),
        pytest.param(
            ["failing-scenario-middle"],
            ["--wip"],
            0,
            "failing-scenario-middle-success-wip",
            id="Feature which fails with wip tag",
        ),
        pytest.param(
            ["scenario-outline"],
            ["--wip"],
            1,
            "scenario-outline-failed-wip",
            id="Feature which does not fail with wip tag",
        ),
        pytest.param(
            ["everything_with_failures"],
            ["-f", "dots"],
            1,
            "everything_with_failures_dot_formatter",
            id="Feature which has everything in it and some Scenario fail",
        ),
        pytest.param(
            ["feature-scenario-steps"],
            ["--syslog"],
            0,
            "feature-scenario-steps-syslog",
            id="Syslog extention is supported",
        ),
        pytest.param(
            ["tags-with-arg-scenario-and-non-tagged"],
            ["--tags=sometag(somevalue)"],
            0,
            "filter-when-using-tags-with-args",
            id="Filter by tags containing variables",
        ),
        pytest.param(
            ["tags-with-arg-scenario-and-non-tagged"],
            ["--tags=sometag(somevalue) and othertag(othervalue)"],
            0,
            "filter-when-using-tags-with-args",
            id="Filter by multiple tags containing variables",
        ),
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
        base_dir_idx = [i for i, x in enumerate(given_cli_args) if x in ("-b", "--basedir")]
        for idx in base_dir_idx:
            given_cli_args[idx + 1] = os.path.join(radishdir, given_cli_args[idx + 1])

    featurefiles = [os.path.join(featurefiledir, x + ".feature") for x in given_featurefiles]
    cli_args = featurefiles + given_cli_args

    expected_output_file = os.path.join(outputdir, "unix", expected_output + ".txt")
    if os.name == "nt":
        expected_output_file_win = os.path.join(outputdir, "windows", expected_output + ".txt")
        if os.path.exists(expected_output_file_win):
            expected_output_file = expected_output_file_win

    with io.open(expected_output_file, "r", encoding="utf-8") as output_file:
        expected_output_string = output_file.read()

    # when
    original_stdout = sys.stdout

    with tempfile.TemporaryFile() as tmp:
        tmp_stdout = io.open(tmp.fileno(), mode="w+", encoding="utf-8", closefd=False)
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
