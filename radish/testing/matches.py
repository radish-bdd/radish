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


def test_step_matches(match_config_file, basedir):
    """
    Test if the given match config matches the actual
    matched step implementations.
    """
    # load the given match config file
    with codecs.open(match_config_file, "r", "utf-8") as f:
        match_config = yaml.safe_load(f)

    # load user's custom python files
    load_modules(basedir)

    steps = StepRegistry().steps

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

        if arguments[arg_name] != arg_value:
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
