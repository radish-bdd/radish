# -*- coding: utf-8 -*-

"""
This module provides functionaliy to test
if some sentences are matched with the expected
step implementations.
"""

import sys
import codecs

import yaml
import colorful

from radish.loader import load_modules
from radish.matcher import match_step
from radish.stepregistry import StepRegistry
from radish.utils import get_func_arg_names, get_func_location, locate


def test_step_matches_configs(
    match_config_files, basedirs, cover_min_percentage=None, cover_show_missing=False
):
    """
    Test if the given match config files matches the actual
    matched step implementations.
    """
    if cover_min_percentage is not None and float(cover_min_percentage) > 100:
        sys.stderr.write(
            str(
                colorful.magenta(
                    "You are a little cocky to think you can reach a minimum coverage of {0:.2f}%\n".format(
                        float(cover_min_percentage)
                    )
                )
            )
        )
        return 3

    # load user's custom python files
    for basedir in basedirs:
        load_modules(basedir)

    steps = StepRegistry().steps

    if not steps:
        sys.stderr.write(
            str(
                colorful.magenta(
                    "No step implementations found in {0}, thus doesn't make sense to continue".format(
                        basedirs
                    )
                )
            )
        )
        return 4

    failed = 0
    passed = 0
    covered_steps = set()

    for match_config_file in match_config_files:
        # load the given match config file
        with codecs.open(match_config_file, "r", "utf-8") as f:
            match_config = yaml.safe_load(f)

        if not match_config:
            print(
                colorful.magenta(
                    "No sentences found in {0} to test against".format(
                        match_config_file
                    )
                )
            )
            return 5

        print(
            colorful.yellow(
                "Testing sentences from {0}:".format(
                    colorful.bold_yellow(match_config_file)
                )
            )
        )
        failed_sentences, passed_senteces = test_step_matches(match_config, steps)
        failed += failed_sentences
        passed += passed_senteces

        covered_steps = covered_steps.union(
            x["should_match"] for x in match_config if "should_match" in x
        )

        # newline
        sys.stdout.write("\n")

    report = colorful.bold_white("{0} sentences (".format(failed + passed))
    if passed > 0:
        report += colorful.bold_green("{0} passed".format(passed))

    if passed > 0 and failed > 0:
        report += colorful.bold_white(", ")

    if failed > 0:
        report += colorful.bold_red("{0} failed".format(failed))
    report += colorful.bold_white(")")
    print(report)

    step_coverage = 100.0 / len(steps) * len(covered_steps)
    coverage_report = colorful.bold_white(
        "Covered {0} of {1} step implementations".format(len(covered_steps), len(steps))
    )

    ret = 0 if failed == 0 else 1

    if cover_min_percentage:
        coverage_color = (
            colorful.bold_green
            if step_coverage >= float(cover_min_percentage)
            else colorful.bold_red
        )
        coverage_report += colorful.bold_white(" (coverage: ")
        coverage_report += coverage_color("{0:.2f}%".format(step_coverage))
        if float(cover_min_percentage) > step_coverage:
            coverage_report += colorful.bold_white(
                ", expected a minimum of {0}".format(
                    colorful.bold_green(cover_min_percentage + "%")
                )
            )
            if failed == 0:
                ret = 2
            # if tests have passed and coverage is too low we fail with exit code 2
        coverage_report += colorful.bold_white(")")

    print(coverage_report)

    if cover_show_missing:
        missing_steps = get_missing_steps(steps, covered_steps)
        if missing_steps:
            missing_step_report = colorful.bold_yellow("Missing steps:\n")
            for step in missing_steps:
                missing_step_report += "- {0} at ".format(colorful.cyan(step[0]))
                missing_step_report += colorful.cyan(step[1]) + "\n"
            sys.stdout.write(str(missing_step_report))

    return ret


def test_step_matches(match_config, steps):
    """
    Test if the given match config matches the actual
    matched step implementations.
    """
    failed = 0
    passed = 0

    for item in match_config:
        validate_config_item(item)

        sentence = item["sentence"]

        if "should_match" in item:
            has_passed = test_step_match(
                sentence, item["should_match"], item.get("with_arguments", None), steps
            )
        else:
            has_passed = test_step_not_match(sentence, item["should_not_match"], steps)

        if has_passed:
            passed += 1
        else:
            failed += 1

    return failed, passed


def test_step_match(sentence, expected_step, expected_arguments, steps):
    sys.stdout.write(
        '{0} STEP "{1}" SHOULD MATCH {2}    '.format(
            colorful.yellow(">>"), colorful.cyan(sentence), colorful.cyan(expected_step)
        )
    )

    result = match_step(sentence, steps)
    if not result:
        output_failure(None, ["Expected sentence didn't match any step implementation"])
        return False

    if expected_step != result.func.__name__:
        output_failure(
            result.func,
            [
                "Expected sentence matched {0} instead of {1}".format(
                    result.func.__name__, expected_step
                )
            ],
        )
        return False

    if expected_arguments:
        arguments = merge_step_args(result)
        expected_arguments = {
            k: v
            for expected_arguments in expected_arguments
            for k, v in expected_arguments.items()
        }
        argument_errors = check_step_arguments(expected_arguments, arguments)
        if argument_errors:
            output_failure(result.func, argument_errors)
            return False

    print(str(colorful.bold_green("✔")))
    return True


