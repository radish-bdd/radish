# -*- coding: utf-8 -*-

"""
This module provides functionaliy to test
if some sentences are matched with the expected
step implementations.
"""

import sys
import codecs

import yaml
from colorful import colorful

from radish.loader import load_modules
from radish.matcher import match_step
from radish.stepregistry import StepRegistry
from radish.utils import get_func_arg_names


def test_step_matches_configs(match_config_files, basedir, cover_min_percentage=None):
    """
    Test if the given match config files matches the actual
    matched step implementations.
    """
    # load user's custom python files
    load_modules(basedir)
    steps = StepRegistry().steps

    failed = 0
    passed = 0
    covered_steps = set()

    for match_config_file in match_config_files:
        # load the given match config file
        with codecs.open(match_config_file, "r", "utf-8") as f:
            match_config = yaml.safe_load(f)

        print(colorful.brown('Testing sentences from {0}:'.format(colorful.bold_brown(match_config_file))))
        failed_sentences, passed_senteces = test_step_matches(match_config, steps)
        failed += failed_sentences
        passed += passed_senteces

        covered_steps = covered_steps.union(x['should_match'] for x in match_config)

        # newline
        sys.stdout.write('\n')

    report = colorful.bold_white('{0} sentences ('.format(failed + passed))
    if passed > 0:
        report += colorful.bold_green('{0} passed'.format(passed))

    if passed > 0 and failed > 0:
        report += colorful.bold_white(', ')

    if failed > 0:
        report += colorful.bold_red('{0} failed'.format(failed))
    report += colorful.bold_white(')')
    print(report)

    step_coverage = 100.0 / len(steps) * len(covered_steps)
    coverage_report = colorful.bold_white('Covered {0} of {1} step implementations'.format(
        len(covered_steps), len(steps)))

    ret = 0 if failed == 0 else 1

    if cover_min_percentage:
        coverage_color = colorful.bold_green if step_coverage >= float(cover_min_percentage) else colorful.bold_red
        coverage_report += colorful.bold_white(' (coverage: ')
        coverage_report += coverage_color('{0:.2f}%'.format(step_coverage))
        if float(cover_min_percentage) > step_coverage:
            coverage_report += colorful.bold_white(', expected a minimum of {0}'.format(
                colorful.bold_green(cover_min_percentage + '%')))
            if failed == 0:
                ret = 2
            # if tests have passed and coverage is too low we fail with exit code 2
        coverage_report += colorful.bold_white(')')
    print(coverage_report)

    return ret


def test_step_matches(match_config, steps):
    """
    Test if the given match config matches the actual
    matched step implementations.
    """
    failed = 0
    passed = 0

    for item in match_config:
        if 'sentence' not in item or 'should_match' not in item:
            raise ValueError('You have provide a sentence and the function name which should be matched (should_match)')

        sentence = item['sentence']
        expected_step = item['should_match']

        sys.stdout.write('{0} STEP "{1}" SHOULD MATCH {2}    '.format(
            colorful.brown('>>'), colorful.cyan(sentence), colorful.cyan(expected_step)))

        result = match_step(item['sentence'], steps)
        if not result:
            output_failure(['Expected sentence didn\'t match any step implemention'])
            failed += 1
            continue

        if expected_step != result.func.__name__:
            output_failure(['Expected sentence matched {0} instead of {1}'.format(result.func.__name__, expected_step)])
            failed += 1
            continue


        expected_arguments = item.get('with-arguments')

        if expected_arguments:
            arguments = merge_step_args(result)
            expected_arguments = {k: v for expected_arguments in expected_arguments for k, v in expected_arguments.items()}
            argument_errors = check_step_arguments(expected_arguments, arguments)
            if argument_errors:
                output_failure(argument_errors)
                failed += 1
                continue

        # check if arguments match
        print(colorful.bold_green('✔'))
        passed += 1

    return failed, passed


def output_failure(errors):
    """
    Write the given errors to stdout.
    """
    print(colorful.bold_red('✘'))
    for error in errors:
        print(colorful.red('  - {0}'.format(error)))


def check_step_arguments(expected_arguments, arguments):
    """
    Check if the given expected arguments
    match the actual arguments
    """
    errors = []
    for arg_name, arg_value in expected_arguments.items():
        if arg_name not in arguments:
            errors.append('Expected argument "{0}" is not in matched arguments {1}'.format(
                arg_name, list(arguments.keys())))
            continue

        # check if argument value is a dict, if yes we'll do thorough comparison
        if isinstance(arg_value, dict):
            _type = arg_value['type']
            value = arg_value['value']
        else:
            _type = type(arg_value).__name__
            value = arg_value

        if type(arguments[arg_name]).__name__ != _type:
            errors.append('Expected argument "{0}" is of type "{1}" instead "{2}"'.format(
                arg_name, type(arguments[arg_name]).__name__, _type))
            continue

        if arguments[arg_name] != value:
            errors.append('Expected argument "{0}" with value "{1}" does not match value "{2}"'.format(
                arg_name, arg_value, arguments[arg_name]))
    return errors


def merge_step_args(step_func):
    """
    Merges the arguments and keyword arguments
    of the given step function.
    """
    #: Holds the merged arguments as a dict with the corresponding matched values
    step_arg_names = get_func_arg_names(step_func.func)[1:]
    arguments = dict(zip(step_arg_names, step_func.args))
    arguments.update(step_func.kwargs)
    return arguments
