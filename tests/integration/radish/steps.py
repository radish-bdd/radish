"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import os
import re
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

from lxml import etree

from radish import after, before, given, then, when


@before.each_scenario()
def create_temporary_directory_for_radish_run(scenario):
    """Create the temporary directory for the radish run"""
    scenario.context.ctx_dir = tempfile.mkdtemp(prefix="radish-")
    scenario.context.features_dir = os.path.join(scenario.context.ctx_dir, "features")
    scenario.context.matching_config_dir = os.path.join(
        scenario.context.ctx_dir, "matcher-configs"
    )
    scenario.context.base_dir = os.path.join(scenario.context.ctx_dir, "radish")
    scenario.context.results_dir = os.path.join(scenario.context.ctx_dir, "results")
    scenario.context.failure_report_path = os.path.join(
        scenario.context.results_dir, "failure_report"
    )

    # setup failure gather hooks
    failure_gather_hooks = """
from radish import after
from radish.models.state import State

@after.each_step()
def gather_failure(step):
    if step.state is not State.FAILED:
        return

    with open(r"{}", "w+", encoding="utf-8") as failure_report_file:
        failure_report_file.write("{{}}\\n".format(step.failure_report.name))
        failure_report_file.write("{{}}\\n".format(step.failure_report.reason))
    """.format(
        scenario.context.failure_report_path
    )

    os.makedirs(scenario.context.features_dir)
    os.makedirs(scenario.context.matching_config_dir)
    os.makedirs(scenario.context.base_dir)
    os.makedirs(scenario.context.results_dir)

    with open(
        os.path.join(scenario.context.base_dir, "failure_report_hook.py"),
        "w+",
        encoding="utf-8",
    ) as failure_report_hook_file:
        failure_report_hook_file.write(textwrap.dedent(failure_gather_hooks))


@after.each_scenario()
def remove_temporary_directory_for_radish_run(scenario):
    """Remove the temporary directory for the radish run"""
    shutil.rmtree(scenario.context.ctx_dir)


@given("the Feature File {feature_filename:QuotedString}")
def create_feature_file(step, feature_filename):
    """Create the Feature File given in the doc string"""
    assert (
        step.doc_string is not None
    ), "Please provide a Feature in the Step doc string"

    feature_contents = step.doc_string

    feature_path = os.path.join(step.context.features_dir, feature_filename)
    with open(feature_path, "w+", encoding="utf-8") as feature_file:
        feature_file.write(feature_contents)


@given("the base dir module {module_filename:QuotedString}")
def create_base_dir_module(step, module_filename):
    """Create the base dir module given in the doc string"""
    assert (
        step.doc_string is not None
    ), "Please provide a Python Module in the Step doc string"

    module_contents = step.doc_string
    module_path = os.path.join(step.context.base_dir, module_filename)
    with open(module_path, "w+", encoding="utf-8") as module_file:
        module_file.write(module_contents)


@given("the Matcher Config File {matching_config_filename:QuotedString}")
def create_matcher_config_file(step, matching_config_filename):
    """Create the Matcher Config File given in the doc string"""
    assert (
        step.doc_string is not None
    ), "Please provide a Matcher Config in the Step doc string"

    matcher_config_contents = step.doc_string

    matching_config_path = os.path.join(
        step.context.matching_config_dir, matching_config_filename
    )
    with open(matching_config_path, "w+", encoding="utf-8") as matching_config_file:
        matching_config_file.write(matcher_config_contents)


