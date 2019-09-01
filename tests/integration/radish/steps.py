"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import os
import shutil
import tempfile
import subprocess

from radish import before, after, given, when, then


@before.each_scenario()
def create_temporary_directory_for_radish_run(scenario):
    """Create the temporary directory for the radish run"""
    scenario.context.ctx_dir = tempfile.mkdtemp(prefix="radish-")
    scenario.context.features_dir = os.path.join(scenario.context.ctx_dir, "features")
    scenario.context.base_dir = os.path.join(scenario.context.ctx_dir, "radish")

    os.makedirs(scenario.context.features_dir)
    os.makedirs(scenario.context.base_dir)


@after.each_scenario()
def remove_temporary_directory_for_radish_run(scenario):
    """Remove the temporary directory for the radish run"""
    shutil.rmtree(scenario.context.ctx_dir)


@given("the Feature File {feature_filename:QuotedString}")
def create_feature_file(step, feature_filename):
    """Create the Feature File given in the doc string"""
    assert step.doc_string is not None, "Please provide a Feature in the Step doc string"

    feature_contents = step.doc_string

    feature_path = os.path.join(step.context.features_dir, feature_filename)
    with open(feature_path, "w+", encoding="utf-8") as feature_file:
        feature_file.write(feature_contents)


@given("the base dir module {module_filename:QuotedString}")
def create_base_dir_module(step, module_filename):
    """Create the base dir module given in the doc string"""
    assert step.doc_string is not None, "Please provide a Python Module in the Step doc string"

    module_contents = step.doc_string
    module_path = os.path.join(step.context.base_dir, module_filename)
    with open(module_path, "w+", encoding="utf-8") as module_file:
        module_file.write(module_contents)


@when("the {feature_filename:QuotedString} is run")
def run_feature_file(step, feature_filename):
    """Run the given Feature File"""
    feature_path = os.path.join(step.context.features_dir, feature_filename)
    radish_command = ["radish", "-b", step.context.base_dir, feature_path]
    proc = subprocess.Popen(radish_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = proc.communicate()

    step.context.exit_code = proc.returncode
    step.context.stdout = stdout
    step.context.command = radish_command


@then("the exit code should be {exit_code:int}")
def expect_exit_code(step, exit_code):
    """Expect the exit code to be a certain integer"""
    assert step.context.exit_code == exit_code, (
        "Actual exit code was: {}\n".format(step.context.exit_code)
        + "stdout from radish run: '{}':\n".format(" ".join(step.context.command))  # noqa
        + step.context.stdout.decode("utf-8")  # noqa
    )