def test_step_not_match(sentence, expected_not_matching_step, steps):
    step_to_print = (
        colorful.cyan(expected_not_matching_step)
        if expected_not_matching_step
        else "ANY"
    )
    sys.stdout.write(
        '{0} STEP "{1}" SHOULD NOT MATCH {2}    '.format(
            colorful.yellow(">>"), colorful.cyan(sentence), step_to_print
        )
    )

    result = match_step(sentence, steps)
    if result:
        if (
            not expected_not_matching_step
            or result.func.__name__ == expected_not_matching_step
        ):
            output_failure(
                None,
                [
                    "Expected sentence did match {0} but it shouldn't".format(
                        expected_not_matching_step
                    )
                ],
            )
            return False

    print(str(colorful.bold_green("✔")))
    return True


VALID_CONFIG_ITEMS = {"sentence", "should_match", "should_not_match", "with_arguments"}


def validate_config_item(config):
    """
    Validate the given config object
    """
    given_attributes = set(config.keys())
    if not given_attributes.issubset(VALID_CONFIG_ITEMS):
        raise ValueError(
            "The config attributes {0} are invalid. Use only {1}".format(
                ", ".join(sorted(given_attributes.difference(VALID_CONFIG_ITEMS))),
                ", ".join(sorted(VALID_CONFIG_ITEMS)),
            )
        )

    if "sentence" not in config or (
        "should_match" not in config and "should_not_match" not in config
    ):
        raise ValueError(
            "You have to provide a sentence and the function name which should (not) be matched (should_match, should_not_match)"
        )


def output_failure(step_func, errors):
    """
    Write the given errors to stdout.
    """
    sys.stdout.write(str(colorful.bold_red("✘")))
    if step_func is not None:
        sys.stdout.write(
            str(colorful.red(" (at {0})".format(get_func_location(step_func))))
        )

    sys.stdout.write("\n")

    for error in errors:
        print(str(colorful.red("  - {0}".format(error))))


def check_step_arguments(expected_arguments, arguments):
    """
    Check if the given expected arguments
    match the actual arguments
    """
    errors = []
    for arg_name, arg_value in expected_arguments.items():
        if arg_name not in arguments:
            errors.append(
                'Expected argument "{0}" is not in matched arguments {1}'.format(
                    arg_name, list(arguments.keys())
                )
            )
            continue

        use_repr = False

        # check if argument value is a dict, if yes we'll do thorough comparison
        if isinstance(arg_value, dict) and "type" not in arg_value.keys():
            _type = "dict"
            value = arg_value
        elif isinstance(arg_value, dict):
            _type = arg_value["type"]
            value = arg_value["value"]
            # Use repr protocol to match argument values
            use_repr = "use_repr" in arg_value and arg_value["use_repr"]

            # check if value should be casted to the given type
            if "cast" in arg_value and arg_value["cast"] is True:
                obj_type = locate(_type)
                if obj_type is None:
                    errors.append(
                        'Cannot cast to type "{0}" because it is unknown'.format(_type)
                    )
                    continue

                try:
                    value = obj_type(value)
                except Exception as exc:
                    errors.append(
                        'Failed to cast "{0}" to given type "{1}"'.format(value, type)
                    )
                    continue
        else:
            _type = type(arg_value).__name__
            value = arg_value

        if not use_repr and _type != type(value).__name__:
            errors.append(
                'Conflicting argument configuration: given value is actually of type "{0}" although it should match a value of type "{1}"'.format(
                    type(value).__name__, _type
                )
            )
            continue

        if type(arguments[arg_name]).__name__ != _type:
            errors.append(
                'Expected argument "{0}" is of type "{1}" instead "{2}"'.format(
                    arg_name, type(arguments[arg_name]).__name__, _type
                )
            )
            continue

        matched = None
        if use_repr:
            matched = repr(arguments[arg_name]) != value
        else:
            matched = arguments[arg_name] != value

        if matched:
            errors.append(
                'Expected argument "{0}" with value "{1}" does not match value "{2}"'.format(
                    arg_name, value, arguments[arg_name]
                )
            )
    return errors


def merge_step_args(step_func):
    """
    Merges the arguments and keyword arguments
    of the given step function.
    """
    #: Holds the merged arguments as a dict with the corresponding matched values
    args, kwargs = step_func.argument_match.evaluate()
    step_arg_names = get_func_arg_names(step_func.func)[1:]
    arguments = dict(zip(step_arg_names, args))
    arguments.update(kwargs)
    return arguments


def get_missing_steps(steps, covered_steps):
    """
    Get all steps within ``steps`` which are not
    covered by ``covered_steps``.
    """
    missing_steps = []
    for step_func in steps.values():
        if step_func.__name__ not in covered_steps:
            missing_steps.append((step_func.__name__, get_func_location(step_func)))
    return missing_steps