@when("the {feature_filename:QuotedString} is run")
def run_feature_file(step, feature_filename):
    """Run the given Feature File"""
    feature_path = os.path.join(step.context.features_dir, feature_filename)
    radish_command = [
        "coverage",
        "run",
        "-p",
        "-m",
        "radish",
        "-b",
        step.context.base_dir,
        feature_path,
        "-t",
    ]
    proc = subprocess.Popen(
        radish_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate()

    step.context.exit_code = proc.returncode
    step.context.stdout = stdout
    step.context.command = radish_command


@when(
    "the {feature_filename:QuotedString} is run with the options {radish_options:QuotedString}"
)
def run_feature_file_with_options(step, feature_filename, radish_options):
    """Run the given Feature File"""
    feature_path = os.path.join(step.context.features_dir, feature_filename)

    # replace ctx_dir in radish_options
    radish_options = radish_options.format(ctx_dir=step.context.ctx_dir)

    radish_command = [
        "coverage",
        "run",
        "-p",
        "-m",
        "radish",
        "-b",
        step.context.base_dir,
        feature_path,
        "-t",
    ] + radish_options.split()
    proc = subprocess.Popen(
        radish_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate()

    step.context.exit_code = proc.returncode
    step.context.stdout = stdout
    step.context.command = radish_command


@then("the exit code should be {exit_code:int}")
def expect_exit_code(step, exit_code):
    """Expect the exit code to be a certain integer"""
    assert step.context.exit_code == exit_code, (
        "Actual exit code was: {}\n".format(step.context.exit_code)
        + "stdout from radish run: '{}':\n".format(" ".join(step.context.command))
        + step.context.stdout.decode("utf-8")
    )


def assert_output(actual_stdout, expected_stdout):
    """Assert that the captured stdout matches"""
    for actual_stdout_line, expected_stdout_line in zip(
        actual_stdout.splitlines(), expected_stdout.splitlines()
    ):
        assert re.match(
            "^" + expected_stdout_line + "$", actual_stdout_line
        ), "{!r} == {!r}".format(expected_stdout_line, actual_stdout_line)


@then("the output to match:")
def expect_output(step):
    """Expect the output to match the regex in the doc string"""
    assert (
        step.doc_string is not None
    ), "Please provide an output in the Step doc string"

    actual_stdout = step.context.stdout.decode("utf-8").replace("\r", "")
    # print(actual_stdout)
    assert_output(actual_stdout, step.doc_string.replace("\r", ""))


@then("the run should fail with a {exc_type_name:word}")
def expect_fail_with_exc(step, exc_type_name):
    """Expect the run failed with an exception of the given type and message from doc string"""
    assert step.context.exit_code != 0, +"stdout from radish run: '{}':\n".format(
        " ".join(step.context.command)
    ) + step.context.stdout.decode("utf-8")

    assert os.path.exists(step.context.failure_report_path), (
        "No Step Failure Report was written\n"
        + "stdout from radish run: '{}':\n".format(
            " ".join(step.context.command)
        )  # noqa
        + step.context.stdout.decode("utf-8")
    )

    with open(
        step.context.failure_report_path, encoding="utf-8"
    ) as failure_report_file:
        actual_exc_type_name = failure_report_file.readline().strip()
        actual_exc_reason = failure_report_file.readline().strip()

    assert (
        actual_exc_type_name == exc_type_name
    ), "Exception types don't match '{}' == '{}'".format(
        actual_exc_type_name, exc_type_name
    )

    if step.doc_string is not None:
        assert step.doc_string.strip() in actual_exc_reason, "Reasons don't match"


@then("the run should fail with")
def expect_fail(step):
    """Expect the run failed with an exception"""
    stdout = step.context.stdout.decode("utf-8").replace("\r", "")

    assert step.context.exit_code != 0, (
        "Actual exit code was: {}\n".format(step.context.exit_code)
        + "stdout from radish run: '{}':\n".format(" ".join(step.context.command))
        + stdout
    )

    match = step.doc_string in stdout
    assert match, (
        "Searched for:\n" + step.doc_string + "\n" + "within stdout:\n" + stdout
    )


@then("the XML file {xmlfile:word} validates against {xsdfile:word}")
def expect_xml_validates(step, xmlfile, xsdfile):
    """Expect that the given XML file validates against the given XSD file"""
    xmlfile_path = os.path.join(step.context.ctx_dir, xmlfile)
    xsdfile_path = Path(__file__).absolute().parent.parent / "assets" / xsdfile

    xmltree = etree.parse(xmlfile_path)
    xsdtree = etree.parse(str(xsdfile_path))
    xsd = etree.XMLSchema(xsdtree)

    xsd.assert_(xmltree)


@then(
    "the XML file {xmlfile:word} has the value "
    "{expected_value:QuotedString} at {xpath:QuotedString}"
)
def expect_value_at_xpath(step, xmlfile, expected_value, xpath):
    """Expect the given value at the given xpath in the given xml file"""
    xmlfile_path = os.path.join(step.context.ctx_dir, xmlfile)
    tree = etree.parse(xmlfile_path)

    elements = tree.xpath(xpath)

    assert len(elements) != 0, "Cannot find any elements at '{}'".format(xpath)

    assert (
        len(elements) == 1
    ), "Found multiple elements at '{}'. Expected exactly one.".format(xpath)

    actual_value = elements[0]

    assert (
        actual_value == expected_value
    ), "Actual value '{}' didn't match expected value '{}'".format(
        actual_value, expected_value
    )


@then("the XML file {xmlfile:word} has the content:")
def expect_xml_content(step, xmlfile):
    """Expect the XML file content to match the given Doc String"""
    assert (
        step.doc_string is not None
    ), "Please provide the content in the Step doc string"

    xmlfile_path = os.path.join(step.context.ctx_dir, xmlfile)

    with open(xmlfile_path, encoding="utf-8") as f:
        actual_content = f.read().replace("\r", "")

    assert_output(actual_content, step.doc_string.replace("\r", ""))


@when("the {matching_config_filename:QuotedString} is tested")
def run_matching_config(step, matching_config_filename):
    """Run the given Feature File"""
    run_matching_config_with_options(step, matching_config_filename, "")


@when(
    "the {matching_config_filename:QuotedString} "
    "is tested with the options {radish_options:QuotedString}"
)
def run_matching_config_with_options(step, matching_config_filename, radish_options):
    """Run the given Feature File"""
    matching_config_path = os.path.join(
        step.context.matching_config_dir, matching_config_filename
    )
    radish_command = [
        "coverage",
        "run",
        "-p",
        "-m",
        "radish.step_testing",
        "-b",
        step.context.base_dir,
        matching_config_path,
    ] + radish_options.split()
    proc = subprocess.Popen(
        radish_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate()

    step.context.exit_code = proc.returncode
    step.context.stdout = stdout
    step.context.command = radish_command


@when("the {feature_filename:QuotedString} is parsed")
def run_parser(step, feature_filename):
    """Run the given Feature File"""
    feature_path = os.path.join(step.context.features_dir, feature_filename)
    radish_command = ["coverage", "run", "-p", "-m", "radish.parser", feature_path]
    proc = subprocess.Popen(
        radish_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate()

    step.context.exit_code = proc.returncode
    step.context.stdout = stdout
    step.context.command = radish_command
